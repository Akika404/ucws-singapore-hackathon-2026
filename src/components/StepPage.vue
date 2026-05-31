<script setup lang="ts">
import { ref, watch, computed, onUnmounted } from 'vue'
import type { StepData, BaseFormData } from './RegAdvisor.vue'

const props = defineProps<{
  step: StepData
  stepIndex: number
  totalSteps: number
  selected: string | undefined
  isLast: boolean
  optionsLoading: boolean
  formData: BaseFormData
}>()

const emit = defineEmits<{
  answer: [stepId: string, value: string | import('./RegAdvisor.vue').BusinessScope]
  updateFormData: [patch: Partial<import('./RegAdvisor.vue').BaseFormData>]
  next: []
  prev: []
}>()

const customInput = ref('')
const customActive = ref(false)
const expanded = ref<Set<string>>(new Set())

function cleanFormData(data: BaseFormData): Partial<BaseFormData> {
  const out: Record<string, unknown> = {}
  for (const [k, v] of Object.entries(data)) {
    if (v === null || v === undefined || v === '') continue
    out[k] = v
  }
  return out as Partial<BaseFormData>
}

// --- type step state ---
interface CompanyTypeRecommendation {
  companyType: string
  explanation: string
}

const peopleCount = ref<number | null>(props.formData.people ?? null)
const shareholderCount = ref<number | null>(props.formData.shareholder ?? null)

// 公司人数为 1 人时展示 image_2，否则展示 image_1
const orgImage = computed(() => (peopleCount.value === 1 ? '/image_2.png' : '/image_1.png'))
const typeLoading = ref(false)
const typeError = ref('')
const typeRecommendation = ref<CompanyTypeRecommendation | null>(null)
let typeRequestSeq = 0
let typeTimer: ReturnType<typeof setTimeout> | null = null

async function loadCompanyType() {
  if (props.step.id !== 'type') return
  if (!peopleCount.value || peopleCount.value <= 0) return
  if (!shareholderCount.value || shareholderCount.value <= 0) return
  const seq = ++typeRequestSeq
  typeLoading.value = true
  typeError.value = ''
  try {
    const res = await fetch('/api/company-type', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        people: peopleCount.value,
        shareholder: shareholderCount.value,
        formData: cleanFormData(props.formData),
      }),
    })
    if (!res.ok) throw new Error('Failed to load company type')
    const data = await res.json() as CompanyTypeRecommendation
    if (seq !== typeRequestSeq) return
    typeRecommendation.value = data
    emit('updateFormData', {
      people: peopleCount.value,
      shareholder: shareholderCount.value,
      companyType: data.companyType,
    })
    emit('answer', 'type', data.companyType)
  } catch {
    if (seq !== typeRequestSeq) return
    typeError.value = '公司类型推荐获取失败，请稍后重试'
  } finally {
    if (seq === typeRequestSeq) typeLoading.value = false
  }
}

function scheduleLoadCompanyType() {
  if (typeTimer) clearTimeout(typeTimer)
  typeTimer = setTimeout(() => loadCompanyType(), 350)
}

watch(peopleCount, () => {
  if (props.step.id === 'type') scheduleLoadCompanyType()
})
watch(shareholderCount, () => {
  if (props.step.id === 'type') scheduleLoadCompanyType()
})
watch(() => props.step.id, (id) => {
  if (id === 'type' && !typeRecommendation.value) loadCompanyType()
})
// --- end type step state ---

// --- scope step state ---
interface ScopeRecommendation {
  main: string
  others: string[]
}

const scopeLoading = ref(false)
const scopeError = ref('')
const scopeRecommendation = ref<ScopeRecommendation | null>(null)
let scopeRequestSeq = 0

async function loadScopeRecommendation() {
  const seq = ++scopeRequestSeq
  scopeLoading.value = true
  scopeError.value = ''
  scopeRecommendation.value = null
  try {
    const res = await fetch('/api/business-scope', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        formData: cleanFormData(props.formData),
      }),
    })
    if (!res.ok) throw new Error('Failed to load business scope')
    const data = await res.json() as ScopeRecommendation
    if (seq !== scopeRequestSeq) return
    scopeRecommendation.value = data
    emit('answer', 'scope', { main: data.main, others: data.others })
  } catch {
    if (seq !== scopeRequestSeq) return
    scopeError.value = '经营范围生成失败，请稍后重试'
  } finally {
    if (seq === scopeRequestSeq) scopeLoading.value = false
  }
}

watch(() => props.step.id, (id) => {
  if (id === 'scope') loadScopeRecommendation()
})
// --- end scope step state ---

// --- capital step state ---
interface CapitalEstimate {
  intention: number
  estimatedAmount: number
  explanation: string
}

const capitalIntention = ref<number | null>(null)
const capitalEstimate = ref<CapitalEstimate | null>(null)
const capitalLoading = ref(false)
const capitalError = ref('')
let capitalTimer: ReturnType<typeof setTimeout> | null = null
let capitalRequestSeq = 0

function formatMoneyWan(amount: number) {
  return `${amount.toLocaleString('zh-CN')} 万元`
}

function formatCapitalAnswer(estimate: CapitalEstimate) {
  return `意向投资金额：${formatMoneyWan(estimate.intention)}；预估注册资本/认缴金额：${formatMoneyWan(estimate.estimatedAmount)}`
}

async function loadCapitalEstimate(amount: number) {
  const seq = ++capitalRequestSeq
  capitalLoading.value = true
  capitalError.value = ''
  try {
    const res = await fetch('/api/capital-estimate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        capitalIntention: amount,
        formData: cleanFormData(props.formData),
      }),
    })
    if (!res.ok) throw new Error('Failed to load capital estimate')
    const data = await res.json() as { estimatedAmount: number; explanation: string }
    if (seq !== capitalRequestSeq) return
    const estimate: CapitalEstimate = { intention: amount, estimatedAmount: data.estimatedAmount, explanation: data.explanation ?? '' }
    capitalEstimate.value = estimate
    emit('answer', 'capital', formatCapitalAnswer(estimate))
  } catch {
    if (seq !== capitalRequestSeq) return
    capitalEstimate.value = null
    capitalError.value = '预估金额获取失败，请稍后重试'
  } finally {
    if (seq === capitalRequestSeq) capitalLoading.value = false
  }
}

