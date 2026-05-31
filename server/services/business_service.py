import json
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
        system_prompt = """你是一位专业的公司注册顾问。
        请根据用户输入生成公司名称建议，并从给定的行业大类列表中选出最贴合用户业务的一个，作为推荐的主营业务。
        Please parse the "names" and "recommendedBusiness" and output them in JSON format.
        EXAMPLE JSON OUTPUT:
        {
            "names": ["星禾云创科技有限公司", "璀璨星禾商务有限公司", "星禾流动网络有限公司"],
            "recommendedBusiness": "(I) 信息传输、软件和信息技术服务业"
        }
        """
        industries_text = "\n".join(INDUSTRY_CATEGORIES)
        prompt = f"""
                请根据用户的输入参考名称和描述信息作为参考。
                1. 生成3-5个公司包含用户偏好词的名称设计，用户偏好词可以在名称的任意位置，生成的名称要符合中国大陆的公司命名规范，且尽量体现业务特点，不要过于通用。
                2. 从以下国民经济行业分类大类中，选择最贴合用户业务的一个作为推荐主营业务，recommendedBusiness 必须与列表中的某一项完全一致（包含括号字母前缀）：
                {industries_text}
                用户偏好词：[{request.namePref}]
                用户的业务描述：{request.desc}
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
                "message": "生成公司名称成功",
                "data": CompanyBasicInfoResponse(
                    names=data.get("names", []),
                    recommendedBusiness=data.get("recommendedBusiness", ""),
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
        system_prompt = """你是一位专业的公司注册顾问。
        Please parse the "needsApproval" and "type" and "detail" and output them in JSON format.
        EXAMPLE JSON OUTPUT:
        {
            "needsApproval": true,#这个返回的是布尔值
            "type": "前置审批",# 从["前置审批","后置审批",""] 中选择,不需要审批选择空字符串
            "details": "公司需要在注册前获得相关审批，才能正式注册。"
        }
        """
        prompt = f"""
                请根据用户的输入行业大类和具体描述(可选)，判断是否需要审批、审批类型、审批详情。如果需要审批，请给出对应的详细的规则。
                行业大类：{request.industry}
                具体描述：{request.desc}(可选)
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
                "message": "查询审批信息成功",
                "data": ApprovalInfoResponse(
                    needsApproval=data.get("needsApproval"),
                    type=data.get("type"),
                    details=data.get("details"),
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
        system_prompt = """你是一位专业的公司注册顾问。
        Please parse the "main" and "others" and output them in JSON format.
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
        prompt = f"""
        请根据用户的输入信息作为参考，生成3-5个相关的其他经营范围项目：
        主营业务类型：{request.formData.business}
        人数：{request.formData.people}
        股东数量：{request.formData.shareholder}
        公司名称偏好：{request.formData.namePref}
        最终公司名称：{request.formData.name}
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
                "message": "生成经营范围成功",
                "data": BusinessScopeResponse(
                    main=data.get("main"),
                    others=data.get("others")
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
        system_prompt = """你是一位专业的公司注册顾问。
        Please parse the "companyType" and "explanation" and output them in JSON format.

        EXAMPLE JSON OUTPUT:
        {
            "companyType": "有限责任公司",
            "explanation": "这里是为什么选择'有限责任公司'的说明。"
        }
        """
        prompt = f"""
        请根据用户的输入信息作为参考，推荐公司类型以及解释说明原因：
        公司人数：{request.people}
        股东人数：{request.shareholder}
        主营业务类型：{request.formData.business}
        行业：{request.formData.business}
        名称偏好：{request.formData.namePref}
        最终公司名称：{request.formData.name}
        主营业务：{request.formData.scope.main}
        其他经营范围：{request.formData.scope.others}
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
                    companyType=data.get("companyType"),
                    explanation=data.get("explanation")
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
        system_prompt = """你是一位专业的公司注册顾问。
        Please parse the "estimatedAmount" and "explanation" and output them in JSON format.
        EXAMPLE JSON OUTPUT:
        {
            "estimatedAmount": 预估金额(万元),
            "explanation": "100字以内的建议与解释"
        }
        """
        prompt = f"""
        系统角色与任务
        你是一位资深工商注册顾问，擅长为 OPC（一人有限责任公司）及小微企业提供注册资本规划建议。请根据用户提供的【预计投入资金】和【主营业务】，输出：
        
        1. 一个合适的注册资本金额（单位：万元，整数或保留一位小数）。
        2. 一段100字以内的建议与解释，说明该数字的合理性及工商合规要点。
        
        分析逻辑（严格按顺序思考）
        
        1. 法定底线：
           · 一般行业无最低注册资本限制（1元亦可）。
           · 若主营业务涉及需要前置/后置许可的行业（如劳务派遣≥200万、建筑施工≥400万、保险经纪≥1000万、增值电信业务≥100万等），必须满足对应最低限额。
           · 若无特殊许可，跳过此条。
        2. 投入资金与注册资本的关系：
           · 注册资本≠投入资金。投入资金通常包括开办费、设备、运营流动资金等。
           · **建议注册资本控制在投入资金的30%~70%之间：**
             · 比例过低（<30%）：客户、合作方可能认为公司实力不足，影响招投标或信任。
             · 比例过高（>100%）：股东面临更大的认缴责任，且超出实际能力可能被认定为“天价资本”引发风险。
           · 若用户投入资金<10万，注册资本可等于或略高于投入资金（如投入5万，建议注册资本5万），因低资本下认缴压力小。
        3. 行业风险匹配：
           · 低风险行业（咨询、设计、零售、信息技术服务）：建议注册资本10万~100万，偏向投入资金的40%~60%。
           · 中风险行业（贸易、餐饮、小规模生产、装修）：建议注册资本30万~200万，偏向投入资金的50%~70%。
           · 高风险行业（建筑工程、劳务派遣、金融服务、医疗器械）：必须满足法定底线，并在底线基础上上浮20%~50%或参考投入资金取高者。
        4. 认缴制适用：
           · 提醒用户：注册资本为认缴制，不要求立即实缴，但需在章程中明确期限内缴足（5年）。
           · 建议数字不宜超过用户未来3~5年可承受的实缴能力。
        -----
        用户投入资本意向（认缴金额）：{request.capitalIntention}（万元）// 此项并非为最终的注册资本，而是用户的资金投入预期，建议注册资本需结合此预期进行合理规划。
        主营业务类型：{request.formData.business}
        人数：{request.formData.people}
        股东数量：{request.formData.shareholder}
        公司类型：{request.formData.companyType}
        公司名称偏好：{request.formData.namePref}
        最终公司名称：{request.formData.name}
        主营业务：{request.formData.scope.main}
        其他经营范围：{request.formData.scope.others}
        """
        print(prompt)

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
                "message": "预估注册资本成功",
                "data": CapitalResponse(
                    estimatedAmount=float(data.get("estimatedAmount")),
                    explanation=data.get("explanation", "")
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
        system_prompt = """你是一位专业的公司注册顾问。
        Please parse the "province" and "recommendation" and "explanation" and output them in JSON format.
        EXAMPLE JSON OUTPUT:
        {
            "recommendation": "商用办公地址",#从这四个种类中选取（商用办公地址、园区/孵化器地址、虚拟地址、住宅地址）
            "explanation": "推荐理由"#详细说明不要过于简短
        }

"""
        prompt = f"""
            请根据用户的输入的信息作为参考，推荐注册地址类型以及解释说明原因：
            省份：{request.province}
            主营业务类型：{request.formData.business}
            人数：{request.formData.people}
            股东数量：{request.formData.shareholder}
            公司名称偏好：{request.formData.namePref}
            最终公司名称：{request.formData.name}
            主营业务：{request.formData.scope.main}
            其他经营范围：{request.formData.scope.others}
            意向注册资本：{request.formData.capital}（万元）

            推理生成推荐的地址类型和推荐理由
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
                "message": "推荐注册地址成功",
                "data": AddressResponse(
                    province=request.province,
                    recommendation=data.get("recommendation", ""),
                    explanation=data.get("explanation", "")
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
        system_prompt = """你是一位专业的公司注册顾问。
        根据用户的公司信息，生成一条简短实用的组织架构建议（100字以内）。
        EXAMPLE JSON OUTPUT:
        {
            "tips": "建议内容"
        }
        """
        prompt = f"""根据以下公司信息生成组织架构小tips：
        用户所选的行业可能仅仅是一个大类，具体的业务类型和经营范围会影响组织架构的设计。
        请根据用户提供的主营业务类型、注册资本、公司规模等信息，结合行业特点，给出一条简短实用的组织架构建议（100字以内）。请确保建议具有针对性和可操作性，能够帮助用户更好地规划公司的组织结构。
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
