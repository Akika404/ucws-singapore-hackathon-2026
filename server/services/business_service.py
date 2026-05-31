import json
import re
import sys
from typing import List, Optional, Dict, Any

from schemas import (
    CompanyBasicInfoRequest,
    CompanyBasicInfoResponse,
    ApprovalInfoRequest,
    ApprovalInfoResponse,
    EmployeeCountRequest,
    EmployeeCountResponse,
    BusinessScopeRequest,
    BusinessScopeResponse,
    CapitalRequest,
    CapitalResponse,
    AddressRequest,
    AddressResponse,
    OrgTipsRequest,
    OrgTipsResponse,
)
from .llm_service import llm_service

# 国民经济行业分类大类（A~T），需与前端 INDUSTRIES 列表保持一致
INDUSTRY_CATEGORIES = [
    "(A) 农、林、牧、渔业", "(B) 采矿业", "(C) 制造业",
    "(D) 电力、热力、燃气及水生产和供应业", "(E) 建筑业",
    "(F) 批发和零售业", "(G) 交通运输、仓储和邮政业",
    "(H) 住宿和餐饮业", "(I) 信息传输、软件和信息技术服务业",
    "(J) 金融业", "(K) 房地产业", "(L) 租赁和商务服务业",
    "(M) 科学研究和技术服务业", "(N) 水利、环境和公共设施管理业",
    "(O) 居民服务、修理和其他服务业", "(P) 教育",
    "(Q) 卫生和社会工作", "(R) 文化、体育和娱乐业",
    "(S) 公共管理、社会保障和社会组织", "(T) 国际组织",
]

# 注册地址类型（须与第六页系统提示词中的四类取值保持一致）
ADDRESS_TYPES = [
    "商用办公地址",
    "园区/孵化器地址",
    "虚拟地址",
    "住宅地址",
]


class BusinessService:
    """业务逻辑服务 - 统一返回标准格式: {code, status, message, data}"""

    @staticmethod
    async def process_page1_generate_names(request: CompanyBasicInfoRequest) -> dict[
        str, int | str | CompanyBasicInfoResponse]:
        """
        第一页：处理公司基本信息
        - 输入：公司名称、描述信息
        - 生成公司名称建议
        """
        # 构建一组提示词：系统提示词、用户提示词、综合消息
        system_prompt = """你是一位资深的中国大陆工商注册命名顾问。
任务：根据用户的字号偏好与业务描述，生成合规且贴合业务的公司全称候选，并从给定行业大类中选出最匹配的一项。

规则：
1. 公司全称结构须符合中国大陆规范：[行政区划]（可省略）+ 字号 + 行业/经营特点 + 组织形式（如"有限公司""有限责任公司"）。
2. 每个名称都必须包含用户字号偏好中的核心字词（可在任意位置），但不要生硬堆砌；行业特点词要与业务描述匹配，避免过于通用（如仅用"科技""商务"）。
3. 生成 3-5 个互不重复、长度适中的候选。
4. recommendedBusiness 必须与给定行业大类列表中的某一项【完全一致】（含括号字母前缀），只能选一项。
5. 业务描述为空或信息不足时，仅依据字号偏好做合理推断。

只输出 JSON，键为 names、recommendedBusiness。
EXAMPLE JSON OUTPUT:
{
    "names": ["星禾云创科技有限公司", "星禾璀璨网络科技有限公司", "星禾流动信息技术有限公司"],
    "recommendedBusiness": "(I) 信息传输、软件和信息技术服务业"
}
"""
        industries_text = "\n".join(INDUSTRY_CATEGORIES)
        prompt = f"""请根据以下输入生成公司名称候选，并推荐最匹配的主营行业大类。
用户字号偏好：{request.namePref}
用户业务描述：{request.desc or "（未提供，仅依据字号偏好推断）"}

可选行业大类（recommendedBusiness 必须从中精确选取一项）：
{industries_text}
"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]

        try:
            response = await llm_service.chat(messages=messages, temperature=0.0)
            data = json.loads(response)

            # 名称去重并过滤空值，限制在 3-5 个
            names = [n.strip() for n in data.get("names", []) if isinstance(n, str) and n.strip()]
            names = list(dict.fromkeys(names))[:5]

            # 行业大类必须精确命中列表，否则置空交由前端处理
            recommended = data.get("recommendedBusiness", "")
            if recommended not in INDUSTRY_CATEGORIES:
                recommended = ""

            return {
                "code": 200,
                "status": "success",
                "message": "生成公司名称成功",
                "data": CompanyBasicInfoResponse(
                    names=names,
                    recommendedBusiness=recommended,
                )
            }
        except Exception as e:
            # 返回默认响应
            return {
                "code": 500,
                "status": "error",
                "message": f"生成公司名称失败: {str(e)}",
                "data": CompanyBasicInfoResponse(
                    names=["名称一", "名称二", "名称三", "名称四", "名称五"],
                    recommendedBusiness="",
                )
            }

    @staticmethod
    async def process_page2_check_approval(request: ApprovalInfoRequest) -> dict[str, int | str | ApprovalInfoResponse]:
        """
        第二页：审批信息
        - 输入：主要经营范围,具体描述
        - 输出：是否需要审批、审批类型、审批详情
        """
        # 构建一组提示词：系统提示词、用户提示词、综合消息
        system_prompt = """你是一位资深的中国大陆工商注册合规顾问，熟悉前置审批、后置审批目录。