watch(capitalIntention, (amount) => {
  capitalEstimate.value = null
  capitalError.value = ''
  if (capitalTimer) clearTimeout(capitalTimer)
  if (props.step.id !== 'capital' || !amount || amount <= 0) return
  capitalTimer = setTimeout(() => loadCapitalEstimate(amount), 350)
})
// --- end capital step state ---

// --- address step state ---
interface AddressRecommendations {
  province: string
  recommendation: string
  explanation: string
}

const PROVINCES = [
  '北京市', '天津市', '河北省', '山西省', '内蒙古自治区',
  '辽宁省', '吉林省', '黑龙江省', '上海市', '江苏省',
  '浙江省', '安徽省', '福建省', '江西省', '山东省',
  '河南省', '湖北省', '湖南省', '广东省', '广西壮族自治区',
  '海南省', '重庆市', '四川省', '贵州省', '云南省',
  '西藏自治区', '陕西省', '甘肃省', '青海省', '宁夏回族自治区',
  '新疆维吾尔自治区',
]

const addressProvince = ref('')
const addressLoading = ref(false)
const addressError = ref('')
const addressRecommendations = ref<AddressRecommendations | null>(null)
let addressRequestSeq = 0

function formatAddressAnswer(data: AddressRecommendations) {
  return `${data.province}：推荐：${data.recommendation}`
}

async function loadAddressRecommendations(province: string) {
  const seq = ++addressRequestSeq
  addressLoading.value = true
  addressError.value = ''
  addressRecommendations.value = null
  try {
    const res = await fetch('/api/address-recommendations', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        province,
        formData: cleanFormData(props.formData),
      }),
    })
    if (!res.ok) throw new Error('Failed to load address recommendations')
    const data = await res.json() as AddressRecommendations
    if (seq !== addressRequestSeq) return
    addressRecommendations.value = data
    emit('answer', 'address', formatAddressAnswer(data))
  } catch {
    if (seq !== addressRequestSeq) return
    addressError.value = '注册地址推荐获取失败，请稍后重试'
  } finally {
    if (seq === addressRequestSeq) addressLoading.value = false
  }
}

watch(addressProvince, (province) => {
  addressRecommendations.value = null
  addressError.value = ''
  if (props.step.id !== 'address' || !province) return
  loadAddressRecommendations(province)
})

watch(() => props.step.id, (id) => {
  if (id === 'address' && addressProvince.value && !addressRecommendations.value) {
    loadAddressRecommendations(addressProvince.value)
  }
})
// --- end address step state ---

// --- name step state ---
const INDUSTRIES = [
  '(A) 农、林、牧、渔业', '(B) 采矿业', '(C) 制造业',
  '(D) 电力、热力、燃气及水生产和供应业', '(E) 建筑业',
  '(F) 批发和零售业', '(G) 交通运输、仓储和邮政业',
  '(H) 住宿和餐饮业', '(I) 信息传输、软件和信息技术服务业',
  '(J) 金融业', '(K) 房地产业', '(L) 租赁和商务服务业',
  '(M) 科学研究和技术服务业', '(N) 水利、环境和公共设施管理业',
  '(O) 居民服务、修理和其他服务业', '(P) 教育',
  '(Q) 卫生和社会工作', '(R) 文化、体育和娱乐业',
  '(S) 公共管理、社会保障和社会组织', '(T) 国际组织',
]
const namePref = ref(props.formData.namePref || '')
const nameIndustry = ref('')
const nameDesc = ref('')
const suggestedNames = ref<string[]>([])
const recommendedBusiness = ref('')
const namesLoading = ref(false)
const approval = ref<{ needsApproval: boolean; type: string; details: string } | null>(null)
const approvalLoading = ref(false)
const showModal = ref(false)
const customNameActive = ref(false)
const customNameInput = ref('')

async function generateNames() {
  if (!namePref.value.trim()) return
  namesLoading.value = true
  suggestedNames.value = []
  customNameActive.value = false
  customNameInput.value = ''
  emit('answer', 'name', '')
  try {
    const res = await fetch('/api/generate-names', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ namePref: namePref.value, desc: nameDesc.value }),
    })
    if (res.ok) {
      const data = await res.json()
      suggestedNames.value = data.names
      // AI 推荐的主营业务：匹配到行业列表后默认选中
      const matched = matchIndustry(data.recommendedBusiness || '')
      recommendedBusiness.value = matched
      if (matched) nameIndustry.value = matched
    }
  } catch { /* ignore */ }
  namesLoading.value = false
}

// 把后端返回的主营业务匹配到固定的行业大类列表（容错：精确 → 包含）
function matchIndustry(val: string): string {
  if (!val) return ''
  const exact = INDUSTRIES.find(i => i === val)
  if (exact) return exact
  return INDUSTRIES.find(i => i.includes(val) || val.includes(i)) || ''
}

let approvalTimer: ReturnType<typeof setTimeout> | null = null
watch(nameIndustry, (ind) => {
  if (approvalTimer) clearTimeout(approvalTimer)
  if (!ind) { approval.value = null; approvalLoading.value = false; return }
  approvalLoading.value = true
  approval.value = null
  approvalTimer = setTimeout(async () => {
    try {
      const res = await fetch('/api/check-approval', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ industry: ind, desc: nameDesc.value }),
      })
      if (res.ok) approval.value = await res.json()
    } catch { /* ignore */ } finally {
      approvalLoading.value = false
    }
  }, 400)
})
onUnmounted(() => { if (approvalTimer) clearTimeout(approvalTimer) })
onUnmounted(() => { if (capitalTimer) clearTimeout(capitalTimer) })
onUnmounted(() => { if (typeTimer) clearTimeout(typeTimer) })

