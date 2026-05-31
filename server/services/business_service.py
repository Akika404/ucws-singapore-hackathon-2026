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
    FormDataOnlyRequest,
    OpeningCostResponse,
    SupportPoliciesResponse,
)
from .llm_service import llm_service
from .prompts import (
    SYSTEM_PROMPTS,
    INDUSTRY_CATEGORIES,
    ADDRESS_TYPES,
    APPROVAL_TYPES,
    FALLBACKS,
    normalize_lang,
    build_page1_user,
    build_page2_user,
    build_page3_user,
    build_page4_user,
    build_page5_user,
    build_page6_user,
    build_page7_user,
    build_opening_cost_user,
    build_support_policies_user,
)


class BusinessService:
    """业务逻辑服务 - 统一返回标准格式: {code, status, message, data}

    所有方法接受 lang('en'|'zh')，据此选择系统/用户提示词、受校验列表与异常兜底文本。
    响应 JSON 键名保持稳定，仅取值随语言变化。"""

    @staticmethod
    def _coerce_json_object(response: str) -> Dict[str, Any]:
        data = json.loads(response)
        if not isinstance(data, dict):
            raise ValueError("LLM response is not a JSON object")
        return data

    @staticmethod
    def _normalize_opening_cost(data: Dict[str, Any]) -> Dict[str, Any]:
        categories = data.get("categories")
        if not isinstance(categories, list):
            categories = []

        total = 0.0
        pie = []
        radar_labels = []
        radar_current = []
        radar_benchmark = []
        drivers = []

        for cat in categories:
            if not isinstance(cat, dict):
                continue
            items = cat.get("items") if isinstance(cat.get("items"), list) else []
            subtotal = 0.0
            for item in items:
                if not isinstance(item, dict):
                    continue
                try:
                    item["amount"] = max(float(item.get("amount", 0) or 0), 0.0)
                except (TypeError, ValueError):
                    item["amount"] = 0.0
                subtotal += item["amount"]
                drivers.append({
                    "name": item.get("name", "") or "",
                    "amount": item["amount"],
                })
            cat["subtotal"] = round(subtotal)
            try:
                cat["benchmark"] = max(float(cat.get("benchmark", subtotal) or subtotal), 0.0)
            except (TypeError, ValueError):
                cat["benchmark"] = subtotal
            total += cat["subtotal"]
            pie.append({
                "categoryId": cat.get("id", "") or "",
                "name": cat.get("name", "") or "",
                "value": cat["subtotal"],
                "color": cat.get("color", "") or "",
            })
            radar_labels.append(cat.get("shortName") or cat.get("name", ""))
            radar_current.append(cat["subtotal"])
            radar_benchmark.append(round(cat["benchmark"]))

        summary = data.get("summary") if isinstance(data.get("summary"), dict) else {}
        summary["currency"] = summary.get("currency") or "CNY"
        summary["totalBudget"] = round(total)
        data["summary"] = summary

        drivers = sorted(drivers, key=lambda x: x["amount"], reverse=True)[:10]
        data["charts"] = {
            "pie": pie,
            "radar": {
                "labels": radar_labels[:6],
                "current": radar_current[:6],
                "benchmark": radar_benchmark[:6],
            },
            "topDrivers": drivers,
        }
        return data

    @staticmethod
    def _normalize_support_policies(data: Dict[str, Any]) -> Dict[str, Any]:
        policies = data.get("policies")
        if not isinstance(policies, list):
            policies = []

        allowed_categories = ["funding", "tax", "space", "loan", "talent"]
        counts = {k: 0 for k in allowed_categories}
        max_benefit = 0.0

        normalized_policies = []
        for idx, policy in enumerate(policies):
            if not isinstance(policy, dict):
                continue
            category = policy.get("category")
            if category not in allowed_categories:
                category = "funding"
            policy["category"] = category
            counts[category] += 1

            priority = policy.get("priority")
            if priority not in ("P0", "P1", "P2"):
                priority = "P2"
            policy["priority"] = priority

            try:
                policy["probability"] = min(max(int(policy.get("probability", 0) or 0), 0), 100)
            except (TypeError, ValueError):
                policy["probability"] = 0
            try:
                policy["deadlineDays"] = max(int(policy.get("deadlineDays", 1) or 1), 1)
            except (TypeError, ValueError):
                policy["deadlineDays"] = 1

            benefit = policy.get("benefit") if isinstance(policy.get("benefit"), dict) else {}
            try:
                benefit["amount"] = max(float(benefit.get("amount", 0) or 0), 0.0)
            except (TypeError, ValueError):
                benefit["amount"] = 0.0
            max_benefit += benefit["amount"]
            policy["benefit"] = benefit
            policy["id"] = policy.get("id") or f"P-AI-{idx + 1:02d}"
            normalized_policies.append(policy)

        raw_categories = data.get("categories") if isinstance(data.get("categories"), list) else []
        raw_category_names = {
            c.get("id"): c.get("name")
            for c in raw_categories
            if isinstance(c, dict) and c.get("id") and c.get("name")
        }
        fallback_category_names = {
            "all": "全部政策",
            "funding": "资金补贴",
            "tax": "税收减免",
            "space": "场地免租",
            "loan": "金融信贷",
            "talent": "人才落户",
        }
        category_names = {
            key: raw_category_names.get(key) or fallback_category_names[key]
            for key in ["all", *allowed_categories]
        }
        category_colors = {
            "all": "#475569",
            "funding": "#e11d48",
            "tax": "#059669",
            "space": "#0891b2",
            "loan": "#1677ff",
            "talent": "#7c3aed",
        }
        data["categories"] = [
            {"id": "all", "name": category_names["all"], "count": len(normalized_policies), "color": category_colors["all"]},
            *[
                {"id": key, "name": category_names[key], "count": counts[key], "color": category_colors[key]}
                for key in allowed_categories
            ],
        ]
        data["policies"] = normalized_policies
        summary = data.get("summary") if isinstance(data.get("summary"), dict) else {}
        summary["matchedCount"] = len(normalized_policies)
        summary["maxBenefit"] = round(max_benefit)
        summary["currency"] = summary.get("currency") or "CNY"
        data["summary"] = summary
        data["filters"] = {
            "categoryOptions": ["all", "funding", "tax", "space", "loan", "talent"],
            "priorityOptions": ["ALL", "P0", "P1", "P2"],
            "sortOptions": ["priority", "amountDesc", "probDesc", "deadlineAsc"],
            "defaultSort": "priority",
        }
        return data

    @staticmethod
    async def process_page1_generate_names(request: CompanyBasicInfoRequest, lang: str = "en") -> dict[
        str, int | str | CompanyBasicInfoResponse]:
        """
        第一页：处理公司基本信息
        - 输入：公司名称、描述信息
        - 生成公司名称建议
        """
        lang = normalize_lang(lang)
        system_prompt = SYSTEM_PROMPTS[lang]["page1"]
        prompt = build_page1_user(lang, request)

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
            if recommended not in INDUSTRY_CATEGORIES[lang]:
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
                    names=FALLBACKS[lang]["page1_names"],
                    recommendedBusiness="",
                )
            }

    @staticmethod
    async def process_page2_check_approval(request: ApprovalInfoRequest, lang: str = "en") -> dict[str, int | str | ApprovalInfoResponse]:
        """
        第二页：审批信息
        - 输入：主要经营范围,具体描述
        - 输出：是否需要审批、审批类型、审批详情
        """
        lang = normalize_lang(lang)
        system_prompt = SYSTEM_PROMPTS[lang]["page2"]
        prompt = build_page2_user(lang, request)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]

        try:
            response = await llm_service.chat(messages=messages, temperature=0.0)
            data = json.loads(response)

            needs_approval = bool(data.get("needsApproval", False))
            approval_type = data.get("type", "") or ""
            # type 只允许两种非空取值（按语言），且与 needsApproval 保持自洽
            if approval_type not in APPROVAL_TYPES[lang]:
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
                    type=FALLBACKS[lang]["page2_type"],
                    details=FALLBACKS[lang]["page2_details"],
                )
            }

    @staticmethod
    async def process_page3_business_scope(request: BusinessScopeRequest, lang: str = "en") -> dict[
        str, int | str | BusinessScopeResponse]:
        """
        第三页：生成经营范围
        - 一个formData结构，包含多个字段
        - 输出：主营业务，其他经营范围项目
        """
        lang = normalize_lang(lang)
        system_prompt = SYSTEM_PROMPTS[lang]["page3"]
        prompt = build_page3_user(lang, request)
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
                    others=FALLBACKS[lang]["page3_others"]
                )
            }

    @staticmethod
    async def process_page4_company_type(request: EmployeeCountRequest, lang: str = "en") -> dict[str, int | str | EmployeeCountResponse]:
        """
        第四页：根据基础信息推荐公司类型
        输入：公司人数、股东人数、前面已填写信息
        输出：推荐公司类型、解释说明原因
        """
        lang = normalize_lang(lang)
        system_prompt = SYSTEM_PROMPTS[lang]["page4"]
        prompt = build_page4_user(lang, request)
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
                    explanation=FALLBACKS[lang]["page4_explanation"]
                )
            }

    @staticmethod
    async def process_page5_capital_estimate(request: CapitalRequest, lang: str = "en") -> dict[str, int | str | CapitalResponse]:
        """
        第五页：预估注册资本
        - 输入：意向金额(万元)、前面已填写信息
        - 输出：预估金额(万元)
        """
        lang = normalize_lang(lang)
        system_prompt = SYSTEM_PROMPTS[lang]["page5"]
        prompt = build_page5_user(lang, request)

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
    async def process_page6_address_recommend(request: AddressRequest, lang: str = "en") -> dict[str, int | str | AddressResponse]:
        """
        第六页：推荐注册地址类型
        根据主营业务、注册资本和省份推荐
        """
        lang = normalize_lang(lang)
        system_prompt = SYSTEM_PROMPTS[lang]["page6"]
        prompt = build_page6_user(lang, request)
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]

        try:
            response = await llm_service.chat(messages=messages, temperature=0.0)
            data = json.loads(response)

            # recommendation 限定为四类合法地址类型（按语言），命中失败则置空
            recommendation = data.get("recommendation", "") or ""
            if recommendation not in ADDRESS_TYPES[lang]:
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
    async def process_page7_org_tips(request: OrgTipsRequest, lang: str = "en") -> dict:
        """第七页：生成组织架构小tips"""
        lang = normalize_lang(lang)
        system_prompt = SYSTEM_PROMPTS[lang]["page7"]
        prompt = build_page7_user(lang, request)
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

    @staticmethod
    async def process_opening_cost_estimate(request: FormDataOnlyRequest, lang: str = "en") -> dict:
        """开业成本预估：由 AI 生成预算结构、明细与图表数据。"""
        lang = normalize_lang(lang)
        system_prompt = SYSTEM_PROMPTS[lang]["opening_cost"]
        prompt = build_opening_cost_user(lang, request)
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ]
        print("======== LLM Request Messages ========")
        print(json.dumps(messages, ensure_ascii=False, indent=2))
        try:
            response = await llm_service.chat(messages=messages, temperature=0.2)
            data = BusinessService._coerce_json_object(response)
            data = BusinessService._normalize_opening_cost(data)
            print("======== LLM Response Data ========")
            print(json.dumps(data, ensure_ascii=False, indent=2))
            return {
                "code": 200,
                "status": "success",
                "message": "生成开业成本预估成功",
                "data": OpeningCostResponse.model_validate(data),
            }
        except Exception as e:
            return {
                "code": 500,
                "status": "error",
                "message": f"生成开业成本预估失败: {str(e)}",
                "data": OpeningCostResponse(),
            }

    @staticmethod
    async def process_support_policies_search(request: FormDataOnlyRequest, lang: str = "en") -> dict:
        """扶持政策检索：由 AI 生成匹配政策、红利估算与申报建议。"""
        lang = normalize_lang(lang)
        system_prompt = SYSTEM_PROMPTS[lang]["support_policies"]
        prompt = build_support_policies_user(lang, request)
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ]
        try:
            response = await llm_service.chat(messages=messages, temperature=0.2)
            data = BusinessService._coerce_json_object(response)
            data = BusinessService._normalize_support_policies(data)
            return {
                "code": 200,
                "status": "success",
                "message": "生成扶持政策检索结果成功",
                "data": SupportPoliciesResponse.model_validate(data),
            }
        except Exception as e:
            return {
                "code": 500,
                "status": "error",
                "message": f"生成扶持政策检索结果失败: {str(e)}",
                "data": SupportPoliciesResponse(),
            }
