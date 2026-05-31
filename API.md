# API 文档

Base URL: `http://localhost:8080`

> 约定：`formData` 始终表示"截至当前步骤之前已保存的所有字段"，本步骤新输入的字段放在请求体顶层。

---

## GET /api/documents

获取“高频合同与文书”可下载文件目录。

**Response 200**

```json
{
  "documents": [
    {
      "id": "labor-contract",
      "title": "劳动合同",
      "filename": "劳动合同.docx",
      "downloadUrl": "/api/documents/labor-contract/download",
      "available": true
    }
  ]
}
```

## GET /api/documents/{document_id}/download

下载指定文书文件。`document_id` 使用 `/api/documents` 返回的 `id`。

## GET /api/documents/download-all

打包下载全部可用文书模板，返回 zip 文件。

---

## POST /api/generate-names

根据用户填写的公司名称偏好（字号）和业务描述，生成候选公司全称。

**Request**

```json
{
  "namePref": "星禾云创",
  "desc": "面向中小企业的 SaaS 协同办公平台"
}
```

| 字段           | 类型   | 说明                                       |
| -------------- | ------ | ------------------------------------------ |
| `namePref`     | string | 公司名称偏好                               |
| `desc`（可选） | string | 公司业务描述，用于 AI 生成更贴合业务的后缀 |

**Response 200**

```json
{
  "names": [
    "星禾云创科技有限公司",
    "星禾云创商务有限公司",
    "星禾云创网络有限公司"
  ],
  "recommendedBusiness": "(I) 信息传输、软件和信息技术服务业"
}
```

| 字段                  | 类型     | 说明                                                                            |
| --------------------- | -------- | ------------------------------------------------------------------------------- |
| `names`               | string[] | AI 生成的公司全称候选列表                                                        |
| `recommendedBusiness` | string   | AI 推荐的主营业务（国民经济行业分类大类，A~T，与前端行业列表一致），前端默认选中 |

---

## POST /api/check-approval

根据所选行业大类，返回该行业是否涉及前置/后置审批及具体说明。

**Request**

```json
{
  "industry": "(E) 建筑业",
  "desc":"我开发了一个软件，用于xxxxx...."
}
```

| 字段           | 类型   | 说明                              |
| -------------- | ------ | --------------------------------- |
| `industry`     | string | 行业大类（国民经济行业分类，A~T） |
| `desc`（可选） | string | 公司业务描述，用于辅助 AI 判断    |

**Response 200**

```json
{
  "needsApproval": true,
  "type": "后置审批",
  "details": "建筑施工及相关业务需在工商登记后取得资质证书方可承接工程。\n\n• 建筑施工：建筑业企业资质证书（住房和城乡建设部门）\n• 工程设计：工程设计资质证书\n• 工程监理：工程监理企业资质证书\n\n资质申请需满足注册资本、技术人员、业绩等要求，办理时限约60个工作日"
}
```

| 字段            | 类型    | 说明                                                       |
| --------------- | ------- | ---------------------------------------------------------- |
| `needsApproval` | boolean | 是否涉及审批                                               |
| `type`          | string  | 审批类型，取值：`前置审批`、`后置审批`，无审批时为空字符串 |
| `details`       | string  | 审批说明详情，支持换行符 `\n`                              |

---

## POST /api/business-scope

根据前面已填写的完整信息，生成主营业务和其他经营范围。

**Request**

```json
{
  "formData": {
    "business": "(I) 信息传输、软件和信息技术服务业",
    "namePref": "星禾云创",
    "name": "星禾云创科技有限公司"
  }
}
```

**Response 200**

```json
{
  "main": "软件开发",
  "others": ["信息系统集成服务", "技术服务", "技术咨询", "数据处理服务"]
}
```

| 字段               | 类型     | 说明                     |
| ------------------ | -------- | ------------------------ |
| `selectedBusiness` | string   | 前面已经选择的主营业务   |
| `main`             | string   | 拟定出的主营业务（一个） |
| `others`           | string[] | 其他经营范围（多个）     |

---

## POST /api/company-type

根据公司人数和股东人数，结合前面已填写的基础信息，推荐公司类型并给出说明。

**Request**

```json
{
  "people": 10,
  "shareholder": 3,
  "formData": {
    "business": "(E) 建筑业",
    "namePref": "星禾云创",
    "name": "星禾云创科技有限公司",
    "scope": {
      "main": "软件开发",
      "others": [
        "信息系统集成服务",
        "技术服务",
        "技术咨询",
        "数据处理服务"
      ]
    }
  }
}
```