function selectNameSuggestion(name: string) {
  customNameActive.value = false
  emit('answer', 'name', name)
}

function selectCustomName() {
  customNameActive.value = true
  const v = customNameInput.value.trim()
  emit('answer', 'name', v)
}

function onCustomNameInput() {
  if (!customNameActive.value) customNameActive.value = true
  emit('answer', 'name', customNameInput.value.trim())
}
// --- end name step state ---

// --- org step state ---
const orgTips = ref('')
const orgTipsLoading = ref(false)

async function loadOrgTips() {
  orgTipsLoading.value = true
  orgTips.value = ''
  try {
    const res = await fetch('/api/org-tips', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ formData: cleanFormData(props.formData) }),
    })
    if (res.ok) orgTips.value = (await res.json()).tips
  } catch { /* ignore */ } finally {
    orgTipsLoading.value = false
  }
}

watch(() => props.step.id, (id) => {
  if (id === 'org' && !orgTips.value) loadOrgTips()
})
// --- end org step state ---

watch(() => props.step.id, () => {
  customInput.value = ''
  customActive.value = false
  expanded.value = new Set()
})

function toggleExpand(label: string, e: Event) {
  e.stopPropagation()
  const s = new Set(expanded.value)
  s.has(label) ? s.delete(label) : s.add(label)
  expanded.value = s
}

function isCustom(label: string) {
  return label.includes('自定义')
}

function select(label: string) {
  if (isCustom(label)) {
    customActive.value = true
    if (customInput.value.trim()) emit('answer', props.step.id, customInput.value.trim())
    else emit('answer', props.step.id, label)
  } else {
    customActive.value = false
    customInput.value = ''
    emit('answer', props.step.id, label)
  }
}

function onCustomInput() {
  if (customInput.value.trim()) emit('answer', props.step.id, customInput.value.trim())
}

const canGoNext = computed(() => {
  if (props.step.id === 'name') {
    if (!namePref.value.trim() || !nameIndustry.value) return false
    if (customNameActive.value) return !!customNameInput.value.trim()
    return !!props.selected
  }
  if (props.step.id === 'type') return !!peopleCount.value && !!shareholderCount.value && !typeLoading.value && !!typeRecommendation.value
  if (props.step.id === 'scope') return !scopeLoading.value && !!scopeRecommendation.value
  if (props.step.id === 'capital') return !!capitalIntention.value && !capitalLoading.value && !!capitalEstimate.value
  if (props.step.id === 'address') return !!addressProvince.value && !addressLoading.value && !!addressRecommendations.value
  if (props.step.id === 'org') return true
  return !!props.selected && !props.optionsLoading
})

function goForward() {
  if (props.step.id === 'name') {
    const chosen = customNameActive.value ? customNameInput.value.trim() : (props.selected || '')
    if (!chosen) return
    emit('answer', 'name', chosen)
    emit('updateFormData', { namePref: namePref.value, business: nameIndustry.value, name: chosen })
    emit('next')
    return
  }

  if (props.step.id === 'type' && typeRecommendation.value) {
    emit('updateFormData', {
      people: peopleCount.value,
      shareholder: shareholderCount.value,
      companyType: typeRecommendation.value.companyType,
    })
    emit('answer', 'type', typeRecommendation.value.companyType)
    emit('next')
    return
  }

  if (props.step.id === 'capital' && capitalEstimate.value) {
    emit('answer', 'capital', formatCapitalAnswer(capitalEstimate.value))
    emit('next')
    return
  }

  if (props.step.id === 'address' && addressRecommendations.value) {
    emit('answer', 'address', formatAddressAnswer(addressRecommendations.value))
    emit('next')
    return
  }

  if (props.step.id === 'org') {
    emit('answer', 'org', '待定')
    emit('next')
    return
  }

  emit('next')
}
</script>

