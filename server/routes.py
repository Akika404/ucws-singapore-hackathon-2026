from io import BytesIO
from pathlib import Path
from typing import List
from urllib.parse import quote
from zipfile import ZIP_DEFLATED, ZipFile

from fastapi import APIRouter, HTTPException, Header
from fastapi.responses import FileResponse, StreamingResponse

#导入格式模板
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

from services import BusinessService

router = APIRouter()

DOCUMENT_FILE_DIR = Path(__file__).resolve().parents[1] / "public" / "file"
DOCUMENTS = [
    {"id": "offer-letter", "title": "Offer letter", "filename": "offer_letter.docx"},
    {"id": "employment-condition", "title": "录用条件确认书", "filename": "录用条件确认书.docx"},
    {"id": "onboarding-form", "title": "新员工入职登记表", "filename": "新员工入职登记表.docx"},
    {"id": "application-form", "title": "应聘登记表", "filename": "应聘登记表.docx"},
    {"id": "labor-contract", "title": "劳动合同", "filename": "劳动合同.docx"},
    {"id": "part-time-agreement", "title": "非全日制用工协议书", "filename": "非全日制用工协议书.docx"},
    {"id": "confidentiality-agreement", "title": "保密协议", "filename": "保密协议.docx"},
    {"id": "non-compete-agreement", "title": "竞业限制协议", "filename": "竞业限制协议.docx"},
    {"id": "salary-table", "title": "工资表", "filename": "工资表.xlsx"},
    {"id": "attendance-sheet", "title": "考勤表", "filename": "考勤表.xlsx"},
    {"id": "attendance-leave-policy", "title": "考勤休假管理制度", "filename": "考勤休假管理制度.docx"},
    {"id": "employee-roster", "title": "职工名册", "filename": "职工名册.xlsx"},
    {"id": "employee-handbook", "title": "员工管理手册", "filename": "员工管理手册.docx"},
    {"id": "performance-review", "title": "绩效评估报告", "filename": "绩效评估报告.docx"},
    {"id": "resignation-approval", "title": "员工离职审批表（辞职）", "filename": "员工离职审批表（辞职）.docx"},
    {"id": "dismissal-approval", "title": "员工离职审批表（辞退）", "filename": "员工离职审批表（辞退）.docx"},
    {"id": "departure-certificate", "title": "离职证明", "filename": "离职证明.docx"},
    {"id": "contract-termination-notice", "title": "终止劳动合同通知书", "filename": "终止劳动合同通知书.docx"},
]


def get_document_or_404(document_id: str) -> dict:
    for document in DOCUMENTS:
        if document["id"] == document_id:
            return document
    raise HTTPException(status_code=404, detail="文书不存在")


def get_document_path_or_404(document: dict) -> Path:
    file_path = (DOCUMENT_FILE_DIR / document["filename"]).resolve()
    if DOCUMENT_FILE_DIR.resolve() not in file_path.parents or not file_path.is_file():
        raise HTTPException(status_code=404, detail="文书文件不存在")
    return file_path


@router.get("/documents")
async def list_documents():
    return {
        "documents": [
            {
                **document,
                "downloadUrl": f"/api/documents/{document['id']}/download",
                "available": (DOCUMENT_FILE_DIR / document["filename"]).is_file(),
            }
            for document in DOCUMENTS
        ]
    }


@router.get("/documents/{document_id}/download")
async def download_document(document_id: str):
    document = get_document_or_404(document_id)
    file_path = get_document_path_or_404(document)
    return FileResponse(
        path=file_path,
        media_type="application/octet-stream",
        filename=document["filename"],
    )


@router.get("/documents/download-all")
async def download_all_documents():
    buffer = BytesIO()
    files_written = 0

    with ZipFile(buffer, "w", ZIP_DEFLATED) as zip_file:
        for document in DOCUMENTS:
            file_path = (DOCUMENT_FILE_DIR / document["filename"]).resolve()
            if DOCUMENT_FILE_DIR.resolve() in file_path.parents and file_path.is_file():
                zip_file.write(file_path, arcname=document["filename"])
                files_written += 1

    if files_written == 0:
        raise HTTPException(status_code=404, detail="暂无可下载文书")

    buffer.seek(0)
    archive_name = "高频合同与文书模板.zip"
    headers = {
        "Content-Disposition": f"attachment; filename*=UTF-8''{quote(archive_name)}"
    }
    return StreamingResponse(buffer, media_type="application/zip", headers=headers)

@router.post("/generate-names", response_model=CompanyBasicInfoResponse)
async def page1_generate_names(request: CompanyBasicInfoRequest, x_lang: str = Header("en", alias="X-Lang")):
    """
    第一页：公司基本信息
    - 输入：公司名称、主营业务（前端传过来），格式校验后面再完善
    - 输出：3-5个公司名称建议、前置/后置审批判断
    """
    try:
        result = await BusinessService.process_page1_generate_names(request, x_lang)
        #这里加上返回格式校验
        if result["status"] == "success":
            print("1.公司基本信息，路由返回内容：")
            print(result["data"])
            return result["data"]
        else:
            raise HTTPException(status_code=500, detail=f"处理失败: {result['message']}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理失败: {str(e)}")