| 字段          | 类型   | 说明                                           |
| ------------- | ------ | ---------------------------------------------- |
| `people`      | number | 公司人数                                       |
| `shareholder` | number | 股东人数                                       |
| `formData`    | object | 前面步骤已保存的字段（业务、字号、公司全称等） |

**Response 200**

```json
{
  "companyType": "有限责任公司",
  "explanation": "这里是为什么选择'有限责任公司'的说明。"
}
```

| 字段          | 类型   | 说明                     |
| ------------- | ------ | ------------------------ |
| `companyType` | string | 推荐的公司类型           |
| `explanation` | string | 选择该公司类型的理由说明 |

---

## POST /api/capital-estimate

根据用户输入的注册资本意向（认缴金额）和前面已填写的完整信息，返回预估金额。

**Request**

```json
{
  "capitalIntention": 100,
  "formData": {
    "business": "(C) 制造业",
    "people": 10,
    "shareholder": 3,
    "companyType": "有限责任公司",
    "namePref": "星禾云创",
    "name": "星禾云创科技有限公司",
    "scope": {
      "main": "软件开发",
      "others": [
        "信息系统集成服务",
        "技术服务",
        "技术咨询",
        "数据处理服务"
      ]
    }
  }
}
```

| 字段               | 类型   | 说明                           |
| ------------------ | ------ | ------------------------------ |
| `capitalIntention` | number | 用户输入的认缴金额，单位：万元 |
| `formData`         | object | 前面步骤已保存的字段           |

**Response 200**

```json
{
  "estimatedAmount": 100
}
```

| 字段              | 类型   | 说明                     |
| ----------------- | ------ | ------------------------ |
| `estimatedAmount` | number | 后端预估金额，单位：万元 |

---

## POST /api/address-recommendations

根据用户选择的注册省份和前面已填写的完整信息，从"商用办公地址、园区/孵化器/集中办公区地址、虚拟地址、住宅地址"中返回推荐注册地址类型并给出说明。

**Request**

```json
{
  "province": "北京市",
  "formData": {
    "business": "(C) 制造业",
    "people": 10,
    "shareholder": 3,
    "companyType": "有限责任公司",
    "namePref": "星禾云创",
    "name": "星禾云创科技有限公司",
    "scope": {
      "main": "软件开发",
      "others": [
        "信息系统集成服务",
        "技术服务",
        "技术咨询",
        "数据处理服务"
      ]
    },
    "capital": "认缴金额：100 万元；预估金额：100 万元"
  }
}
```

| 字段       | 类型   | 说明                           |
| ---------- | ------ | ------------------------------ |
| `province` | string | 用户选择的注册省份，不含港澳台 |
| `formData` | object | 前面步骤已保存的字段           |

**Response 200**

```json
{
  "province": "北京市",
  "recommendation": "商用办公地址",
  "explanation": "这里是为什么推荐'商用办公地址'的说明。"
}
```

| 字段             | 类型   | 说明                       |
| ---------------- | ------ | -------------------------- |
| `province`       | string | 用户选择的注册省份         |
| `recommendation` | string | 推荐的注册地址类型，四选一 |
| `explanation`    | string | 推荐该地址类型的理由说明   |

---

## POST /api/opening-cost-estimate

根据“智能工商注册顾问”已保存的完整 `formData`，AI 生成“开业成本预估”页面所需的首季现金储备预算、六大成本体系明细、图表数据与风险提示。

**Request**

```json
{
  "formData": {
    "business": "(I) 信息传输、软件和信息技术服务业",
    "people": 10,
    "shareholder": 3,
    "companyType": "有限责任公司",
    "namePref": "星禾云创",
    "name": "星禾云创科技有限公司",
    "scope": {
      "main": "软件开发",
      "others": [
        "信息系统集成服务",
        "技术服务",
        "技术咨询",
        "数据处理服务"
      ]
    },
    "capital": "认缴金额：100 万元；预估金额：100 万元",
    "address": "北京市海淀区中关村创业大街"
  }
}
```

| 字段       | 类型   | 说明                                                                 |
| ---------- | ------ | -------------------------------------------------------------------- |
| `formData` | object | 截至当前步骤已保存的完整表单数据。后端从中识别行业、地区、人数、股东、公司类型、字号、注册资本和经营范围 |

**Response 200**

