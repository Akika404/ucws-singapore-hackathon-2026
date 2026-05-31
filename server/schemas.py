from token import OP

from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional, Literal, Union
from enum import Enum

# ============== 第一页：generate-names ==============
# 根据用户填写的公司名称偏好（字号）和业务描述，生成候选公司全称。

class CompanyBasicInfoRequest(BaseModel):
    """第一页请求：公司基本信息"""
    namePref: str = Field(..., description="公司名称偏好")
    desc: Optional[str] = Field(None, description="公司业务描述，用于 AI 生成更贴合业务的后缀")

class CompanyBasicInfoResponse(BaseModel):
    """第一页响应"""
    names: List[str] = Field(default_factory=list, description="公司名称建议列表")
    recommendedBusiness: str = Field("", description="AI 推荐的主营业务（国民经济行业分类大类，A~T，需与前端行业列表一致）")

# ============== 第二页：check-approval ==============
# 根据所选行业大类，返回该行业是否涉及前置/后置审批及具体说明。
class ApprovalInfoRequest(BaseModel):
    """审批信息"""
    industry: str = Field(..., description="行业大类（国民经济行业分类，A~T）")
    desc: Optional[str] = Field(None, description="公司业务描述，用于辅助 AI 判")

class ApprovalType(str, Enum):
    BEFOR = "前置审批"
    AFTER = "后置审批"
    NONE = ""  # 无审批时用空字符串

class ApprovalInfoResponse(BaseModel):
    """审批响应"""
    needsApproval: bool = Field(..., description="是否涉及审批")
    # type 放宽为字符串：合法取值（前置/后置审批，中英文）由 service 按 X-Lang 校验
    type: str = Field("", description="审批类型：前置审批/后置审批/空字符串（按语言）")
    details: str = Field(..., description="审批说明详情，支持换行符")


# ============== 第三页：business-scope ==============
# 经营范围：根据前面已填写的完整信息，生成主营业务和其他经营范围。

# 先定义内部 formData 结构
class BusinessScopeFormData(BaseModel):
    business: Optional[str] = Field(None, description="主营业务类型")
    people: Optional[int] = Field(None, description="人数")
    shareholder: Optional[int] = Field(None, description="股东数")
    namePref: Optional[str] = Field(None, description="公司名称偏好")
    name: Optional[str] = Field(None, description="最终公司名称")

# 外层请求（完整结构）
class BusinessScopeRequest(BaseModel):
    """请求：经营范围"""
    formData: BusinessScopeFormData = Field(..., description="表单完整数据")


class BusinessScopeResponse(BaseModel):
    """响应：主营业务、主营业务（一个）、其他经营范围·"""
    main: str = Field(..., description="主营业务（一个）")
    others: List[str] = Field(..., description="其他经营范围")

# ============== 第四页：company-type ==============
# 公司类型：根据前面已填写的完整信息，生成推荐的公司类型。

class BusinessScopeData(BaseModel):
    main: str = Field(..., description="主营业务")
    others: List[str] = Field(..., description="其他经营范围列表")

class EmployeeCountFormData(BaseModel):
    """公司人数、股东人数、前面已填写信息"""
    business: Optional[str] = Field(None, description="主营业务类型")
    namePref: Optional[str] = Field(None, description="公司名称偏好")
    name: Optional[str] = Field(None, description="最终公司名称")
    scope: Optional[BusinessScopeData] = Field(None, description="经营范围")


class EmployeeCountRequest(BaseModel):
    """请求：公司人数、股东人数、前面已填写信息"""
    people: int = Field(..., description="人数")
    shareholder: int = Field(..., description="股东数")
    formData: EmployeeCountFormData = Field(..., description="表单完整数据")

class EmployeeCountResponse(BaseModel):
    """响应:推荐公司类型、解释说明原因"""
    companyType: str = Field(..., description="推荐的公司类型")
    explanation: str = Field(..., description="解释说明原因")


# ============== 第五页：capital-estimate ==============
# 注册资本：根据注册资金意向和前面已填写的完整信息，生成推荐的注册资本。

class ScopeData(BaseModel):
    main: str = Field(..., description="主营业务")
    others: List[str] = Field(..., description="其他经营范围列表")

class CapitalFormData(BaseModel):
    business: Optional[str] = Field(None, description="主营业务类型")
    people: Optional[int] = Field(None, description="公司人数")
    shareholder: Optional[int] = Field(None, description="股东人数")
    companyType: Optional[str] = Field(None, description="公司类型")
    namePref: Optional[str] = Field(None, description="公司名称偏好")
    name: Optional[str] = Field(None, description="最终公司全称")
    scope: Optional[ScopeData] = Field(None, description="经营范围")