@router.post("/check-approval", response_model=ApprovalInfoResponse)
async def page2_check_approval(request: ApprovalInfoRequest, x_lang: str = Header("en", alias="X-Lang")):
    """
    第二页：审批信息
    - 输入：业务类型,具体描述
    - 输出：审批信息（是否需要审批、审批类型、审批详情）
    """
    try:
        result = await BusinessService.process_page2_check_approval(request, x_lang)
        if result["status"] == "success":
            print("2.审批信息，路由返回内容：")
            print(result["data"])
            return result["data"]
        else:
            raise HTTPException(status_code=500, detail=f"处理失败: {result['message']}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理失败: {str(e)}")


@router.post("/business-scope", response_model=BusinessScopeResponse)
async def page3_business_scope(request: BusinessScopeRequest, x_lang: str = Header("en", alias="X-Lang")):
    """
    第三页：经营范围
    - 输入：一个formData结构，包含多个字段
    - 输出：多个其他经营范围
    """
    try:
        result = await BusinessService.process_page3_business_scope(request, x_lang)
        if result["status"] == "success":
            print("3.经营范围，路由返回内容：")
            print(result["data"])
            return result["data"]
        else:
            raise HTTPException(status_code=500, detail=f"处理失败: {result['message']}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理失败: {str(e)}")


@router.post("/company-type", response_model=EmployeeCountResponse)
async def page4_company_type(request: EmployeeCountRequest, x_lang: str = Header("en", alias="X-Lang")):
    """
    第四页：根据基础信息推荐公司类型
    输入：公司人数、股东人数、前面已填写信息
    输出：推荐公司类型、解释说明原因
    """
    try:
        result = await BusinessService.process_page4_company_type(request, x_lang)
        if result["status"] == "success":
            print("4.根据基础信息推荐公司类型，路由返回内容：")
            print(result["data"])
            return result["data"]
        else:
            raise HTTPException(status_code=500, detail=f"处理失败: {result['message']}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理失败: {str(e)}")


@router.post("/capital-estimate", response_model=CapitalResponse)
async def page5_capital_estimate(request: CapitalRequest, x_lang: str = Header("en", alias="X-Lang")):
    """
    第五页：注册资本
    - 输入：主营业务类型、注册资本意向金额
    - 输出：预估金额(万元)
    """
    try:
        result = await BusinessService.process_page5_capital_estimate(request, x_lang)
        if result["status"] == "success":
            print("5.注册资本，路由返回内容：")
            print(result["data"])
            return result["data"]
        else:
            raise HTTPException(status_code=500, detail=f"处理失败: {result['message']}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理失败: {str(e)}")


@router.post("/address-recommendations", response_model=AddressResponse)
async def page6_address_recommend(request: AddressRequest, x_lang: str = Header("en", alias="X-Lang")):
    """
    第六页：注册地址
    - 输入：主营业务类型、注册资本、省份
    - 输出：地址类型推荐（商用办公地址、园区/孵化器/集中办公区地址、虚拟地址、住宅地址）
    """
    try:
        result = await BusinessService.process_page6_address_recommend(request, x_lang)
        if result["status"] == "success":
            print("6.注册地址，路由返回内容：")
            print(result["data"])
            return result["data"]
        else:
            raise HTTPException(status_code=500, detail=f"处理失败: {result['message']}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理失败: {str(e)}")


@router.post("/org-tips", response_model=OrgTipsResponse)
async def page7_org_tips(request: OrgTipsRequest, x_lang: str = Header("en", alias="X-Lang")):
    try:
        result = await BusinessService.process_page7_org_tips(request, x_lang)
        if result["status"] == "success":
            print("7.组织架构tips，路由返回内容：")
            print(result["data"])
            return result["data"]
        else:
            raise HTTPException(status_code=500, detail=f"处理失败: {result['message']}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理失败: {str(e)}")


@router.post("/opening-cost-estimate", response_model=OpeningCostResponse)
async def opening_cost_estimate(request: FormDataOnlyRequest, x_lang: str = Header("en", alias="X-Lang")):
    """
    开业成本预估
    - 输入：完整 formData
    - 输出：AI 生成的首季开业成本、六大成本体系、图表数据与提示
    """
    try:
        result = await BusinessService.process_opening_cost_estimate(request, x_lang)
        if result["status"] == "success":
            return result["data"]
        raise HTTPException(status_code=500, detail=f"处理失败: {result['message']}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理失败: {str(e)}")


@router.post("/support-policies/search", response_model=SupportPoliciesResponse)
async def support_policies_search(request: FormDataOnlyRequest, x_lang: str = Header("en", alias="X-Lang")):
    """
    扶持政策检索
    - 输入：完整 formData
    - 输出：AI 生成的政策匹配结果、红利预估、申报优先级与材料建议
    """
    try:
        result = await BusinessService.process_support_policies_search(request, x_lang)
        if result["status"] == "success":
            return result["data"]
        raise HTTPException(status_code=500, detail=f"处理失败: {result['message']}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理失败: {str(e)}")