```json
{
  "companyProfile": {
    "previewName": "星禾云创科技有限公司",
    "companyType": "有限责任公司",
    "province": "北京市",
    "industry": "信息传输、软件和信息技术服务业",
    "teamSize": 10,
    "shareholder": 3,
    "capitalWan": 100,
    "scopeMain": "软件开发",
    "scopeOthers": [
      "信息系统集成服务",
      "技术服务",
      "技术咨询",
      "数据处理服务"
    ]
  },
  "summary": {
    "currency": "CNY",
    "period": "开办首季",
    "totalBudget": 488000,
    "cashReserveLabel": "实时申报首季现金储备需求",
    "conclusion": "以轻资产软件服务企业为基准，首季预算重点集中在人力、数字化工具和基础合规投入。北京地区办公与合规服务价格偏高，建议预留 8%-12% 机动资金。"
  },
  "categories": [
    {
      "id": "compliance",
      "name": "合规与制度成本",
      "shortName": "合规",
      "icon": "⚖️",
      "color": "#6366f1",
      "subtotal": 52000,
      "benchmark": 48000,
      "items": [
        {
          "id": "regCompliance",
          "name": "注册/设立/基础合规",
          "amount": 12000,
          "tier": "10–30%",
          "reason": "包含工商注册、刻章、银行开户、基础制度文件与初期行政办理成本。"
        },
        {
          "id": "license",
          "name": "行业资质/许可证",
          "amount": 8000,
          "tier": "10–30%",
          "reason": "软件与信息服务通常无重许可，但涉及数据、互联网信息服务或特定行业客户时需预留合规咨询预算。"
        },
        {
          "id": "legalTaxBasic",
          "name": "法律/税务基础服务",
          "amount": 32000,
          "tier": "10–30%",
          "reason": "用于合同模板、财税建账、股东协议及初期税务申报辅导。"
        }
      ]
    },
    {
      "id": "digital",
      "name": "数字化与软件成本",
      "shortName": "数字化",
      "icon": "💻",
      "color": "#06b6d4",
      "subtotal": 76000,
      "benchmark": 69000,
      "items": [
        {
          "id": "saas",
          "name": "SaaS订阅（CRM/ERP/HRM）",
          "amount": 18000,
          "tier": "30%以上",
          "reason": "协同办公、客户管理、财务与人事工具是信息服务企业启动期的核心生产力投入。"
        },
        {
          "id": "cloud",
          "name": "云服务/服务器/CDN",
          "amount": 24000,
          "tier": "30%以上",
          "reason": "用于开发、测试、上线环境及基础安全防护。"
        },
        {
          "id": "devops",
          "name": "系统开发/DevOps/IT工具",
          "amount": 22000,
          "tier": "30%以上",
          "reason": "覆盖代码托管、CI/CD、监控、日志与研发协作工具。"
        },
        {
          "id": "apiAi",
          "name": "API/AI工具/自动化",
          "amount": 12000,
          "tier": "30%以上",
          "reason": "用于模型接口、自动化流程和客服/销售辅助工具。"
        }
      ]
    }
  ],
  "charts": {
    "pie": [
      { "categoryId": "compliance", "name": "合规与制度成本", "value": 52000, "color": "#6366f1" },
      { "categoryId": "digital", "name": "数字化与软件成本", "value": 76000, "color": "#06b6d4" }
    ],
    "radar": {
      "labels": ["合规", "空间", "数字化", "人力", "增长", "风险"],
      "current": [52000, 68000, 76000, 216000, 54000, 22000],
      "benchmark": [48000, 62000, 69000, 210000, 59000, 19000]
    },
    "topDrivers": [
      { "name": "人力成本（核心团队）", "amount": 180000 },
      { "name": "办公租金", "amount": 52000 },
      { "name": "云服务/服务器/CDN", "amount": 24000 }
    ]
  },
  "tips": [
    "以上成本为基于行业矩阵和企业画像的模拟推演，实际支出需结合城市、供应商及谈判能力逐项询价。",
    "如使用园区注册地址或共享办公空间，空间与基础设施成本通常可下调 15%-30%。"
  ]
}
```