class CapitalRequest(BaseModel):
    """请求：意向注册资本 + 完整历史表单数据"""
    capitalIntention: float = Field(..., description="注册资本意向(万元)", ge=0)
    formData: CapitalFormData = Field(..., description="完整表单数据")

class CapitalResponse(BaseModel):
    """响应：预估金额(万元)"""
    estimatedAmount: float = Field(..., description="预估金额(万元)")
    explanation: str = Field(..., description="建议与解释")

# ============== 第六页：address-recommendations ==============
# 注册地址：根据前面已填写的完整信息，生成推荐的注册地址。

# 1. 经营范围结构
class ScopeData(BaseModel):
    main: str = Field(..., description="主营业务")
    others: List[str] = Field(..., description="其他经营范围列表")

# 2. 完整 formData 结构（和你 JSON 完全一致）
class AddressFormData(BaseModel):
    business: str = Field(..., description="主营业务类型")
    people: int = Field(..., description="公司人数")
    shareholder: int = Field(..., description="股东人数")
    companyType: str = Field(..., description="公司类型")
    namePref: str = Field(..., description="公司名称偏好")
    name: str = Field(..., description="最终公司名称")
    scope: ScopeData = Field(..., description="经营范围")
    capital: str = Field(..., description="注册资本描述信息")

# 3. 最外层请求
class AddressRequest(BaseModel):
    """请求：注册地址 + 已填写表单信息"""
    province: str = Field(..., description="省份")
    formData: AddressFormData = Field(..., description="完整表单数据")

class AddressResponse(BaseModel):
    """响应：推荐的地址类型、推荐理由"""
    province: str = Field(..., description="省份")
    recommendation: str = Field(..., description="推荐的地址类型")
    explanation: str = Field(..., description="推荐理由")

# ============== 第七页：org-tips ==============
class OrgTipsRequest(BaseModel):
    """请求：组织架构小tips"""
    formData: dict = Field(..., description="完整表单数据")

class OrgTipsResponse(BaseModel):
    """响应：组织架构小tips"""
    tips: str = Field(..., description="组织架构建议")


# ============== 开业成本预估 ==============
class FormDataOnlyRequest(BaseModel):
    """通用请求：只包含完整 formData"""
    formData: Dict[str, Any] = Field(..., description="完整表单数据")


class OpeningCostCompanyProfile(BaseModel):
    previewName: str = Field("", description="拟展示公司名称")
    companyType: str = Field("", description="公司类型")
    province: str = Field("", description="注册地")
    industry: str = Field("", description="行业")
    teamSize: int = Field(0, description="团队规模")
    shareholder: int = Field(0, description="股东人数")
    capitalWan: float = Field(0, description="注册资本，单位万元")
    scopeMain: str = Field("", description="主营范围")
    scopeOthers: List[str] = Field(default_factory=list, description="其他经营范围")


class OpeningCostSummary(BaseModel):
    currency: str = Field("CNY", description="币种")
    period: str = Field("", description="预算周期")
    totalBudget: float = Field(0, description="总预算，单位元")
    cashReserveLabel: str = Field("", description="现金储备标签")
    conclusion: str = Field("", description="AI 总评")


class OpeningCostItem(BaseModel):
    id: str = Field("", description="成本科目 id")
    name: str = Field("", description="成本科目名称")
    amount: float = Field(0, description="预估金额，单位元")
    tier: str = Field("", description="权重档位")
    reason: str = Field("", description="金额依据")


class OpeningCostCategory(BaseModel):
    id: str = Field("", description="成本体系 id")
    name: str = Field("", description="成本体系名称")
    shortName: str = Field("", description="短名称")
    icon: str = Field("", description="图标")
    color: str = Field("", description="颜色")
    subtotal: float = Field(0, description="当前体系小计，单位元")
    benchmark: float = Field(0, description="行业基准小计，单位元")
    items: List[OpeningCostItem] = Field(default_factory=list, description="成本科目")


class PiePoint(BaseModel):
    categoryId: str = Field("", description="成本体系 id")
    name: str = Field("", description="名称")
    value: float = Field(0, description="金额")
    color: str = Field("", description="颜色")