任务：根据用户所选行业大类与业务描述，判断该业务在注册流程中是否涉及行政许可/审批，并说明审批类型与要点。

概念界定：
- 前置审批：必须在工商登记【之前】取得许可，否则无法注册（如：金融、危化品、医疗机构、教育培训等）。
- 后置审批：可先完成工商登记，但【经营前】须取得相应资质/许可（如：餐饮的食品经营许可、建筑施工资质、增值电信业务许可等）。
- 无需审批：一般性行业（如普通信息技术服务、咨询、设计等）。

判断原则：
1. 行业大类范围较广，须结合业务描述定位到具体经营活动再判断；描述为空时，按该行业最常见的普通经营情形判断。
2. needsApproval 为布尔值 true/false。
3. type 只能取以下三者之一：前置审批 | 后置审批 | （空字符串）。needsApproval 为 false 时 type 必须为空字符串。
4. details 给出具体、可操作的说明：涉及哪些许可证、由哪个主管部门核发、办理顺序与大致条件。无需审批时简要说明该业务通常无需专项审批即可经营。details 支持使用 \\n 换行与"• "列举。

只输出 JSON，键为 needsApproval、type、details。
EXAMPLE JSON OUTPUT:
{
    "needsApproval": true,
    "type": "后置审批",
    "details": "餐饮服务可先完成工商登记，经营前须办理以下许可：\\n\\n• 食品经营许可证（市场监督管理部门）\\n• 涉及堂食的还需排污、环保等相关手续\\n\\n建议在取得营业执照后尽快申办，避免无证经营。"
}
"""
        prompt = f"""请判断以下业务在中国大陆注册时的审批情况：