| 字段                               | 类型     | 说明                                                                 |
| ---------------------------------- | -------- | -------------------------------------------------------------------- |
| `companyProfile`                   | object   | 页面顶部公司画像，用于展示公司名、类型、注册地、行业、人数、股东、资本和经营范围 |
| `summary.currency`                 | string   | 币种，固定建议返回 `CNY`                                             |
| `summary.period`                   | string   | 成本周期，例如 `开办首季`                                             |
| `summary.totalBudget`              | number   | 预估总预算，单位：元                                                 |
| `summary.conclusion`               | string   | AI 对预算结构的总评，可展示在提示区或报告中                          |
| `categories`                       | object[] | 六大成本体系，建议固定返回 `compliance`、`space`、`digital`、`people`、`growth`、`risk` |
| `categories[].subtotal`            | number   | 当前成本体系小计，单位：元                                           |
| `categories[].benchmark`           | number   | 行业基准小计，单位：元，用于雷达图对比                              |
| `categories[].items`               | object[] | 当前体系下的预算科目明细                                             |
| `categories[].items[].amount`      | number   | 科目预估金额，单位：元                                               |
| `categories[].items[].tier`        | string   | 该科目在当前行业中的成本权重档位，建议取值：`0–10%`、`10–30%`、`30%以上` |
| `categories[].items[].reason`      | string   | AI 生成的金额依据或业务解释                                          |
| `charts.pie`                       | object[] | 甜甜圈图数据，通常与 `categories` 的小计一致                         |
| `charts.radar`                     | object   | 雷达图数据，包含短标签、当前方案与行业基准                           |
| `charts.topDrivers`                | object[] | 成本 Top 驱动项，按金额从高到低排列                                  |
| `tips`                             | string[] | AI 风险提示、节省建议或后续询价建议                                  |

---

## POST /api/support-policies/search

根据“智能工商注册顾问”已保存的完整 `formData`，AI 生成“扶持政策检索”页面所需的企业画像、政策匹配结果、预估红利、申报优先级和匹配理由。

**Request**

```json
{
  "formData": {
    "business": "(I) 信息传输、软件和信息技术服务业",
    "people": 25,
    "shareholder": 3,
    "companyType": "有限责任公司",
    "namePref": "星禾云创",
    "name": "星禾云创科技有限公司",
    "scope": {
      "main": "软件开发",
      "others": [
        "信息系统集成服务",
        "技术服务",
        "技术咨询",
        "数据处理服务"
      ]
    },
    "capital": "认缴金额：150 万元；预估金额：150 万元",
    "address": "上海市浦东新区张江科学城"
  }
}
```

| 字段       | 类型   | 说明                                                                 |
| ---------- | ------ | -------------------------------------------------------------------- |
| `formData` | object | 截至当前步骤已保存的完整表单数据。后端从中识别行业、注册地、字号、团队规模、注册资本和经营范围 |

**Response 200**

```json
{
  "companyProfile": {
    "previewName": "星禾云创科技有限公司",
    "province": "上海市",
    "industry": "信息传输、软件和信息技术服务业",
    "teamSize": 25,
    "capitalWan": 150
  },
  "summary": {
    "matchedCount": 7,
    "maxBenefit": 708000,
    "currency": "CNY",
    "conclusion": "企业画像符合科技型中小企业、初创企业和吸纳就业类政策的基础条件，建议优先处理时效短、确定性高的就业补贴和税收减免。"
  },
  "categories": [
    { "id": "all", "name": "全部政策", "count": 7, "color": "#475569" },
    { "id": "funding", "name": "资金补贴", "count": 2, "color": "#e11d48" },
    { "id": "tax", "name": "税收减免", "count": 2, "color": "#059669" },
    { "id": "space", "name": "场地免租", "count": 1, "color": "#0891b2" },
    { "id": "loan", "name": "金融信贷", "count": 1, "color": "#1677ff" },
    { "id": "talent", "name": "人才落户", "count": 1, "color": "#7c3aed" }
  ],
  "policies": [
    {
      "id": "P-FUND-02",
      "category": "funding",
      "categoryName": "资金补贴",
      "title": "稳岗扩岗及一次性吸纳就业补贴",
      "description": "鼓励企业吸纳高校毕业生及登记失业人员，当社保缴纳人数达标即可触发该项补贴，部分地区已实现后台比对免申即享。",
      "department": "各地人社局",
      "priority": "P0",
      "priorityLabel": "P0 立即申请",
      "benefit": {
        "displayPrefix": "最高预估",
        "displayValue": "¥ 50,000",
        "amount": 50000,
        "unit": "年"
      },
      "probability": 99,
      "deadlineDays": 15,
      "cycle": "免申即享",
      "reasons": [
        "规模 25 人（要求≥15人）",
        "符合国家普惠性中小微企业标准"
      ],
      "requirements": {
        "province": "all",
        "minTeamSize": 15,
        "minCapitalWan": 0,
        "industries": "all"
      },
      "materials": [
        "营业执照",
        "社保缴纳记录",
        "吸纳就业人员名单"
      ],
      "applyAction": {
        "label": "启动申报",
        "url": "https://zwdt.sh.gov.cn/"
      }
    },
    {
      "id": "P-TALENT-01",
      "category": "talent",
      "categoryName": "人才落户",
      "title": "临港/张江重点产业人才落户",
      "description": "针对特定区域和重点产业创业的核心团队。用人单位引进的紧缺急需人才可直接落户，享受专属人才公寓及租房补贴。",
      "department": "临港管委会/人社局",
      "priority": "P0",
      "priorityLabel": "P0 立即申请",
      "benefit": {
        "displayPrefix": "",
        "displayValue": "3-5年",
        "amount": 0,
        "unit": "居转户缩短"
      },
      "probability": 50,
      "deadlineDays": 20,
      "cycle": "2-3个月",
      "reasons": [
        "上海市属地注册",
        "规模 25 人（要求≥5人）",
        "资本 150 万（要求≥100万）",
        "所属 信息传输、软件和信息技术服务业 等重点行业"
      ],
      "requirements": {
        "province": "上海市",
        "minTeamSize": 5,
        "minCapitalWan": 100,
        "industries": [
          "信息传输、软件和信息技术服务业",
          "科学研究和技术服务业",
          "制造业"
        ]
      },
      "materials": [
        "营业执照",
        "劳动合同",
        "社保与个税记录",
        "重点产业证明材料"
      ],
      "applyAction": {
        "label": "启动申报",
        "url": "https://zwdt.sh.gov.cn/"
      }
    }
  ],
  "filters": {
    "categoryOptions": ["all", "funding", "tax", "space", "loan", "talent"],
    "priorityOptions": ["ALL", "P0", "P1", "P2"],
    "sortOptions": ["priority", "amountDesc", "probDesc", "deadlineAsc"],
    "defaultSort": "priority"
  },
  "tips": [
    "政策口径存在地区与年度差异，正式申报前需以主管部门最新通知为准。",
    "建议优先准备营业执照、社保缴纳记录、财务报表和经营场地证明。"
  ]
}
```

