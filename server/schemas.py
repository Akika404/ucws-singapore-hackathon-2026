from token import OP

from pydantic import BaseModel, Field
from typing import List, Optional, Literal
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