行业大类：{request.industry}
具体业务描述：{request.desc or "（未提供，按该行业最常见的普通经营情形判断）"}
"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]

        try:
            response = await llm_service.chat(messages=messages, temperature=0.0)
            data = json.loads(response)

            needs_approval = bool(data.get("needsApproval", False))
            approval_type = data.get("type", "") or ""
            # type 只允许三种取值，且与 needsApproval 保持自洽
            if approval_type not in ("前置审批", "后置审批"):
                approval_type = ""
            if not needs_approval:
                approval_type = ""

            return {
                "code": 200,
                "status": "success",
                "message": "查询审批信息成功",
                "data": ApprovalInfoResponse(
                    needsApproval=needs_approval,
                    type=approval_type,
                    details=data.get("details", "") or "",
                )
            }
        except Exception as e:
            return {
                "code": 500,
                "status": "error",
                "message": f"查询审批信息失败: {str(e)}",
                "data": ApprovalInfoResponse(
                    needsApproval=True,
                    type="后置审批",
                    details="建筑施工及相关业务需在工商登记后取得资质证书方可承接工程。\n\n• 建筑施工：建筑业企业资质证书（住房和城乡建设部门）\n• 工程设计：工程设计资质证书\n• 工程监理企业资质证书\n\n资质申请需满足注册资本、技术人员、业绩等要求，办理时限约60个工作日",
                )
            }

    @staticmethod
    async def process_page3_business_scope(request: BusinessScopeRequest) -> dict[
        str, int | str | BusinessScopeResponse]:
        """
        第三页：生成经营范围
        - 一个formData结构，包含多个字段
        - 输出：主营业务，其他经营范围项目
        """
        system_prompt = """你是一位资深的中国大陆工商注册经营范围顾问，熟悉工商登记规范的经营范围用语。
任务：根据公司已填写信息，确定一个核心主营业务，并补充若干相关的其他经营范围项目。

规则：
1. main：一个最能代表公司核心业务的规范经营范围用语（如"软件开发""技术服务""餐饮服务"），简洁规范，不含标点，不要照抄行业大类名称。
2. others：3-5 个与主营业务相关、可合法登记的经营范围用语，彼此不重复，且不与 main 重复；优先选用工商登记常用规范表述。
3. 用语须符合中国大陆经营范围登记习惯，避免使用需特批却与本业务无关的项目。

只输出 JSON，键为 main、others。
EXAMPLE INPUT:
主营业务类型：(I) 信息传输、软件和信息技术服务业
人数：10
股东数量：3
公司名称偏好：星河云创
最终公司名称：星禾云创科技有限公司
EXAMPLE JSON OUTPUT:
{
    "main": "软件开发",
    "others": ["信息系统集成服务", "技术服务", "技术咨询", "数据处理服务"]
}
"""
        fd = request.formData
        prompt = f"""请根据以下公司信息，确定一个主营业务并生成 3-5 个相关的其他经营范围项目：
主营业务类型（行业大类）：{fd.business or "（未提供）"}
人数：{fd.people if fd.people is not None else "（未提供）"}
股东数量：{fd.shareholder if fd.shareholder is not None else "（未提供）"}
公司名称偏好：{fd.namePref or "（未提供）"}
最终公司名称：{fd.name or "（未提供）"}
"""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]

        try:
            response = await llm_service.chat(messages=messages, temperature=0.0)
            data = json.loads(response)

            main = (data.get("main") or "").strip()
            others = [o.strip() for o in data.get("others", []) if isinstance(o, str) and o.strip()]
            # 去重并剔除与主营业务重复的项，保留 3-5 个
            others = [o for o in dict.fromkeys(others) if o != main][:5]

            return {
                "code": 200,
                "status": "success",
                "message": "生成经营范围成功",
                "data": BusinessScopeResponse(
                    main=main,
                    others=others
                )
            }
        except Exception as e:
            return {
                "code": 500,
                "message": f"生成经营范围失败: {str(e)}",
                "status": "error",
                "data": BusinessScopeResponse(
                    main=request.formData.business,
                    others=["错误信息", "错误信息", "错误信息"]
                )
            }

    @staticmethod
    async def process_page4_company_type(request: EmployeeCountRequest) -> dict[str, int | str | EmployeeCountResponse]:
        """
        第四页：根据基础信息推荐公司类型
        输入：公司人数、股东人数、前面已填写信息
        输出：推荐公司类型、解释说明原因
        """
        system_prompt = """你是一位资深的中国大陆工商注册顾问，熟悉《公司法》《市场主体登记管理条例》下各类市场主体的设立条件与适用场景。
任务：根据公司人数、股东人数及已填写信息，推荐最合适的市场主体类型，并说明理由。

companyType 只能从以下取值中精确选取一项：
- 个人独资企业：仅 1 名出资人，且为自然人独资，承担无限责任，适合小本经营、风险低的个体业务。
- 一人有限责任公司：仅 1 名股东（自然人或法人），以认缴出资为限担责，适合单一股东但希望隔离风险。
- 有限责任公司：2-50 名股东，以认缴出资为限担责，是绝大多数中小企业的首选。
- 合伙企业：2 名及以上合伙人共同经营、共担风险，常见于律所、会计师事务所、投资基金等专业服务或合伙投资场景。
- 股份有限公司：股东人数较多、计划规范治理或未来融资/上市，设立门槛与治理要求较高。

判断原则：
1. 优先依据股东人数（shareholder）判断：1 人优先在"个人独资企业 / 一人有限责任公司"间权衡（看是否需要风险隔离），2 人及以上默认"有限责任公司"。
2. 仅当业务/规模明显匹配时才推荐合伙企业或股份有限公司，避免对普通中小企业过度推荐。
3. explanation 用通俗语言说明推荐理由，并简要点出该类型的责任承担与关键注意点，100 字以内。

只输出 JSON，键为 companyType、explanation。
EXAMPLE JSON OUTPUT:
{
    "companyType": "有限责任公司",
    "explanation": "公司有 3 名股东，选择有限责任公司可按认缴出资承担有限责任，设立与治理成本低，是中小企业的常规选择。"
}
"""
        fd = request.formData
        scope_main = fd.scope.main if fd.scope else ""
        scope_others = fd.scope.others if fd.scope else []
        prompt = f"""请根据以下信息推荐市场主体类型并说明理由：
公司人数：{request.people}
股东人数：{request.shareholder}
行业大类：{fd.business or "（未提供）"}
公司名称偏好：{fd.namePref or "（未提供）"}
最终公司名称：{fd.name or "（未提供）"}
主营业务：{scope_main or "（未提供）"}
其他经营范围：{scope_others}
"""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]

        try:
            response = await llm_service.chat(messages=messages, temperature=0.0)
            data = json.loads(response)
            return {
                "code": 200,
                "status": "success",
                "message": "推荐公司类型成功",
                "data": EmployeeCountResponse(
                    companyType=(data.get("companyType") or "").strip(),
                    explanation=(data.get("explanation") or "").strip()
                )
            }
        except Exception as e:
            return {
                "code": 500,
                "status": "error",
                "message": f"推荐公司类型失败: {str(e)}",
                "data": EmployeeCountResponse(
                    companyType="",
                    explanation="错误信息"
                )
            }

    @staticmethod
    async def process_page5_capital_estimate(request: CapitalRequest) -> dict[str, int | str | CapitalResponse]:
        """
        第五页：预估注册资本
        - 输入：意向金额(万元)、前面已填写信息
        - 输出：预估金额(万元)
        """
        system_prompt = """你是一位资深的中国大陆工商注册顾问，擅长为中小企业及一人有限责任公司规划注册资本。
任务：根据用户的【认缴投入意向】与【主营业务/公司信息】，给出一个合理的建议注册资本（万元）及简明解释。

分析逻辑（严格按顺序思考）：
1. 法定底线：
   · 一般行业实行认缴制，无最低注册资本限制。
   · 若业务涉及法定最低注册资本的特许行业（如劳务派遣≥200万、建筑施工≥按资质等级、保险经纪≥1000万、增值电信业务≥100万等），建议金额必须不低于对应法定限额。
2. 注册资本 ≠ 投入资金：投入资金还含开办费、设备、流动资金等。
   · 一般建议注册资本约为投入意向的 30%~70%。
   · 比例过低（<30%）显得实力不足，影响招投标与信任；过高（>100%）会放大股东认缴责任与风险。
   · 若投入意向 < 10 万，建议注册资本可等于或略高于投入意向。
3. 行业风险匹配：
   · 低风险（咨询、设计、零售、信息技术服务）：约 10~100 万，取投入意向的 40%~60%。
   · 中风险（贸易、餐饮、小规模生产、装修）：约 30~200 万，取投入意向的 50%~70%。
   · 高风险（建筑工程、劳务派遣、金融、医疗器械）：先满足法定底线，再在其上浮 20%~50%或参考投入意向取高者。
4. 认缴制提醒：注册资本为认缴制，无需立即实缴，但须在章程约定期限（一般 5 年内）缴足；建议金额不宜超过股东未来 3~5 年可承受的实缴能力。

输出要求：
- estimatedAmount：数字类型（万元），整数或保留一位小数，不要带单位或引号。
- explanation：100 字以内，说明该金额的合理性与关键合规要点。

只输出 JSON，键为 estimatedAmount、explanation。
EXAMPLE JSON OUTPUT:
{
    "estimatedAmount": 50,
    "explanation": "结合 100 万元投入意向与信息技术服务的低风险特征，建议注册资本 50 万元，约为投入的一半，既体现实力又控制认缴压力。注册资本为认缴制，可在 5 年内缴足。"
}
"""
        fd = request.formData
        scope_main = fd.scope.main if fd.scope else ""
        scope_others = fd.scope.others if fd.scope else []
        prompt = f"""请根据以下信息给出建议注册资本（万元）及解释：
认缴投入意向：{request.capitalIntention}（万元，仅为用户资金投入预期，并非最终注册资本，请结合上述逻辑合理规划）
行业大类：{fd.business or "（未提供）"}
人数：{fd.people if fd.people is not None else "（未提供）"}
股东数量：{fd.shareholder if fd.shareholder is not None else "（未提供）"}
公司类型：{fd.companyType or "（未提供）"}
公司名称偏好：{fd.namePref or "（未提供）"}
最终公司名称：{fd.name or "（未提供）"}
主营业务：{scope_main or "（未提供）"}
其他经营范围：{scope_others}
"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]

        try:
            response = await llm_service.chat(messages=messages, temperature=0.0)
            data = json.loads(response)

            # estimatedAmount 容错：模型可能返回字符串（如 "50万"），提取数值，失败则回退到意向金额
            raw_amount = data.get("estimatedAmount")
            try:
                estimated = float(raw_amount)
            except (TypeError, ValueError):
                match = re.search(r"-?\d+(?:\.\d+)?", str(raw_amount or ""))
                estimated = float(match.group()) if match else float(request.capitalIntention)
            estimated = max(estimated, 0.0)

            return {
                "code": 200,
                "status": "success",
                "message": "预估注册资本成功",
                "data": CapitalResponse(
                    estimatedAmount=estimated,
                    explanation=data.get("explanation", "") or ""
                )
            }
        except Exception as e:
            return {
                "code": 500,
                "status": "error",
                "message": f"预估注册资本失败: {str(e)}",
                "data": CapitalResponse(
                    estimatedAmount=request.capitalIntention,
                    explanation=""
                )
            }

    @staticmethod
    async def process_page6_address_recommend(request: AddressRequest) -> dict[str, int | str | AddressResponse]:
        """
        第六页：推荐注册地址类型
        根据主营业务、注册资本和省份推荐
        """
        system_prompt = """你是一位资深的中国大陆工商注册地址顾问，熟悉各类注册地址的合规要求与适用场景。