| 字段                           | 类型     | 说明                                                                 |
| ------------------------------ | -------- | -------------------------------------------------------------------- |
| `companyProfile`               | object   | 页面顶部企业画像，用于展示公司名、注册地、行业、团队规模和认缴资本   |
| `summary.matchedCount`         | number   | 匹配政策数量                                                         |
| `summary.maxBenefit`           | number   | 可量化政策红利合计，单位：元；非金额型权益可用 `benefit.amount = 0` 并只参与展示 |
| `summary.conclusion`           | string   | AI 对政策匹配结果的总评和申报建议                                    |
| `categories`                   | object[] | 政策类别及每类命中数量，包含 `all`、`funding`、`tax`、`space`、`loan`、`talent` |
| `policies`                     | object[] | AI 匹配出的政策卡片列表，默认建议按 `P0 > P1 > P2` 排序              |
| `policies[].category`          | string   | 政策类别，取值：`funding`、`tax`、`space`、`loan`、`talent`           |
| `policies[].priority`          | string   | 申报优先级，取值：`P0`、`P1`、`P2`                                   |
| `policies[].benefit.amount`    | number   | 可量化金额，单位：元；无法量化时返回 `0`                             |
| `policies[].benefit.displayValue` | string | 前端直接展示的红利值，例如 `¥ 50,000`、`40%`、`3-5年`                |
| `policies[].probability`       | number   | AI 预估通过率，0-100                                                 |
| `policies[].deadlineDays`      | number   | 距离申报截止的天数                                                   |
| `policies[].cycle`             | string   | 预计办理周期                                                         |
| `policies[].reasons`           | string[] | AI 动态参数匹配理由                                                  |
| `policies[].requirements`      | object   | 触发该政策的结构化条件，便于前端调试和后续筛选                       |
| `policies[].materials`         | string[] | AI 建议准备材料                                                      |
| `policies[].applyAction`       | object   | 申报按钮配置；`url` 应优先返回当地政务服务网、主管部门办事页、园区/银行官方申请页等官方申报入口 |
| `filters`                      | object   | 前端筛选与排序选项                                                   |
| `tips`                         | string[] | AI 风险提示、材料准备建议或申报节奏建议                              |

---

## 错误响应

| 状态码 | 说明                 |
| ------ | -------------------- |
| 400    | 请求体 JSON 解析失败 |
| 404    | 接口路径不存在       |
| 405    | 非 POST 请求         |

---