class RadarData(BaseModel):
    labels: List[str] = Field(default_factory=list, description="标签")
    current: List[float] = Field(default_factory=list, description="当前方案")
    benchmark: List[float] = Field(default_factory=list, description="行业基准")


class TopDriver(BaseModel):
    name: str = Field("", description="驱动项名称")
    amount: float = Field(0, description="金额")


class OpeningCostCharts(BaseModel):
    pie: List[PiePoint] = Field(default_factory=list, description="甜甜圈图数据")
    radar: RadarData = Field(default_factory=RadarData, description="雷达图数据")
    topDrivers: List[TopDriver] = Field(default_factory=list, description="成本 Top 驱动项")


class OpeningCostResponse(BaseModel):
    companyProfile: OpeningCostCompanyProfile = Field(default_factory=OpeningCostCompanyProfile)
    summary: OpeningCostSummary = Field(default_factory=OpeningCostSummary)
    categories: List[OpeningCostCategory] = Field(default_factory=list)
    charts: OpeningCostCharts = Field(default_factory=OpeningCostCharts)
    tips: List[str] = Field(default_factory=list)


# ============== 扶持政策检索 ==============
class SupportPolicyCompanyProfile(BaseModel):
    previewName: str = Field("", description="拟展示公司名称")
    province: str = Field("", description="注册地")
    industry: str = Field("", description="行业")
    teamSize: int = Field(0, description="团队规模")
    capitalWan: float = Field(0, description="注册资本，单位万元")


class SupportPolicySummary(BaseModel):
    matchedCount: int = Field(0, description="匹配政策数量")
    maxBenefit: float = Field(0, description="可量化红利合计，单位元")
    currency: str = Field("CNY", description="币种")
    conclusion: str = Field("", description="AI 总评")


class SupportPolicyCategory(BaseModel):
    id: str = Field("", description="政策类别 id")
    name: str = Field("", description="政策类别名称")
    count: int = Field(0, description="命中数量")
    color: str = Field("", description="颜色")


class SupportPolicyBenefit(BaseModel):
    displayPrefix: str = Field("", description="展示前缀")
    displayValue: str = Field("", description="展示值")
    amount: float = Field(0, description="可量化金额，单位元")
    unit: str = Field("", description="单位")


class SupportPolicyRequirements(BaseModel):
    province: Union[str, List[str]] = Field("all", description="地区要求")
    minTeamSize: int = Field(0, description="最低人数")
    minCapitalWan: float = Field(0, description="最低注册资本，单位万元")
    industries: Union[str, List[str]] = Field("all", description="行业要求")


class SupportPolicyAction(BaseModel):
    label: str = Field("", description="按钮文案")
    url: str = Field("", description="官方政策申报入口链接，优先返回当地政务服务网或主管部门办事页")


class SupportPolicyItem(BaseModel):
    id: str = Field("", description="政策 id")
    category: str = Field("", description="政策类别")
    categoryName: str = Field("", description="政策类别名称")
    title: str = Field("", description="政策标题")
    description: str = Field("", description="政策描述")
    department: str = Field("", description="主管部门")
    priority: str = Field("", description="优先级")
    priorityLabel: str = Field("", description="优先级展示文案")
    benefit: SupportPolicyBenefit = Field(default_factory=SupportPolicyBenefit)
    probability: int = Field(0, description="通过率，0-100")
    deadlineDays: int = Field(0, description="距截止天数")
    cycle: str = Field("", description="办理周期")
    reasons: List[str] = Field(default_factory=list, description="匹配理由")
    requirements: SupportPolicyRequirements = Field(default_factory=SupportPolicyRequirements)
    materials: List[str] = Field(default_factory=list, description="建议材料")
    applyAction: SupportPolicyAction = Field(default_factory=SupportPolicyAction)


class SupportPolicyFilters(BaseModel):
    categoryOptions: List[str] = Field(default_factory=list)
    priorityOptions: List[str] = Field(default_factory=list)
    sortOptions: List[str] = Field(default_factory=list)
    defaultSort: str = Field("priority")


class SupportPoliciesResponse(BaseModel):
    companyProfile: SupportPolicyCompanyProfile = Field(default_factory=SupportPolicyCompanyProfile)
    summary: SupportPolicySummary = Field(default_factory=SupportPolicySummary)
    categories: List[SupportPolicyCategory] = Field(default_factory=list)
    policies: List[SupportPolicyItem] = Field(default_factory=list)
    filters: SupportPolicyFilters = Field(default_factory=SupportPolicyFilters)
    tips: List[str] = Field(default_factory=list)