任务：根据公司所在省份与已填写信息，从给定四类地址中推荐最合适的一种，并说明理由。

recommendation 只能从以下四项中精确选取一项：
- 商用办公地址：正规商办楼/写字楼，资质齐全、可实地核查，适合需要对外接待、招投标或对资质要求较高的业务。
- 园区/孵化器地址：产业园、孵化器、集中办公区提供的地址，常有租金优惠或注册扶持，适合初创、科技型小微企业。
- 虚拟地址：由园区或代办机构提供的合规挂靠地址（仅用于注册，不实际办公），成本低，适合轻资产、线上或无固定经营场所的业务；需注意部分地区/行业不允许。
- 住宅地址：以住宅作为经营场所，部分城市允许"住改商"或一址多照，适合无对外经营、低扰民的个体或微型企业；需符合当地住改商规定。

判断原则：
1. 结合行业特点、公司规模（人数）、注册资本与省份政策综合判断。
2. 涉及前置/后置许可、对实地经营场所有硬性要求的业务（如餐饮、生产、危化品等），优先推荐商用办公地址或园区地址，避免推荐虚拟/住宅地址。
3. explanation 要具体说明推荐理由及该地址类型的注意事项，不要过于简短。

只输出 JSON，键为 recommendation、explanation。
EXAMPLE JSON OUTPUT:
{
    "recommendation": "园区/孵化器地址",
    "explanation": "公司为信息技术类初创企业、规模较小，推荐入驻产业园区或孵化器地址，可享受注册扶持与租金优惠，地址合规且便于后续享受相关产业政策。需确认园区可提供正式注册地址证明。"
}
"""
        fd = request.formData
        prompt = f"""请根据以下信息推荐注册地址类型并说明理由：
