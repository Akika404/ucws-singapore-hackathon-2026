<script setup lang="ts">
import { ref, computed, reactive, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { sharedFormData } from '../store'

const { t, tm, locale } = useI18n()

/* ---------------- 基础配置 ---------------- */

// 行业（PolicyEngine 自有 9 项，与 A~T 不对齐）；仅展示，逻辑用 industryIdx
const industries = computed(() => tm('policy.industries') as string[])

const PROVINCE_IDS = ['shanghai', 'beijing', 'guangdong', 'zhejiang', 'other']
const provinceLabel = (id: string) => t('policy.provinces.' + id)

// 政策类别：id 语言无关（all/funding/tax/space/loan/talent），显示走 t()
type CategoryKey = 'all' | 'funding' | 'tax' | 'space' | 'loan' | 'talent'

interface CategoryStyle {
  hex: string
  light: string
  border: string
}

const policyCategories: Record<CategoryKey, CategoryStyle> = {
  all:     { hex: '#475569', light: '#f1f5f9', border: '#cbd5e1' },
  funding: { hex: '#e11d48', light: '#fff1f2', border: '#fecdd3' },
  tax:     { hex: '#059669', light: '#ecfdf5', border: '#a7f3d0' },
  space:   { hex: '#0891b2', light: '#ecfeff', border: '#a5f3fc' },
  loan:    { hex: '#1677ff', light: '#e6f4ff', border: '#91caff' },
  talent:  { hex: '#7c3aed', light: '#f5f3ff', border: '#ddd6fe' },
}
const categoryKeys = Object.keys(policyCategories) as CategoryKey[]
const categoryLabel = (id: CategoryKey) => t('policy.categories.' + id)

type Priority = 'P0' | 'P1' | 'P2'
const priorityStyles: Record<Priority, { weight: number; color: string; bg: string; border: string }> = {
  P0: { weight: 3, color: '#b91c1c', bg: '#fef2f2', border: '#fecaca' },
  P1: { weight: 2, color: '#c2410c', bg: '#fff7ed', border: '#fed7aa' },
  P2: { weight: 1, color: '#475569', bg: '#f8fafc', border: '#e2e8f0' },
}
const priorityLabel = (p: Priority) => t('policy.priority.' + p)

// 政策记录：仅保留逻辑/数值字段；展示字段（title/desc/department/cycle/valueUnit/字符串型 maxValue）按 id 查 t('policy.db.<id>.*')
interface PolicyDef {
  id: string
  category: Exclude<CategoryKey, 'all'>
  maxValue: number | 'maxValue'  // 数字→直接展示；'maxValue'→查 t('policy.db.<id>.maxValue')
  typeValue: number
  prob: number
  deadlineDays: number
  priority: Priority
  reqProv: string
  reqSizeMin: number
  reqCapMin: number
  reqInd: 'all' | number[]
}

const policyDatabase: PolicyDef[] = [
  { id: 'P-FUND-01', category: 'funding', maxValue: 8000, typeValue: 8000, prob: 95, deadlineDays: 120, priority: 'P1', reqProv: 'shanghai', reqSizeMin: 1, reqCapMin: 0, reqInd: 'all' },
  { id: 'P-FUND-02', category: 'funding', maxValue: 50000, typeValue: 50000, prob: 99, deadlineDays: 15, priority: 'P0', reqProv: 'all', reqSizeMin: 15, reqCapMin: 0, reqInd: 'all' },
  { id: 'P-SPACE-01', category: 'space', maxValue: 30000, typeValue: 30000, prob: 80, deadlineDays: 60, priority: 'P1', reqProv: 'all', reqSizeMin: 1, reqCapMin: 0, reqInd: 'all' },
  { id: 'P-LOAN-01', category: 'loan', maxValue: 3000000, typeValue: 300000, prob: 65, deadlineDays: 365, priority: 'P2', reqProv: 'all', reqSizeMin: 1, reqCapMin: 0, reqInd: 'all' },
  { id: 'P-TAX-01', category: 'tax', maxValue: 'maxValue', typeValue: 150000, prob: 100, deadlineDays: 45, priority: 'P1', reqProv: 'all', reqSizeMin: 1, reqCapMin: 0, reqInd: 'all' },
  { id: 'P-TAX-02', category: 'tax', maxValue: 'maxValue', typeValue: 200000, prob: 90, deadlineDays: 365, priority: 'P2', reqProv: 'shanghai', reqSizeMin: 1, reqCapMin: 0, reqInd: 'all' },
  { id: 'P-TALENT-01', category: 'talent', maxValue: 'maxValue', typeValue: 0, prob: 50, deadlineDays: 20, priority: 'P0', reqProv: 'shanghai', reqSizeMin: 5, reqCapMin: 100, reqInd: [0, 1, 2] },
]

// 展示字段访问器（按 id）
const pTitle = (p: PolicyDef) => t(`policy.db.${p.id}.title`)
const pDesc = (p: PolicyDef) => t(`policy.db.${p.id}.desc`)
const pDept = (p: PolicyDef) => t(`policy.db.${p.id}.department`)
const pCycle = (p: PolicyDef) => t(`policy.db.${p.id}.cycle`)
const pUnit = (p: PolicyDef) => t(`policy.db.${p.id}.unit`)

/* ---------------- 表单状态 + 联动 ---------------- */

const formState = reactive({
  industryIdx: 0,
  province: 'shanghai',
  namePref: '星禾云创',
  teamSize: 25,
  capital: 150,
})

const overridden = reactive<Record<keyof typeof formState, boolean>>({
  industryIdx: false, province: false, namePref: false, teamSize: false, capital: false,
})

// 行业匹配（自有 9 项）：优先 (A)~(T) 字母前缀映射，再退回中英文关键词扫描
const LETTER_TO_IDX: Record<string, number> = { I: 0, M: 1, C: 2, F: 3, H: 4, J: 5, E: 6, R: 7 }
function matchIndustryIdx(text: string): number {
  if (!text) return 0
  const letter = text.match(/\(([A-T])\)/i)?.[1]?.toUpperCase()
  if (letter) return LETTER_TO_IDX[letter] ?? 8
  const lower = text.toLowerCase()
  const map: { kws: string[]; idx: number }[] = [
    { kws: ['软件', '互联网', 'saas', 'it', '信息', '科技', '数字', 'software', 'information'], idx: 0 },
    { kws: ['科研', '研究', '技术服务', 'research', 'technical'], idx: 1 },
    { kws: ['制造', '工厂', 'manufactur'], idx: 2 },
    { kws: ['批发', '零售', '电商', 'wholesale', 'retail'], idx: 3 },
    { kws: ['餐饮', '酒店', '住宿', 'catering', 'accommodation'], idx: 4 },
    { kws: ['金融', '银行', '保险', '证券', 'finance'], idx: 5 },
    { kws: ['建筑', '工程', 'construction'], idx: 6 },
    { kws: ['文化', '体育', '娱乐', 'culture', 'sports', 'entertainment'], idx: 7 },
  ]
  for (const a of map) if (a.kws.some(k => lower.includes(k.toLowerCase()))) return a.idx
  return 8
}

// 省份匹配：返回 id，中英文皆可识别
function matchProvince(addr: string): string {
  if (!addr) return 'other'
  const s = addr.toLowerCase()
  if (addr.includes('北京') || s.includes('beijing')) return 'beijing'
  if (addr.includes('上海') || s.includes('shanghai')) return 'shanghai'
  if (addr.includes('广东') || addr.includes('深圳') || addr.includes('广州') || s.includes('guangdong') || s.includes('shenzhen') || s.includes('guangzhou')) return 'guangdong'
  if (addr.includes('浙江') || addr.includes('杭州') || addr.includes('宁波') || s.includes('zhejiang') || s.includes('hangzhou') || s.includes('ningbo')) return 'zhejiang'
  return 'other'
}

function parseCapital(c: string): number {
  if (!c) return 150
  const m = c.match(/(\d+(\.\d+)?)/)
  return m ? Math.round(parseFloat(m[1])) : 150
}

const isLinked = computed(() => !!sharedFormData.value)

const linkedFields = computed(() => {
  const f = sharedFormData.value
  if (!f) return [] as string[]
  const arr: string[] = []
  if (f.business && !overridden.industryIdx) arr.push(t('policy.fieldTags.industry'))
  if (f.address && !overridden.province) arr.push(t('policy.fieldTags.province'))
  if (f.namePref && !overridden.namePref) arr.push(t('policy.fieldTags.namePref'))
  if (typeof f.people === 'number' && f.people > 0 && !overridden.teamSize) arr.push(t('policy.fieldTags.teamSize'))
  if (f.capital && !overridden.capital) arr.push(t('policy.fieldTags.capital'))
  return arr
})

function applyFromShared() {
  const f = sharedFormData.value
  if (!f) return
  if (f.business && !overridden.industryIdx) formState.industryIdx = matchIndustryIdx(f.business)
  if (f.address && !overridden.province) formState.province = matchProvince(f.address)
  if (f.namePref && !overridden.namePref) formState.namePref = f.namePref
  if (typeof f.people === 'number' && f.people > 0 && !overridden.teamSize) formState.teamSize = f.people
  if (f.capital && !overridden.capital) formState.capital = parseCapital(f.capital)
}

watch(() => sharedFormData.value, applyFromShared, { deep: true, immediate: true })

function markOverride(field: keyof typeof formState) { overridden[field] = true }
function resetLink() {
  ;(Object.keys(overridden) as (keyof typeof formState)[]).forEach(k => (overridden[k] = false))
  applyFromShared()
}

/* 输入区默认隐藏（已联动时） */
const setupVisible = ref(false)
watch(isLinked, v => { setupVisible.value = !v }, { immediate: true })

/* ---------------- 政策引擎 ---------------- */

const currentCategory = ref<CategoryKey>('all')
type PriorityFilter = 'ALL' | Priority
const currentPriority = ref<PriorityFilter>('ALL')
type SortMethod = 'priority' | 'amountDesc' | 'probDesc' | 'deadlineAsc'
const currentSort = ref<SortMethod>('priority')

interface MatchedPolicy extends PolicyDef {
  reasons: string[]
}

const matchedPolicies = computed<MatchedPolicy[]>(() => {
  const { industryIdx, province, teamSize, capital } = formState
  const industryName = industries.value[industryIdx] ?? ''

  const list: MatchedPolicy[] = []
  policyDatabase.forEach(policy => {
    if (policy.reqProv !== 'all' && policy.reqProv !== province) return
    if (teamSize < policy.reqSizeMin) return
    if (capital < policy.reqCapMin) return
    if (policy.reqInd !== 'all' && !policy.reqInd.includes(industryIdx)) return
    if (currentCategory.value !== 'all' && policy.category !== currentCategory.value) return
    if (currentPriority.value !== 'ALL' && policy.priority !== currentPriority.value) return

    const reasons: string[] = []
    if (policy.reqProv !== 'all') reasons.push(t('policy.reasons.local', { province: provinceLabel(province) }))
    if (policy.reqSizeMin > 1)    reasons.push(t('policy.reasons.size', { teamSize, min: policy.reqSizeMin }))
    if (policy.reqCapMin > 0)     reasons.push(t('policy.reasons.capital', { capital, min: policy.reqCapMin }))
    if (policy.reqInd !== 'all')  reasons.push(t('policy.reasons.industry', { industry: industryName }))
    if (reasons.length === 0)     reasons.push(t('policy.reasons.universal'))

    list.push({ ...policy, reasons })
  })

  list.sort((a, b) => {
    switch (currentSort.value) {
      case 'priority':    return priorityStyles[b.priority].weight - priorityStyles[a.priority].weight
      case 'amountDesc':  return (b.typeValue || 0) - (a.typeValue || 0)
      case 'probDesc':    return b.prob - a.prob
      case 'deadlineAsc': return a.deadlineDays - b.deadlineDays
    }
  })

  return list
})

const matchedSum = computed(() =>
  matchedPolicies.value.reduce((s, p) => s + (typeof p.typeValue === 'number' ? p.typeValue : 0), 0),
)
const localeTag = computed(() => (locale.value === 'zh' ? 'zh-CN' : 'en-US'))

const previewName = computed(() => t('policy.previewName', { name: formState.namePref || t('policy.unnamed') }))

function setCategory(c: CategoryKey) { currentCategory.value = c }

function formatValue(p: PolicyDef): { prefix: string; value: string } {
  if (typeof p.maxValue === 'number') {
    return { prefix: t('policy.card.maxPrefix'), value: `¥ ${p.maxValue.toLocaleString(localeTag.value)}` }
  }
  return { prefix: '', value: t(`policy.db.${p.id}.maxValue`) }
}

function probColor(prob: number): string {
  if (prob >= 80) return '#059669'
  if (prob >= 50) return '#d97706'
  return '#dc2626'
}

function deadlineColor(days: number): string {
  return days <= 30 ? '#dc2626' : '#334155'
}
</script>

<template>
  <div class="pol-root">
    <!-- 顶部联动状态条 -->
    <div class="link-bar" :class="{ linked: isLinked && linkedFields.length }">
      <div class="link-left">
        <span class="dot" />
        <template v-if="isLinked && linkedFields.length">
          <span class="link-title">{{ t('policy.link.syncedTitle') }}</span>
          <span class="link-fields">{{ t('policy.link.syncedFields', { fields: linkedFields.join(' / ') }) }}</span>
        </template>
        <template v-else>
          <span class="link-title">{{ t('policy.link.notDetected') }}</span>
          <span class="link-fields">{{ t('policy.link.manualHint') }}</span>
        </template>
      </div>
      <button v-if="isLinked" class="link-reset" @click="resetLink">{{ t('policy.link.resync') }}</button>
    </div>

    <!-- 沙盘参数（已联动则默认隐藏） -->
    <div v-show="setupVisible" class="card setup-card">
      <div class="card-header">
        <div>
          <span class="step-chip">{{ t('policy.setup.stepChip') }}</span>
          <h3 class="setup-title">{{ t('policy.setup.title') }}</h3>
          <p class="setup-sub">{{ t('policy.setup.sub') }}</p>
        </div>
        <span class="ai-badge">{{ t('policy.setup.badge') }}</span>
      </div>

      <div class="setup-grid">
        <div class="field col-2">
          <label>{{ t('policy.setup.industry') }}</label>
          <select v-model.number="formState.industryIdx" @change="markOverride('industryIdx')" class="input">
            <option v-for="(name, i) in industries" :key="i" :value="i">{{ name }}</option>
          </select>
        </div>

        <div class="field">
          <label>{{ t('policy.setup.location') }}</label>
          <select v-model="formState.province" @change="markOverride('province')" class="input">
            <option v-for="p in PROVINCE_IDS" :key="p" :value="p">{{ provinceLabel(p) }}</option>
          </select>
        </div>

        <div class="field">
          <label>{{ t('policy.setup.name') }}</label>
          <input class="input" v-model="formState.namePref" @input="markOverride('namePref')" />
        </div>

        <div class="field">
          <label>{{ t('policy.setup.teamSize') }}</label>
          <div class="num-box">
            <input type="number" min="1" v-model.number="formState.teamSize" @input="markOverride('teamSize')" />
            <span class="unit">{{ t('policy.setup.peopleUnit') }}</span>
          </div>
        </div>

        <div class="field">
          <label>{{ t('policy.setup.capital') }}</label>
          <div class="num-box">
            <input type="number" min="1" v-model.number="formState.capital" @input="markOverride('capital')" />
            <span class="unit">{{ t('policy.setup.wanUnit') }}</span>
          </div>
        </div>

        <div class="field col-2 ready-strip">
          <span class="ready-text">{{ t('policy.setup.readyText') }}</span>
          <span class="ready-pulse"><span /><span /><span /></span>
        </div>
      </div>
    </div>

    <!-- 总览看板 -->
    <div class="summary-card">
      <div class="sum-left">
        <div class="sum-name">
          <span class="sum-title">{{ previewName }}</span>
          <button class="eye-btn" @click="setupVisible = !setupVisible" :title="setupVisible ? t('policy.summary.collapse') : t('policy.summary.expand')">
            <svg v-if="!setupVisible" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
              <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8S1 12 1 12z" />
              <circle cx="12" cy="12" r="3" />
            </svg>
            <svg v-else viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
              <path d="M17.94 17.94A10.94 10.94 0 0 1 12 20c-7 0-11-8-11-8a19.6 19.6 0 0 1 5.06-5.94" />
              <path d="M9.9 4.24A10.94 10.94 0 0 1 12 4c7 0 11 8 11 8a19.6 19.6 0 0 1-2.16 3.19" />
              <path d="M14.12 14.12a3 3 0 1 1-4.24-4.24" />
              <line x1="1" y1="1" x2="23" y2="23" />
            </svg>
          </button>
        </div>
        <div class="sum-meta">
          {{ t('policy.summary.regLoc') }}<b>{{ provinceLabel(formState.province) }}</b>
          <span class="sep">·</span>
          {{ t('policy.summary.industry') }}<b>{{ industries[formState.industryIdx] }}</b>
          <span class="sep">·</span>
          {{ t('policy.summary.scalePre') }}<b class="em">{{ formState.teamSize }}</b>{{ t('policy.summary.scalePost') }}
          <span class="sep">·</span>
          {{ t('policy.summary.capitalPre') }}<b class="em">{{ formState.capital }}</b>{{ t('policy.summary.capitalPost') }}
        </div>
      </div>

      <div class="sum-right">
        <div class="sum-stat">
          <div class="sum-stat-label">{{ t('policy.summary.matchedCount') }}</div>
          <div class="sum-stat-val">{{ matchedPolicies.length }} <span>{{ t('policy.summary.matchedUnit') }}</span></div>
        </div>
        <div class="sum-stat danger">
          <div class="sum-stat-label">{{ t('policy.summary.maxBenefit') }}</div>
          <div class="sum-stat-val red">¥ {{ matchedSum.toLocaleString(localeTag) }}</div>
        </div>
      </div>
    </div>

    <!-- 分类与控制台 -->
    <div class="control-bar">
      <div class="tab-group">
        <button
          v-for="cat in categoryKeys"
          :key="cat"
          class="tab"
          :class="{ active: currentCategory === cat }"
          :style="currentCategory === cat ? { color: policyCategories[cat].hex, borderColor: policyCategories[cat].border } : {}"
          @click="setCategory(cat)"
        >{{ categoryLabel(cat) }}</button>
      </div>

      <div class="filters">
        <div class="select-wrap">
          <select v-model="currentPriority" class="input">
            <option value="ALL">{{ t('policy.filters.allPriority') }}</option>
            <option value="P0">{{ t('policy.priority.P0') }}</option>
            <option value="P1">{{ t('policy.priority.P1') }}</option>
            <option value="P2">{{ t('policy.priority.P2') }}</option>
          </select>
        </div>
        <div class="select-wrap">
          <select v-model="currentSort" class="input">
            <option value="priority">{{ t('policy.filters.sortPriority') }}</option>
            <option value="amountDesc">{{ t('policy.filters.sortAmount') }}</option>
            <option value="probDesc">{{ t('policy.filters.sortProb') }}</option>
            <option value="deadlineAsc">{{ t('policy.filters.sortDeadline') }}</option>
          </select>
        </div>
      </div>
    </div>

    <!-- 政策卡片 -->
    <div v-if="matchedPolicies.length === 0" class="empty">
      <div class="empty-ico">📭</div>
      <h4>{{ t('policy.empty.title') }}</h4>
      <p>{{ t('policy.empty.desc') }}</p>
    </div>

    <div v-else class="policy-grid">
      <div
        v-for="policy in matchedPolicies"
        :key="policy.id"
        class="policy-card"
        :style="{ borderLeftColor: policyCategories[policy.category].hex }"
      >
        <div class="pc-head">
          <h4 class="pc-title">{{ pTitle(policy) }}</h4>
          <span
            class="pc-priority"
            :style="{ color: priorityStyles[policy.priority].color, background: priorityStyles[policy.priority].bg, borderColor: priorityStyles[policy.priority].border }"
          >{{ priorityLabel(policy.priority) }}</span>
        </div>

        <div class="pc-board">
          <div class="pc-board-top">
            <div class="pc-value">
              <span v-if="formatValue(policy).prefix" class="pc-value-prefix">{{ formatValue(policy).prefix }}</span>
              <span class="pc-value-num" :style="{ color: policyCategories[policy.category].hex }">{{ formatValue(policy).value }}</span>
              <span class="pc-value-unit">{{ t('policy.card.perUnit', { unit: pUnit(policy) }) }}</span>
            </div>
            <div class="pc-deadline">
              <div class="pc-deadline-label">{{ t('policy.card.deadlineLabel') }}</div>
              <div class="pc-deadline-num" :style="{ color: deadlineColor(policy.deadlineDays) }">
                <span v-if="policy.deadlineDays <= 15" class="fire">🔥</span>{{ policy.deadlineDays }} <span class="dim">{{ t('policy.card.days') }}</span>
              </div>
            </div>
          </div>
          <div class="pc-board-bottom">
            <span>{{ t('policy.card.prob') }}<b :style="{ color: probColor(policy.prob) }">{{ policy.prob }}%</b></span>
            <span class="sep">·</span>
            <span>{{ t('policy.card.cycle') }}<b>{{ pCycle(policy) }}</b></span>
          </div>
        </div>

        <div class="pc-reasons">
          <div class="pc-reasons-title">{{ t('policy.card.aiMatch') }}</div>
          <div class="pc-reasons-list">
            <span v-for="(r, idx) in policy.reasons" :key="idx" class="pc-reason">
              <span class="check">✓</span>{{ r }}
            </span>
          </div>
        </div>

        <p class="pc-desc">{{ pDesc(policy) }}</p>

        <div class="pc-foot">
          <div class="pc-dept" :style="{ color: policyCategories[policy.category].hex }">
            🏛️ <span>{{ pDept(policy) }}</span>
          </div>
          <button class="pc-apply">{{ t('policy.card.apply') }}</button>
        </div>
      </div>
    </div>

    <div class="ai-disclaimer">
      <span class="ai-disclaimer-icon">⚠️</span>
      <p><b>{{ t('common.aiRiskTitle') }}</b>{{ t('common.aiRiskSep') }}{{ t('common.aiRiskDesc') }}</p>
    </div>
  </div>
</template>

<style scoped>
.pol-root { display: flex; flex-direction: column; gap: 20px; }

/* link bar (与 ControlSandbox 一致) */
.link-bar {
  display: flex; justify-content: space-between; align-items: center;
  background: #fff7e6; border: 1px solid #ffe7ba; color: #8c5300;
  padding: 10px 16px; border-radius: var(--radius); font-size: 13px;
}
.link-bar.linked { background: #f6ffed; border-color: #b7eb8f; color: #389e0d; }
.link-left { display: flex; flex-wrap: wrap; align-items: center; gap: 12px; }
.dot { width: 8px; height: 8px; border-radius: 50%; background: #fa8c16; animation: pulse 1.6s infinite; }
.link-bar.linked .dot { background: #52c41a; }
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.3; } }
.link-title { font-weight: 600; }
.link-fields { font-size: 12px; opacity: 0.85; }
.link-reset {
  background: white; border: 1px solid #b7eb8f; color: #389e0d;
  padding: 4px 12px; border-radius: 4px; font-size: 12px; cursor: pointer;
}
.link-reset:hover { background: #f6ffed; }

/* generic card */
.card {
  background: white; border-radius: var(--radius);
  box-shadow: var(--shadow);
  padding: 24px;
}
.card-header {
  display: flex; justify-content: space-between; align-items: flex-start;
  margin-bottom: 20px; padding-bottom: 16px;
  border-bottom: 1px solid var(--border-light); gap: 16px;
}
.step-chip {
  display: inline-block;
  background: linear-gradient(135deg, #e6f4ff, #f0f5ff);
  color: var(--primary); font-size: 11px; font-weight: 600;
  padding: 3px 10px; border-radius: 12px; letter-spacing: 0.5px;
}
.setup-title { font-size: 17px; font-weight: 700; margin-top: 8px; color: var(--text); }
.setup-sub { font-size: 12px; color: var(--text-secondary); margin-top: 4px; }
.ai-badge {
  background: linear-gradient(135deg, #1677ff, #4096ff);
  color: white; font-size: 11px; padding: 4px 12px; border-radius: 12px;
  font-weight: 500; white-space: nowrap;
}

/* setup grid */
.setup-grid { display: grid; gap: 16px; grid-template-columns: repeat(4, minmax(0, 1fr)); }
.field { display: flex; flex-direction: column; gap: 6px; min-width: 0; }
.field.col-2 { grid-column: span 2; }
.field label { font-size: 12px; font-weight: 500; color: var(--text-secondary); }
.input {
  height: 36px; padding: 0 10px; border: 1px solid var(--border);
  border-radius: 6px; font-size: 13px; color: var(--text);
  background: white; outline: none; transition: all 0.2s;
}
.input:focus { border-color: var(--primary); box-shadow: 0 0 0 2px rgba(22,119,255,0.15); }
.num-box {
  display: flex; align-items: center; border: 1px solid var(--border);
  border-radius: 6px; padding: 0 10px 0 4px; height: 36px;
  background: white; transition: all 0.2s;
}
.num-box:focus-within { border-color: var(--primary); box-shadow: 0 0 0 2px rgba(22,119,255,0.15); }
.num-box input {
  flex: 1; min-width: 0; border: none; outline: none; height: 100%;
  text-align: center; font-size: 13px; font-weight: 600; background: transparent;
}
.unit { font-size: 12px; color: var(--text-secondary); }

.ready-strip {
  flex-direction: row !important; justify-content: space-between; align-items: center;
  padding: 10px 14px; background: #f5f9ff; border: 1px solid #d6e8ff; border-radius: 6px;
}
.ready-text { font-size: 12px; color: var(--text-secondary); }
.ready-text b { color: var(--primary); font-weight: 700; }
.ready-pulse { display: inline-flex; gap: 4px; }
.ready-pulse span {
  width: 6px; height: 6px; border-radius: 50%; background: var(--primary);
  animation: pulse 1.6s infinite;
}
.ready-pulse span:nth-child(2) { animation-delay: 0.2s; }
.ready-pulse span:nth-child(3) { animation-delay: 0.4s; }

/* summary */
.summary-card {
  background: linear-gradient(135deg, #f0f7ff, #e6f4ff 60%, #f5f0ff);
  border-radius: var(--radius); padding: 24px 28px;
  display: flex; justify-content: space-between; align-items: center;
  gap: 24px; flex-wrap: wrap;
  border: 1px solid #d6e8ff; box-shadow: var(--shadow);
}
.sum-left { display: flex; flex-direction: column; gap: 6px; min-width: 0; }
.sum-name { display: flex; align-items: center; gap: 10px; }
.sum-title { font-size: 19px; font-weight: 700; letter-spacing: 0.3px; color: var(--text); }
.eye-btn {
  background: transparent; border: none; cursor: pointer;
  width: 24px; height: 24px; padding: 0;
  display: inline-flex; align-items: center; justify-content: center;
  border-radius: 4px; color: var(--text-secondary); opacity: 0.7;
  transition: all 0.15s;
}
.eye-btn:hover { opacity: 1; background: rgba(0,0,0,0.06); }
.sum-meta { font-size: 12px; color: var(--text-secondary); }
.sum-meta b { color: var(--text); font-weight: 500; }
.sum-meta .em { color: var(--primary); font-weight: 700; }
.sum-meta .sep { margin: 0 8px; opacity: 0.4; }

.sum-right { display: flex; align-items: center; gap: 28px; }
.sum-stat { text-align: right; }
.sum-stat-label { font-size: 10px; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 1px; margin-bottom: 4px; }
.sum-stat-val { font-size: 26px; font-weight: 800; color: var(--text); font-variant-numeric: tabular-nums; }
.sum-stat-val span { font-size: 13px; font-weight: 500; color: var(--text-secondary); }
.sum-stat-val.red { color: var(--error); }
.sum-stat.danger { border-left: 3px solid var(--error); padding-left: 16px; }

/* control bar */
.control-bar {
  display: flex; justify-content: space-between; align-items: center;
  gap: 16px; flex-wrap: wrap;
}
.tab-group {
  display: inline-flex; gap: 4px; padding: 4px;
  background: #f1f5f9; border: 1px solid #e2e8f0; border-radius: 8px;
}
.tab {
  background: transparent; border: 1px solid transparent;
  padding: 6px 14px; font-size: 13px; font-weight: 500;
  color: var(--text-secondary); border-radius: 6px;
  cursor: pointer; transition: all 0.15s;
  white-space: nowrap;
}
.tab:hover { color: var(--text); background: rgba(255,255,255,0.6); }
.tab.active {
  background: white; box-shadow: var(--shadow);
  font-weight: 600;
}
.filters { display: flex; gap: 10px; }
.select-wrap .input { min-width: 160px; cursor: pointer; }

/* empty */
.empty {
  background: white; border: 1px dashed var(--border);
  border-radius: var(--radius); padding: 60px 24px;
  text-align: center; color: var(--text-secondary);
}
.empty-ico { font-size: 36px; margin-bottom: 12px; opacity: 0.5; }
.empty h4 { font-size: 15px; font-weight: 700; color: var(--text); margin-bottom: 6px; }
.empty p { font-size: 12.5px; max-width: 420px; margin: 0 auto; }

/* policy cards */
.policy-grid {
  display: grid; gap: 20px;
  grid-template-columns: repeat(auto-fill, minmax(420px, 1fr));
}
.policy-card {
  background: white; border-radius: var(--radius);
  border: 1px solid var(--border-light); border-left: 4px solid #cbd5e1;
  box-shadow: var(--shadow); padding: 22px;
  display: flex; flex-direction: column; gap: 14px;
  transition: all 0.2s;
}
.policy-card:hover { box-shadow: var(--shadow-md); transform: translateY(-1px); }

.pc-head { display: flex; justify-content: space-between; align-items: flex-start; gap: 12px; }
.pc-title {
  font-size: 16px; font-weight: 700; color: var(--text);
  line-height: 1.4; flex: 1;
}
.pc-priority {
  font-size: 11px; font-weight: 700; padding: 3px 8px;
  border-radius: 4px; border: 1px solid; white-space: nowrap; flex-shrink: 0;
}

.pc-board {
  background: #fafbfc; border: 1px solid #f1f5f9;
  border-radius: 6px; padding: 14px;
}
.pc-board-top {
  display: flex; justify-content: space-between; align-items: flex-end;
  padding-bottom: 12px; margin-bottom: 12px;
  border-bottom: 1px dashed #e2e8f0;
}
.pc-value { display: flex; align-items: baseline; gap: 4px; flex-wrap: wrap; }
.pc-value-prefix { font-size: 11px; color: var(--text-secondary); margin-right: 2px; }
.pc-value-num { font-size: 24px; font-weight: 800; letter-spacing: -0.3px; font-variant-numeric: tabular-nums; }
.pc-value-unit { font-size: 11px; color: var(--text-secondary); }
.pc-deadline { text-align: right; }
.pc-deadline-label { font-size: 10px; color: var(--text-secondary); margin-bottom: 2px; }
.pc-deadline-num { font-size: 15px; font-weight: 700; font-variant-numeric: tabular-nums; }
.pc-deadline-num .dim { font-size: 11px; font-weight: 500; color: var(--text-secondary); }
.pc-deadline-num .fire { margin-right: 4px; animation: pulse 1.4s infinite; }

.pc-board-bottom { font-size: 12px; color: var(--text-secondary); display: flex; gap: 8px; align-items: center; }
.pc-board-bottom b { color: var(--text); font-weight: 700; margin-left: 2px; }
.pc-board-bottom .sep { opacity: 0.3; }

.pc-reasons {
  background: #f5f3ff; border: 1px solid #ede9fe;
  border-radius: 6px; padding: 10px 12px;
}
.pc-reasons-title { font-size: 11px; font-weight: 700; color: #6d28d9; margin-bottom: 6px; }
.pc-reasons-list { display: flex; flex-wrap: wrap; gap: 8px 14px; }
.pc-reason {
  font-size: 11.5px; color: var(--text); display: inline-flex; align-items: center; gap: 4px;
}
.pc-reason .check { color: #059669; font-weight: 700; }

.pc-desc {
  font-size: 11.5px; color: var(--text-secondary); line-height: 1.6;
  display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical;
  overflow: hidden;
}

.pc-foot {
  display: flex; justify-content: space-between; align-items: center;
  padding-top: 12px; border-top: 1px solid var(--border-light); margin-top: auto;
}
.pc-dept {
  font-size: 11.5px; font-weight: 500; display: flex; align-items: center; gap: 6px;
  max-width: 60%; overflow: hidden; white-space: nowrap; text-overflow: ellipsis;
}
.pc-dept span { overflow: hidden; text-overflow: ellipsis; }
.pc-apply {
  background: white; color: var(--text);
  border: 1px solid var(--border); border-radius: 6px;
  padding: 6px 14px; font-size: 12px; font-weight: 500;
  cursor: pointer; transition: all 0.15s;
}
.pc-apply:hover {
  color: var(--primary); border-color: var(--primary);
  background: #e6f4ff;
}

@media (max-width: 900px) {
  .setup-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .field.col-2 { grid-column: span 2; }
  .sum-right { width: 100%; justify-content: space-between; }
}
@media (max-width: 600px) {
  .setup-grid { grid-template-columns: 1fr; }
  .field.col-2 { grid-column: span 1; }
  .policy-grid { grid-template-columns: 1fr; }
}
</style>