<template>
  <div class="step-wrap">
    <div class="step-card">
      <div class="step-head">
        <div class="step-icon">{{ step.icon }}</div>
        <div>
          <div class="step-counter">步骤 {{ stepIndex + 1 }} / {{ totalSteps }}</div>
          <div class="step-title">{{ step.title }}</div>
        </div>
      </div>

      <div v-if="step.id === 'name'" class="name-step">
        <!-- 公司名称偏好 -->
        <div class="field-group">
          <label class="field-label">公司名称偏好</label>
          <input v-model="namePref" class="input" placeholder="如：星禾云创、智云科技..." @keydown.enter="generateNames" />
        </div>

        <!-- 业务描述（可选） -->
        <div class="field-group">
          <label class="field-label">业务描述 <span class="field-optional">（可选）</span></label>
          <textarea
            v-model="nameDesc"
            class="input textarea"
            placeholder="描述您要从事的业务领域，帮助生成更贴合的名称，例如：面向中小企业的 SaaS 协同办公平台"
          />
          <div class="field-hint">填写越详细，生成的名称越贴合您的业务方向</div>
        </div>

        <!-- 生成按钮 -->
        <div class="generate-row">
          <button class="btn-generate" :disabled="!namePref.trim() || namesLoading" @click="generateNames">
            <span v-if="namesLoading" class="spinner spinner--dark"></span>
            <span v-else class="btn-generate-icon">✨</span>
            {{ suggestedNames.length ? '重新生成' : '生成名称建议' }}
          </button>
        </div>

        <!-- 生成结果 -->
        <div class="field-group">
          <div v-if="namesLoading" class="names-loading"><span class="spinner"></span> 正在生成名称建议...</div>
          <div v-if="suggestedNames.length" class="name-suggestions">
            <button
              v-for="(name, i) in suggestedNames"
              :key="name"
              type="button"
              class="name-option"
              :class="{ selected: !customNameActive && selected === name }"
              @click="selectNameSuggestion(name)"
            >
              <div class="name-option-index">{{ i + 1 }}</div>
              <span class="name-option-label">{{ name }}</span>
              <span v-if="!customNameActive && selected === name" class="check">✓</span>
            </button>

            <button
              type="button"
              class="name-option name-option--custom"
              :class="{ selected: customNameActive }"
              @click="selectCustomName"
            >
              <div class="name-option-index">✎</div>
              <div class="name-option-custom-body">
                <span class="name-option-label">自定义名称</span>
                <input
                  v-model="customNameInput"
                  class="custom-name-input"
                  placeholder="输入您已经取好的公司全称..."
                  @click.stop="selectCustomName"
                  @input="onCustomNameInput"
                />
              </div>
              <span v-if="customNameActive && customNameInput.trim()" class="check">✓</span>
            </button>
          </div>
        </div>

        <!-- 主营业务 -->
        <div class="field-group">
          <label class="field-label">主营业务</label>
          <div class="biz-row">
            <select v-model="nameIndustry" class="input select">
              <option value="">请选择行业分类</option>
              <option v-for="ind in INDUSTRIES" :key="ind" :value="ind">{{ ind }}</option>
            </select>
          </div>
          <div v-if="recommendedBusiness" class="biz-reco">
            <span class="biz-reco-tag">✨ AI 推荐</span>
            <span class="biz-reco-value">{{ recommendedBusiness }}</span>
          </div>
          <div class="field-hint">参考：经营范围、公司类型、注册资本将在后续步骤中根据此信息智能推荐</div>
        </div>

        <!-- 前置/后置审批提示 -->
        <div v-if="approvalLoading" class="approval-banner approval-banner--loading">
          <span class="spinner spinner--dark" style="border-color: rgba(0,0,0,0.15); border-top-color: #d46b08;"></span>
          <span style="font-size:13px;color:#8c6d1f;">正在检查审批要求...</span>
        </div>
        <div v-else-if="approval?.needsApproval" class="approval-banner">
          <div class="banner-left">
            <span class="banner-icon">⚠️</span>
            <div>
              <div class="banner-title">涉及{{ approval.type }}</div>
              <div class="banner-desc">您所选的业务类型需要办理相关审批手续，请提前了解相关要求</div>
            </div>
          </div>
          <button class="btn-detail" @click="showModal = true">查看详情</button>
        </div>
      </div>

      <div v-else-if="step.id === 'type'" class="type-step">
        <div class="type-input-row">
          <div class="field-group">
            <label class="field-label">公司人数</label>
            <div class="pretty-control">
              <input v-model.number="peopleCount" type="number" min="1" class="input pretty-input type-input" placeholder="请输入公司人数" />
              <span class="pretty-suffix">人</span>
            </div>
          </div>
          <div class="field-group">
            <label class="field-label">股东人数</label>
            <div class="pretty-control">
              <input v-model.number="shareholderCount" type="number" min="1" class="input pretty-input type-input" placeholder="请输入股东人数" />
              <span class="pretty-suffix">人</span>
            </div>
          </div>
        </div>

        <div v-if="typeLoading" class="type-loading">
          <span class="spinner"></span>
          正在为您推荐合适的公司类型...
        </div>

        <div v-else-if="typeError" class="type-error">
          <span>{{ typeError }}</span>
          <button class="btn-detail" @click="loadCompanyType">重试</button>
        </div>

        <div v-else-if="typeRecommendation" class="type-result-card">
          <div class="type-result">
            <span class="type-label">推荐公司类型：</span>
            <span class="type-value">{{ typeRecommendation.companyType }}</span>
          </div>
          <div class="type-explanation">{{ typeRecommendation.explanation }}</div>
        </div>

        <div v-else class="type-empty">输入公司人数和股东人数后将自动推荐公司类型</div>
      </div>

      <div v-else-if="step.id === 'scope'" class="scope-step">
        <div class="scope-business">
          <span class="scope-business-label">已选择主营业务</span>
          <span class="scope-business-value">{{ formData.business || '未选择' }}</span>
        </div>

        <div v-if="scopeLoading" class="scope-loading">
          <span class="spinner"></span>
          正在拟定经营范围...
        </div>

        <div v-else-if="scopeError" class="scope-error">
          <span>{{ scopeError }}</span>
          <button class="btn-detail" @click="loadScopeRecommendation">重试</button>
        </div>

        <div v-else-if="scopeRecommendation" class="scope-result">
          <div class="scope-main">
            <span class="scope-tag scope-tag--main">主营业务</span>
            <span class="scope-main-text">{{ scopeRecommendation.main }}</span>
          </div>

          <div class="scope-others">
            <div class="scope-section-title">其他经营范围</div>
            <div class="scope-chip-list">
              <span v-for="item in scopeRecommendation.others" :key="item" class="scope-chip">{{ item }}</span>
            </div>
          </div>
        </div>
      </div>

      <div v-else-if="step.id === 'capital'" class="capital-step">
        <div class="field-group">
          <label class="field-label">意向投资金额</label>
          <div class="capital-input-row pretty-control">
            <input
              v-model.number="capitalIntention"
              type="number"
              min="1"
              class="input pretty-input capital-input"
              placeholder="请输入认缴金额"
            />
            <span class="pretty-suffix capital-unit">万元</span>
          </div>
        </div>

        <div class="capital-tip">新公司法要求五年内完成实缴。</div>

        <div class="capital-estimate">
          <span class="capital-estimate-label">预估注册资本/认缴金额</span>
          <span v-if="capitalLoading" class="capital-estimate-value muted">
            <span class="spinner"></span>
            正在预估...
          </span>
          <span v-else-if="capitalError" class="capital-estimate-value error">{{ capitalError }}</span>
          <span v-else-if="capitalEstimate" class="capital-estimate-value">
            {{ formatMoneyWan(capitalEstimate.estimatedAmount) }}
          </span>
          <span v-else class="capital-estimate-value muted">输入认缴金额后自动显示</span>
        </div>
        <div v-if="capitalEstimate?.explanation" class="capital-explanation">{{ capitalEstimate.explanation }}</div>
      </div>

      <div v-else-if="step.id === 'address'" class="address-step">
        <div class="field-group">
          <label class="field-label">注册地址</label>
          <div class="pretty-control pretty-select-wrap">
            <select v-model="addressProvince" class="input select pretty-input address-select">
              <option value="">请选择省份</option>
              <option v-for="province in PROVINCES" :key="province" :value="province">{{ province }}</option>
            </select>
          </div>
        </div>

        <div class="address-recommend">
          <div class="address-recommend-title">推荐</div>
          <div v-if="addressLoading" class="address-loading">
            <span class="spinner"></span>
            正在生成注册地址建议...
          </div>
          <div v-else-if="addressError" class="address-error">{{ addressError }}</div>
          <div v-else-if="addressRecommendations" class="address-result">
            <div class="address-chip-list">
              <span class="address-chip">{{ addressRecommendations.recommendation }}</span>
            </div>
            <div v-if="addressRecommendations.explanation" class="address-explanation">
              {{ addressRecommendations.explanation }}
            </div>
          </div>
          <div v-else class="address-empty">选择省份后自动显示推荐地址类型</div>
        </div>
      </div>

      <div v-else-if="step.id === 'org'" class="org-step">
        <div class="org-image-wrap">
          <img class="org-image" :src="orgImage" alt="组织架构设计图" />
        </div>
        <div class="org-tips">
          <span class="org-tips-label">Tips: </span>
          <span v-if="orgTipsLoading" class="org-tips-text muted"><span class="spinner"></span> 正在生成建议...</span>
          <span v-else class="org-tips-text">{{ orgTips || '待定' }}</span>
        </div>
      </div>

      <div v-else-if="optionsLoading" class="options-loading">
        <span class="spinner"></span> AI 正在根据您的信息生成选项...
      </div>

      <div v-else class="options-list">
        <button
          v-for="opt in step.options"
          :key="opt.label"
          class="option-card"
          :class="{
            selected: isCustom(opt.label) ? customActive : selected === opt.label,
            recommended: opt.recommended && selected === undefined
          }"
          @click="select(opt.label)"
        >
          <div class="opt-left">
            <div class="opt-top">
              <span class="opt-label">{{ opt.label }}</span>
              <span v-if="opt.recommended" class="rec-badge">推荐</span>
              <span v-if="isCustom(opt.label) ? customActive : selected === opt.label" class="check">✓</span>
            </div>
            <div class="opt-summary">{{ opt.summary }}</div>
            <template v-if="expanded.has(opt.label)">
              <div class="opt-detail">{{ opt.detail }}</div>
            </template>
            <button class="expand-btn" @click.stop="toggleExpand(opt.label, $event)">
              {{ expanded.has(opt.label) ? '收起 ▲' : '查看详情 ▼' }}
            </button>
            <input
              v-if="isCustom(opt.label) && customActive"
              v-model="customInput"
              class="custom-input"
              placeholder="请输入自定义内容..."
              @click.stop
              @input="onCustomInput"
            />
          </div>
        </button>
      </div>
    </div>

    <div class="nav-bar">
      <button class="btn-ghost" @click="emit('prev')">
      ← {{ stepIndex === 0 ? '返回' : '上一步' }}
      </button>
      <div class="nav-center">
        <span v-if="step.id === 'type'" class="selected-hint">{{ typeRecommendation ? `已选：${typeRecommendation.companyType}` : '请输入公司人数和股东人数' }}</span>
        <span v-else-if="step.id === 'org'" class="selected-hint"></span>
        <span v-else-if="step.id === 'name'">
          <span v-if="customNameActive && customNameInput.trim()" class="selected-hint">已选：{{ customNameInput.trim() }}</span>
          <span v-else-if="!customNameActive && selected" class="selected-hint">已选：{{ selected }}</span>
          <span v-else-if="!namePref.trim() || !nameIndustry" class="selected-hint muted">请填写名称偏好并选择主营业务</span>
          <span v-else class="selected-hint muted">请选择一个 AI 推荐名称，或输入自定义名称</span>
        </span>
        <span v-else-if="step.id === 'scope'" class="selected-hint">
          <span v-if="scopeRecommendation">已选主营：{{ scopeRecommendation.main }}</span>
          <span v-else class="muted">正在拟定经营范围...</span>
        </span>
        <span v-else-if="selected" class="selected-hint">已选：{{ selected }}</span>
        <span v-else class="selected-hint muted">请选择一个选项</span>
      </div>
      <button
        class="btn-primary"
        :disabled="!canGoNext"
        @click="goForward"
      >
        {{ step.id === 'org' ? '生成个性化建议及完整流程' : (isLast ? '完成注册方案 🎉' : '下一步 →') }}
      </button>
    </div>
  </div>

  <Teleport to="body">
    <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
      <div class="modal">
        <div class="modal-head">
          <span>{{ approval?.type }}说明</span>
          <button class="modal-close" @click="showModal = false">✕</button>
        </div>
        <div class="modal-body">{{ approval?.details }}</div>
        <div class="modal-footer">
          <button class="btn-primary" @click="showModal = false">我已了解</button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.options-loading {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 13px;
  color: var(--text-secondary);
  padding: 32px 0;
  justify-content: center;
}
.spinner {
  width: 14px;
  height: 14px;
  border: 2px solid var(--border);
  border-top-color: var(--primary);
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
  flex-shrink: 0;
}
@keyframes spin { to { transform: rotate(360deg); } }