省份：{request.province}
行业大类：{fd.business}
人数：{fd.people}
股东数量：{fd.shareholder}
公司类型：{fd.companyType}
公司名称偏好：{fd.namePref}
最终公司名称：{fd.name}
主营业务：{fd.scope.main}
其他经营范围：{fd.scope.others}
注册资本：{fd.capital}
"""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]

        try:
            response = await llm_service.chat(messages=messages, temperature=0.0)
            data = json.loads(response)

            # recommendation 限定为四类合法地址类型，命中失败则置空
            recommendation = data.get("recommendation", "") or ""
            if recommendation not in ADDRESS_TYPES:
                recommendation = ""

            return {
                "code": 200,
                "status": "success",
                "message": "推荐注册地址成功",
                "data": AddressResponse(
                    province=request.province,
                    recommendation=recommendation,
                    explanation=data.get("explanation", "") or ""
                )
            }
        except Exception as e:
            return {
                "code": 500,
                "status": "error",
                "message": f"推荐注册地址失败: {str(e)}",
                "data": AddressResponse(
                    province=request.province,
                    recommendation="",
                    explanation=""
                )
            }

    @staticmethod
    async def process_page7_org_tips(request: OrgTipsRequest) -> dict:
        """第七页：生成组织架构小tips"""
        system_prompt = """你是一位资深的中国大陆公司治理与组织架构顾问。
任务：根据用户的公司信息，给出一条简短、实用、有针对性的组织架构建议。

要求：
1. 结合行业特点、公司规模（人数）、股东人数与公司类型给出建议，避免空泛套话。
2. 建议须具体可操作，例如关键岗位/部门设置、治理结构（股东会/执行董事/监事等）、人少时的职能合并思路。
3. 控制在 100 字以内，使用通俗中文。

只输出 JSON，键为 tips。
EXAMPLE JSON OUTPUT:
{
    "tips": "10 人左右的软件公司，建议设研发、市场、行政三条线，由执行董事统筹、设监事一名即可，初期产品与项目管理可由技术负责人兼任，待规模扩大再拆分。"
}
"""
        prompt = f"""请根据以下公司信息，给出一条 100 字以内、具针对性的组织架构建议。
注意：用户所选行业往往只是大类，应结合其具体业务与经营范围细化建议。
公司信息：
{json.dumps(request.formData, ensure_ascii=False)}
"""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
        try:
            response = await llm_service.chat(messages=messages, temperature=0.3)
            data = json.loads(response)
            return {
                "code": 200,
                "status": "success",
                "message": "生成组织架构tips成功",
                "data": OrgTipsResponse(tips=data.get("tips", ""))
            }
        except Exception as e:
            return {
                "code": 500,
                "status": "error",
                "message": f"生成组织架构tips失败: {str(e)}",
                "data": OrgTipsResponse(tips="")
            }