.step-wrap { display: flex; flex-direction: column; gap: 16px; width: 100%; max-width: 1280px; margin: 0 auto; }

.step-card {
  background: white;
  border-radius: var(--radius);
  border: 1px solid var(--border-light);
  box-shadow: var(--shadow);
  padding: 28px;
}
.step-head {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
  padding-bottom: 20px;
  border-bottom: 1px solid var(--border-light);
}
.step-icon { font-size: 36px; }
.step-counter { font-size: 12px; color: var(--text-secondary); margin-bottom: 4px; }
.step-title { font-size: 20px; font-weight: 700; color: var(--text); }

.options-list { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; }
@media (max-width: 700px) { .options-list { grid-template-columns: 1fr; } }
.option-card {
  background: white;
  border: 2px solid var(--border-light);
  border-radius: 10px;
  padding: 18px 20px;
  text-align: left;
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
}
.option-card:hover { border-color: var(--primary); box-shadow: 0 2px 8px rgba(22,119,255,0.1); }
.option-card.recommended { border-color: #91caff; background: #f0f7ff; }
.option-card.selected { border-color: var(--primary); background: #e6f4ff; box-shadow: 0 0 0 3px rgba(22,119,255,0.1); }

.opt-top { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }
.opt-label { font-size: 14px; font-weight: 600; color: var(--text); flex: 1; }
.rec-badge {
  font-size: 11px;
  background: #fff7e6;
  color: #d46b08;
  border: 1px solid #ffd591;
  padding: 1px 7px;
  border-radius: 10px;
  font-weight: 500;
}
.check {
  width: 20px; height: 20px;
  background: var(--primary);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 700;
  flex-shrink: 0;
}
.opt-summary { font-size: 12px; color: var(--text-secondary); margin-top: 4px; }
.opt-detail { font-size: 12px; color: var(--text-secondary); line-height: 1.6; margin-top: 6px; padding-top: 6px; border-top: 1px solid var(--border-light); }
.expand-btn {
  background: none;
  border: none;
  padding: 2px 0;
  margin-top: 4px;
  font-size: 12px;
  color: var(--primary);
  cursor: pointer;
  display: block;
}
.custom-input {
  margin-top: 10px;
  width: 100%;
  height: 34px;
  padding: 0 10px;
  border: 1px solid var(--primary);
  border-radius: 6px;
  font-size: 13px;
  color: var(--text);
  outline: none;
  background: white;
  box-shadow: 0 0 0 2px rgba(22,119,255,0.1);
}

.nav-bar {
  background: white;
  border-radius: var(--radius);
  border: 1px solid var(--border-light);
  padding: 16px 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: var(--shadow);
}
.nav-center { flex: 1; text-align: center; }
.selected-hint { font-size: 13px; color: var(--text); }
.selected-hint.muted { color: var(--text-secondary); }

.btn-ghost {
  background: none;
  border: 1px solid var(--border);
  color: var(--text-secondary);
  padding: 0 18px;
  height: 36px;
  border-radius: 6px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}
.btn-ghost:hover { border-color: var(--primary); color: var(--primary); }

.btn-primary {
  background: linear-gradient(135deg, #1677ff, #4096ff);
  color: white;
  border: none;
  padding: 0 24px;
  height: 36px;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
  box-shadow: 0 2px 6px rgba(22,119,255,0.25);
}
.btn-primary:hover:not(:disabled) { transform: translateY(-1px); box-shadow: 0 4px 10px rgba(22,119,255,0.35); }
.btn-primary:disabled { opacity: 0.4; cursor: not-allowed; transform: none; }

.pretty-control {
  display: inline-flex;
  align-items: center;
  width: min(360px, 100%);
  min-height: 50px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: white;
  box-shadow: 0 1px 2px rgba(0,0,0,0.03);
  transition: border-color 0.2s, box-shadow 0.2s, background 0.2s;
}
.pretty-control:focus-within {
  border-color: var(--primary);
  background: white;
  box-shadow: 0 0 0 3px rgba(22,119,255,0.12);
}
.input.pretty-input {
  flex: 1;
  width: 100%;
  min-width: 0;
  height: 48px;
  padding: 0 16px;
  border: none;
  border-radius: 8px;
  background: transparent;
  box-shadow: none;
  font-size: 16px;
  font-weight: 700;
  color: var(--text);
}
.input.pretty-input:focus {
  border-color: transparent;
  box-shadow: none;
}
.input.pretty-input::placeholder {
  color: rgba(0,0,0,0.32);
  font-weight: 500;
}
.pretty-suffix {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  align-self: stretch;
  min-width: 56px;
  padding: 0 14px;
  border-left: 1px solid var(--border-light);
  color: var(--text-secondary);
  background: #fafafa;
  font-size: 13px;
  font-weight: 800;
}
.pretty-select-wrap {
  position: relative;
}
.pretty-select-wrap::after {
  content: '';
  position: absolute;
  right: 16px;
  top: 50%;
  width: 8px;
  height: 8px;
  border-right: 2px solid var(--primary);
  border-bottom: 2px solid var(--primary);
  pointer-events: none;
  transform: translateY(-65%) rotate(45deg);
}

/* type step */
.type-step { display: flex; flex-direction: column; gap: 20px; }
.type-input-row {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}
.type-input-row .field-group { flex: 1; min-width: 240px; }
.type-loading,
.type-error,
.type-empty {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  min-height: 96px;
  color: var(--text-secondary);
  font-size: 13px;
  border: 1px dashed var(--border);
  border-radius: 8px;
  background: #fafafa;
}
.type-error { justify-content: space-between; padding: 0 16px; color: var(--error); }
.type-result-card {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 18px;
  border: 1px solid #91caff;
  border-radius: 8px;
  background: #f0f7ff;
}
.type-result { display: flex; align-items: center; gap: 8px; }
.type-label { font-size: 13px; color: var(--text-secondary); }
.type-value { font-size: 18px; font-weight: 800; color: var(--primary); }
.type-hint { font-size: 12px; color: var(--text-secondary); }
.type-explanation {
  font-size: 13px;
  line-height: 1.7;
  color: var(--text);
  white-space: pre-line;
}

/* scope step */
.scope-step { display: flex; flex-direction: column; gap: 18px; }
.scope-business {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 14px;
  background: #f5f7fa;
  border: 1px solid var(--border-light);
  border-radius: 8px;
}
.scope-business-label {
  font-size: 12px;
  color: var(--text-secondary);
  white-space: nowrap;
}
.scope-business-value {
  font-size: 14px;
  font-weight: 700;
  color: var(--text);
}
.scope-loading,
.scope-error {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  min-height: 132px;
  color: var(--text-secondary);
  font-size: 13px;
  border: 1px dashed var(--border);
  border-radius: 8px;
  background: #fafafa;
}
.scope-error { justify-content: space-between; min-height: 64px; padding: 0 16px; color: var(--error); }
.scope-result {
  display: grid;
  gap: 14px;
}
.scope-main,
.scope-others {
  border: 1px solid var(--border-light);
  border-radius: 8px;
  background: white;
}
.scope-main {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 18px;
  border-color: #91caff;
  background: #f0f7ff;
}
.scope-tag {
  display: inline-flex;
  align-items: center;
  height: 24px;
  padding: 0 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
  white-space: nowrap;
}
.scope-tag--main {
  color: var(--primary);
  background: white;
  border: 1px solid #91caff;
}
.scope-main-text {
  font-size: 20px;
  font-weight: 800;
  color: var(--primary);
}
.scope-others {
  padding: 16px 18px 18px;
}
.scope-section-title {
  font-size: 13px;
  font-weight: 700;
  color: var(--text);
  margin-bottom: 12px;
}
.scope-chip-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}
.scope-chip {
  display: inline-flex;
  align-items: center;
  min-height: 34px;
  padding: 6px 12px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: #fafafa;
  color: var(--text);
  font-size: 13px;
  font-weight: 600;
}

/* capital step */
.capital-step { display: flex; flex-direction: column; gap: 18px; }
.capital-input-row {
  width: min(360px, 100%);
}
.input.capital-input {
  flex: 1;
}
.capital-unit {
  color: var(--primary);
}
.capital-explanation {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.7;
  padding: 12px 14px;
  border: 1px solid var(--border-light);
  border-radius: 8px;
  background: #fafafa;
  white-space: pre-line;
}
.capital-tip {
  padding: 12px 14px;
  border: 1px solid #ffe58f;
  border-radius: 8px;
  background: #fffbe6;
  color: #8c6d1f;
  font-size: 13px;
  font-weight: 600;
}
.capital-estimate {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  padding: 18px;
  border: 1px solid #91caff;
  border-radius: 8px;
  background: #f0f7ff;
}
.capital-estimate-label {
  color: var(--text-secondary);
  font-size: 13px;
  font-weight: 600;
}
.capital-estimate-value {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: var(--primary);
  font-size: 22px;
  font-weight: 800;
  text-align: right;
}
.capital-estimate-value.muted {
  color: var(--text-secondary);
  font-size: 13px;
  font-weight: 500;
}
.capital-estimate-value.error {
  color: var(--error);
  font-size: 13px;
  font-weight: 600;
}

/* address step */
.address-step { display: flex; flex-direction: column; gap: 18px; }
.input.address-select {
  height: 48px;
  padding-right: 44px;
  font-weight: 700;
  background-image: none;
}
.address-recommend {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  min-height: 56px;
  padding: 14px;
  border: 1px solid #91caff;
  border-radius: 8px;
  background: #f0f7ff;
}
.address-recommend-title {
  color: var(--text-secondary);
  font-size: 13px;
  font-weight: 700;
  white-space: nowrap;
  padding-top: 8px;
}
.address-loading,
.address-empty,
.address-error {
  display: flex;
  align-items: center;
  gap: 8px;
  min-height: 34px;
  color: var(--text-secondary);
  font-size: 13px;
}
.address-error { color: var(--error); font-weight: 600; }
.address-chip-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  min-width: 0;
}
.address-result {
  display: flex;
  flex-direction: column;
  gap: 8px;
  flex: 1;
  min-width: 0;
}
.address-explanation {
  font-size: 12px;
  color: var(--text-secondary);
  line-height: 1.6;
  white-space: pre-line;
}
.address-chip {
  display: inline-flex;
  align-items: center;
  min-height: 36px;
  padding: 7px 12px;
  border: 1px solid #91caff;
  border-radius: 8px;
  background: white;
  color: var(--primary);
  font-size: 13px;
  font-weight: 700;
}

/* org step */
.org-step { display: flex; flex-direction: column; gap: 16px; }
.org-image-wrap {
  overflow: hidden;
  border: 1px solid var(--border-light);
  border-radius: 8px;
  background: #fafafa;
}
.org-image {
  display: block;
  width: 100%;
  max-height: 460px;
  object-fit: contain;
  background: white;
}
.org-tips {
  display: flex;
  align-items: flex-start;
  gap: 6px;
  padding: 12px 14px;
  border: 1px solid #ffe58f;
  border-radius: 8px;
  background: #fffbe6;
}
.org-tips-label {
  color: #8c6d1f;
  font-size: 13px;
  font-weight: 800;
  white-space: nowrap;
  flex-shrink: 0;
}
.org-tips-text {
  color: var(--text);
  font-size: 13px;
  font-weight: 600;
  line-height: 1.6;
}
.org-tips-text.muted { color: var(--text-secondary); font-weight: 400; }

/* name step */
.name-step { display: flex; flex-direction: column; gap: 22px; }
.field-group { display: flex; flex-direction: column; gap: 8px; }
.field-label {
  font-size: 13px;
  font-weight: 600;
  color: var(--text);
  letter-spacing: 0.2px;
}
.field-optional { font-size: 12px; color: var(--text-secondary); font-weight: 400; margin-left: 2px; }
.field-hint { font-size: 12px; color: var(--text-secondary); margin-top: 2px; }
.name-step .input {
  width: 100%;
  flex: none;
  height: 44px;
  padding: 0 14px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: #fafbfc;
  font-size: 14px;
  color: var(--text);
  transition: border-color 0.2s, box-shadow 0.2s, background 0.2s;
}
.name-step .input::placeholder {
  color: rgba(0,0,0,0.32);
}
.name-step .input:hover {
  border-color: #b0b8c4;
  background: white;
}
.name-step .input:focus {
  border-color: var(--primary);
  background: white;
  box-shadow: 0 0 0 3px rgba(22,119,255,0.12);
}
.name-step .textarea {
  height: auto;
  min-height: 92px;
  padding: 12px 14px;
  line-height: 1.65;
  resize: vertical;
  font-size: 13px;
}
.name-row, .biz-row { display: flex; gap: 8px; }
.biz-reco {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 8px;
  padding: 8px 12px;
  background: #f0f7ff;
  border: 1px solid #91caff;
  border-radius: 8px;
}
.biz-reco-tag {
  flex-shrink: 0;
  font-size: 12px;
  font-weight: 600;
  color: var(--primary);
}
.biz-reco-value { font-size: 13px; font-weight: 600; color: var(--text); }
.generate-row {
  display: flex;
  justify-content: flex-end;
}
.btn-generate {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 0 22px;
  height: 40px;
  background: var(--primary);
  color: white;
  border: 1px solid var(--primary);
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
  box-shadow: 0 2px 6px rgba(22,119,255,0.25);
  transition: background 0.2s, box-shadow 0.2s, transform 0.1s;
}
.btn-generate:hover:not(:disabled) {
  background: #4096ff;
  box-shadow: 0 4px 12px rgba(22,119,255,0.35);
}
.btn-generate:active:not(:disabled) {
  transform: translateY(1px);
  box-shadow: 0 1px 3px rgba(22,119,255,0.25);
}
.btn-generate:disabled {
  background: #fafbfc;
  color: var(--text-secondary);
  border-color: var(--border);
  box-shadow: none;
  cursor: not-allowed;
}
.btn-generate-icon { font-size: 14px; }
.input {
  flex: 1;
  height: 36px;
  padding: 0 12px;
  border: 1px solid var(--border);
  border-radius: 6px;
  font-size: 14px;
  color: var(--text);
  background: white;
  outline: none;
  transition: border-color 0.2s;
}
.input:focus { border-color: var(--primary); box-shadow: 0 0 0 2px rgba(22,119,255,0.15); }
.input.type-input {
  flex: 1;
}
.select {
  cursor: pointer;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%23999' d='M6 8L1 3h10z'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 12px center;
  padding-right: 32px;
}
.names-loading { display: flex; align-items: center; gap: 8px; font-size: 12px; color: var(--text-secondary); }
.name-suggestions {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
  margin-top: 4px;
}
.name-option {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  background: white;
  border: 2px solid var(--border-light);
  border-radius: 10px;
  cursor: pointer;
  text-align: left;
  transition: border-color 0.2s;
  width: 100%;
  position: relative;
  isolation: isolate;
}
.name-option:hover { border-color: #91caff; }
.name-option.selected {
  border-color: var(--primary);
  background: #f0f7ff;
  box-shadow: 0 0 0 3px rgba(22,119,255,0.1);
}
.name-option-index {
  width: 24px; height: 24px;
  border-radius: 50%;
  background: #f0f2f5;
  color: var(--text-secondary);
  font-size: 12px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.name-option.selected .name-option-index { background: var(--primary); color: white; }
.name-option-label { flex: 1; font-size: 15px; font-weight: 600; color: var(--text); }
.name-option--custom { grid-column: 1 / -1; align-items: stretch; padding: 12px 16px; }
.name-option--custom .name-option-index { font-size: 13px; }
.name-option-custom-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 6px;
  min-width: 0;
}
.name-option-custom-body .name-option-label { font-size: 14px; }
.custom-name-input {
  width: 100%;
  height: 36px;
  padding: 0 12px;
  border: 1px solid var(--border);
  border-radius: 6px;
  font-size: 14px;
  color: var(--text);
  background: white;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
}
.custom-name-input:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 2px rgba(22,119,255,0.15);
}
.name-option--custom.selected .custom-name-input {
  border-color: var(--primary);
}
.name-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  border: 2px solid var(--border-light);
  border-radius: 20px;
  background: white;
  font-size: 13px;
  color: var(--text);
  cursor: pointer;
  transition: all 0.2s;
}
.name-chip:hover { border-color: var(--primary); color: var(--primary); }
.name-chip.selected { border-color: var(--primary); background: #e6f4ff; color: var(--primary); font-weight: 600; }
.chip-check {
  width: 16px; height: 16px;
  background: var(--primary);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  font-weight: 700;
}
.approval-banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  background: #fffbe6;
  border: 1px solid #ffe58f;
  border-radius: 8px;
  padding: 14px 16px;
}
.banner-left { display: flex; align-items: flex-start; gap: 10px; }
.banner-icon { font-size: 18px; flex-shrink: 0; }
.banner-title { font-size: 13px; font-weight: 600; color: #d46b08; }
.banner-desc { font-size: 12px; color: #8c6d1f; margin-top: 2px; }
.approval-banner--loading {
  gap: 10px;
  justify-content: flex-start;
}
.btn-detail {
  padding: 5px 14px;
  border: 1px solid #ffa940;
  border-radius: 6px;
  background: white;
  color: #d46b08;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  white-space: nowrap;
  flex-shrink: 0;
}
.btn-detail:hover { background: #fff7e6; }
.spinner--dark { border-color: rgba(255,255,255,0.4); border-top-color: white; }

/* modal */
.modal-overlay {
  position: fixed; inset: 0;
  background: rgba(0,0,0,0.45);
  display: flex; align-items: center; justify-content: center;
  z-index: 1000;
}
.modal {
  background: white; border-radius: 12px;
  width: 480px; max-width: 90vw;
  box-shadow: 0 20px 60px rgba(0,0,0,0.2);
}
.modal-head {
  display: flex; justify-content: space-between; align-items: center;
  padding: 18px 24px;
  border-bottom: 1px solid var(--border-light);
  font-size: 15px; font-weight: 700; color: var(--text);
}
.modal-close { background: none; border: none; font-size: 16px; color: var(--text-secondary); cursor: pointer; padding: 2px 6px; border-radius: 4px; }
.modal-close:hover { background: #f5f5f5; }
.modal-body { padding: 20px 24px; font-size: 13px; color: var(--text-secondary); line-height: 1.8; white-space: pre-line; max-height: 60vh; overflow-y: auto; }
.modal-footer { padding: 16px 24px; border-top: 1px solid var(--border-light); display: flex; justify-content: flex-end; }
</style>
