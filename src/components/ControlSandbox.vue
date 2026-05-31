<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount, watch, nextTick, reactive } from 'vue'
import { useI18n } from 'vue-i18n'
import { Chart, registerables } from 'chart.js'
import type { ChartType } from 'chart.js'
import { sharedFormData } from '../store'

const { t, tm, locale } = useI18n()

Chart.register(...registerables)

/* ---------------- 行业 / 成本矩阵 ---------------- */

// 行业名（仅展示，随语言切换）；逻辑用 industryIdx，与列表顺序一一对应
const industries = computed(() => tm('control.industries') as string[])

type Tier = '0–10%' | '10–30%' | '30%以上'

// 成本科目：cat = 一级体系 id（语言无关），key = 科目 id（语言无关），values = 行业档位
interface CostRow {
  cat: string
  key: string
  values: Tier[]
}

function normTier(v: string): Tier {
  if (v.includes('30%')) return '30%以上'
  if (v.includes('10')) return '10–30%'
  return '0–10%'
}

const RAW_STRUCTURE: { cat: string; key: string; values: string[] }[] = [
  { cat: 'compliance', key: 'regCompliance', values: ['10–30%','30%以上','10–30%','30%以上','10–30%','0–10%','10–30%','10–30%','10–30%','30%以上','30%以上','10–30%','10–30%','30%以上','0–10%','10–30%','30%以上','10–30%','30%以上','30%以上'] },
  { cat: 'compliance', key: 'license', values: ['10–30%','30%以上','30%以上','30%以上','30%以上','0–10%','30%以上','30%以上','10–30%','30%以上','30%以上','10–30%','10–30%','30%以上','10–30%','30%以上','30%以上','10–30%','30%以上','30%以上'] },
  { cat: 'compliance', key: 'legalTaxBasic', values: ['10–30%','30%以上','10–30%','10–30%','10–30%','10–30%','10–30%','10–30%','10–30%','30%','30%以上','10–30%','10–30%','10–30%','0–10%','10–30%','10–30%','10–30%','30%以上','30%以上'] },
  { cat: 'space', key: 'officeRent', values: ['0–10%','10–30%','10–30%','10–30%','10–30%','30%以上','10–30%','30%以上','10–30%','30%以上','30%以上','30%以上','10–30%','10–30%','10–30%','10–30%','30%以上','10–30%','10–30%','10–30%'] },
  { cat: 'space', key: 'storeFactory', values: ['10–30%','30%以上','30%以上','30%以上','10–30%','30%以上','30%以上','30%以上','0–10%','0–10%','30%以上','10–30%','0–10%','10–30%','10–30%','0–10%','30%以上','10–30%','0–10%','0–10%'] },
  { cat: 'space', key: 'equipment', values: ['10–30%','30%以上','30%以上','30%以上','10–30%','10–30%','30%以上','10–30%','0–10%','10–30%','10–30%','0–10%','10–30%','30%以上','10–30%','10–30%','30%以上','10–30%','10–30%','10–30%'] },
  { cat: 'space', key: 'warehouse', values: ['30%以上','10–30%','30%以上','10–30%','10–30%','30%以上','30%以上','10–30%','0–10%','0–10%','10–30%','0–10%','0–10%','10–30%','0–10%','0–10%','10–30%','0–10%','0–10%','0–10%'] },
  { cat: 'digital', key: 'saas', values: ['0–10%','0–10%','10–30%','10–30%','10–30%','10–30%','10–30%','0–10%','30%以上','30%以上','10–30%','30%以上','30%以上','10–30%','10–30%','10–30%','10–30%','10–30%','10–30%','10–30%'] },
  { cat: 'digital', key: 'cloud', values: ['0–10%','0–10%','0–10%','0–10%','0–10%','0–10%','10–30%','0–10%','30%以上','30%以上','10–30%','10–30%','30%以上','10–30%','0–10%','10–30%','10–30%','30%以上','10–30%','30%以上'] },
  { cat: 'digital', key: 'devops', values: ['0–10%','0–10%','10–30%','10–30%','0–10%','0–10%','10–30%','0–10%','30%以上','30%以上','10–30%','10–30%','30%以上','10–30%','0–10%','10–30%','10–30%','30%以上','10–30%','30%以上'] },
  { cat: 'digital', key: 'apiAi', values: ['0–10%','0–10%','0–10%','0–10%','0–10%','0–10%','10–30%','0–10%','30%以上','30%以上','10–30%','10–30%','30%以上','10–30%','0–10%','10–30%','10–30%','30%以上','10–30%','30%以上'] },
  { cat: 'people', key: 'coreHR', values: ['10–30%','10–30%','10–30%','10–30%','30%以上','10–30%','10–30%','30%以上','30%以上','30%以上','10–30%','30%以上','30%以上','10–30%','30%以上','30%以上','30%以上','30%以上','30%以上','30%以上'] },
  { cat: 'people', key: 'support', values: ['0–10%','0–10%','10–30%','10–30%','10–30%','30%以上','30%以上','30%以上','10–30%','30%以上','10–30%','10–30%','10–30%','10–30%','30%以上','10–30%','30%以上','10–30%','10–30%','10–30%'] },
  { cat: 'people', key: 'opsMgmt', values: ['10–30%','10–30%','10–30%','10–30%','30%以上','10–30%','30%','30%以上','30%以上','30%以上','30%以上','30%以上','30%以上','30%以上','10–30%','30%以上','30%以上','30%以上','30%以上','30%以上'] },
  { cat: 'people', key: 'travelTraining', values: ['0–10%','10–30%','10–30%','0–10%','30%以上','0–10%','10–30%','0–10%','10–30%','10–30%','10–30%','10–30%','30%以上','10–30%','0–10%','10–30%','10–30%','10–30%','10–30%','30%以上'] },
  { cat: 'growth', key: 'ads', values: ['0–10%','0–10%','10–30%','0–10%','0–10%','30%以上','10–30%','30%以上','30%以上','10–30%','10–30%','10–30%','10–30%','0–10%','10–30%','30%以上','0–10%','30%以上','0–10%','0–10%'] },
  { cat: 'growth', key: 'channelCommission', values: ['0–10%','0–10%','10–30%','0–10%','0–10%','30%以上','10–30%','30%以上','10–30%','0–10%','0–10%','10–30%','0–10%','0–10%','10–30%','10–30%','0–10%','30%以上','0–10%','0–10%'] },
  { cat: 'growth', key: 'salesCommission', values: ['0–10%','10–30%','10–30%','10–30%','10–30%','30%以上','10–30%','10–30%','30%以上','30%以上','30%以上','30%以上','10–30%','0–10%','10–30%','10–30%','0–10%','30%以上','0–10%','0–10%'] },
  { cat: 'growth', key: 'brandContent', values: ['0–10%','0–10%','0–10%','0–10%','0–10%','10–30%','10–30%','30%以上','30%以上','10–30%','10–30%','10–30%','10–30%','0–10%','10–30%','30%以上','0–10%','30%以上','0–10%','10–30%'] },
  { cat: 'risk', key: 'returnsLoss', values: ['30%以上','10–30%','10–30%','0–10%','10–30%','30%以上','10–30%','30%以上','0–10%','10–30%','10–30%','0–10%','0–10%','0–10%','10–30%','0–10%','10–30%','10–30%','0–10%','0–10%'] },
  { cat: 'risk', key: 'inventory', values: ['30%以上','10–30%','30%以上','10–30%','0–10%','30%以上','10–30%','30%以上','0–10%','0–10%','30%以上','0–10%','0–10%','0–10%','0–10%','0–10%','10–30%','0–10%','0–10%','0–10%'] },
  { cat: 'risk', key: 'legalRiskFine', values: ['10–30%','30%以上','10–30%','30%以上','30%以上','10–30%','10–30%','10–30%','30%以上','30%以上','30%以上','10–30%','10–30%','30%以上','10–30%','10–30%','30%以上','10–30%','30%以上','30%以上'] },
  { cat: 'risk', key: 'insuranceFx', values: ['30%以上','30%以上','10–30%','10–30%','10–30%','10–30%','30%以上','10–30%','0–10%','30%以上','10–30%','10–30%','0–10%','10–30%','0–10%','0–10%','10–30%','10–30%','0–10%','30%以上'] },
]

const costStructure: CostRow[] = RAW_STRUCTURE.map(r => ({
  cat: r.cat,
  key: r.key,
  values: r.values.map(normTier) as Tier[],
}))

// 一级体系：id → 图标/配色（语言无关）；显示名走 t('control.categories.'+id)
interface CategoryMeta { icon: string; hex: string }
const categoriesMeta: Record<string, CategoryMeta> = {
  compliance: { icon: '⚖️', hex: '#6366f1' },
  space:      { icon: '🏢', hex: '#3b82f6' },
  digital:    { icon: '💻', hex: '#06b6d4' },
  people:     { icon: '👥', hex: '#10b981' },
  growth:     { icon: '📈', hex: '#f59e0b' },
  risk:       { icon: '🛡️', hex: '#f43f5e' },
}
const categoryOrder = Object.keys(categoriesMeta)
const catLabel = (id: string) => t('control.categories.' + id)
const itemLabel = (key: string) => t('control.items.' + key)

/* ---------------- 表单状态 + 联动 ---------------- */

// 省份 / 公司类型：id 语言无关，显示走 t()
const PROVINCE_IDS = ['beijing', 'shanghai', 'guangdong', 'zhejiang', 'other']
const COMPANY_TYPE_IDS = ['llc', 'jsc', 'partnership']
const provinceLabel = (id: string) => t('control.provinces.' + id)
const companyTypeLabel = (id: string) => t('control.companyTypes.' + id)

const formState = reactive({
  industryIdx: 8,
  teamSize: 10,
  shareholder: 3,
  province: 'beijing',
  companyType: 'llc',
  namePref: '星禾云创',
  capital: 100,
  scopeMain: '软件开发',
  scopeOthers: '信息系统集成服务、技术服务、技术咨询、数据处理服务',
})

/** 字段是否曾被用户手动覆盖：若是，则不再被工商注册数据自动覆盖。 */
const overridden = reactive<Record<keyof typeof formState, boolean>>({
  industryIdx: false, teamSize: false, shareholder: false, province: false,
  companyType: false, namePref: false, capital: false, scopeMain: false, scopeOthers: false,
})

// 行业匹配：优先 (A)~(T) 字母前缀（语言无关），再退回中文关键词扫描
function matchIndustryIdx(text: string): number {
  if (!text) return 8
  const letter = text.match(/\(([A-T])\)/i)?.[1]?.toUpperCase()
  if (letter) {
    const idx = letter.charCodeAt(0) - 65
    if (idx >= 0 && idx < 20) return idx
  }
  const lower = text.toLowerCase()
  const aliases: { kws: string[]; idx: number }[] = [
    { kws: ['农', '林', '牧', '渔', 'agricultur'], idx: 0 },
    { kws: ['矿', 'mining'], idx: 1 },
    { kws: ['制造', '工厂', 'manufactur'], idx: 2 },
    { kws: ['电力', '燃气', '水务', 'electricity', 'gas', 'water'], idx: 3 },
    { kws: ['建筑', '工程', 'construction'], idx: 4 },
    { kws: ['批发', '零售', '电商', 'wholesale', 'retail'], idx: 5 },
    { kws: ['物流', '仓储', '运输', '邮政', 'transport', 'storage', 'postal'], idx: 6 },
    { kws: ['餐饮', '酒店', '住宿', 'catering', 'accommodation'], idx: 7 },
    { kws: ['软件', '互联网', 'saas', 'it', '信息', '科技', '数字', 'software', 'information'], idx: 8 },
    { kws: ['金融', '银行', '保险', '证券', 'finance'], idx: 9 },
    { kws: ['房地产', '地产', 'real estate'], idx: 10 },
    { kws: ['租赁', '商务服务', '咨询', 'leasing', 'business service'], idx: 11 },
    { kws: ['科研', '研究', '技术服务', 'research', 'technical'], idx: 12 },
    { kws: ['环境', '环保', '公共设施', 'environment', 'conservancy'], idx: 13 },
    { kws: ['居民服务', '维修', '修理', 'residential', 'repair'], idx: 14 },
    { kws: ['教育', '培训', 'education'], idx: 15 },
    { kws: ['卫生', '医疗', '社会工作', 'health', 'social work'], idx: 16 },
    { kws: ['文化', '体育', '娱乐', 'culture', 'sports', 'entertainment'], idx: 17 },
    { kws: ['公共管理', '社保', 'public administration'], idx: 18 },
    { kws: ['国际组织', 'international organization'], idx: 19 },
  ]
  for (const a of aliases) if (a.kws.some(k => lower.includes(k.toLowerCase()))) return a.idx
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

// 公司类型匹配：返回 id，中英文皆可识别
function matchCompanyType(ct: string): string {
  if (!ct) return 'llc'
  const s = ct.toLowerCase()
  if (ct.includes('股份') || s.includes('joint-stock') || s.includes('joint stock')) return 'jsc'
  if (ct.includes('合伙') || s.includes('partnership')) return 'partnership'
  return 'llc'
}

function parseCapital(c: string): number {
  if (!c) return 100
  const m = c.match(/(\d+(\.\d+)?)/)
  return m ? Math.round(parseFloat(m[1])) : 100
}

const isLinked = computed(() => !!sharedFormData.value)

const linkedFields = computed(() => {
  const f = sharedFormData.value
  if (!f) return [] as string[]
  const arr: string[] = []
  if (f.business && !overridden.industryIdx) arr.push(t('control.fieldTags.industry'))
  if (typeof f.people === 'number' && f.people > 0 && !overridden.teamSize) arr.push(t('control.fieldTags.teamSize'))
  if (typeof f.shareholder === 'number' && f.shareholder > 0 && !overridden.shareholder) arr.push(t('control.fieldTags.shareholder'))
  if (f.address && !overridden.province) arr.push(t('control.fieldTags.province'))
  if (f.companyType && !overridden.companyType) arr.push(t('control.fieldTags.companyType'))
  if (f.namePref && !overridden.namePref) arr.push(t('control.fieldTags.namePref'))
  if (f.capital && !overridden.capital) arr.push(t('control.fieldTags.capital'))
  if (f.scope && typeof f.scope === 'object') {
    if (f.scope.main && !overridden.scopeMain) arr.push(t('control.fieldTags.scopeMain'))
    if (f.scope.others?.length && !overridden.scopeOthers) arr.push(t('control.fieldTags.scopeOthers'))
  }
  return arr
})

function applyFromShared() {
  const f = sharedFormData.value
  if (!f) return
  if (f.business && !overridden.industryIdx)      formState.industryIdx = matchIndustryIdx(f.business)
  if (typeof f.people === 'number' && f.people > 0 && !overridden.teamSize) formState.teamSize = f.people
  if (typeof f.shareholder === 'number' && f.shareholder > 0 && !overridden.shareholder) formState.shareholder = f.shareholder
  if (f.address && !overridden.province)          formState.province = matchProvince(f.address)
  if (f.companyType && !overridden.companyType)   formState.companyType = matchCompanyType(f.companyType)
  if (f.namePref && !overridden.namePref)         formState.namePref = f.namePref
  if (f.capital && !overridden.capital)           formState.capital = parseCapital(f.capital)
  if (f.scope && typeof f.scope === 'object') {
    if (f.scope.main && !overridden.scopeMain)    formState.scopeMain = f.scope.main
    if (f.scope.others?.length && !overridden.scopeOthers) formState.scopeOthers = f.scope.others.join('、')
  }
}

watch(() => sharedFormData.value, applyFromShared, { deep: true, immediate: true })

function markOverride(field: keyof typeof formState) { overridden[field] = true }
function resetLink() {
  ;(Object.keys(overridden) as (keyof typeof formState)[]).forEach(k => (overridden[k] = false))
  applyFromShared()
}

const previewName = computed(() =>
  t('control.previewName', {
    name: formState.namePref,
    suffix: formState.companyType === 'jsc' ? t('control.jscSuffix') : '',
  }),
)

const setupVisible = ref(false)
watch(isLinked, v => { setupVisible.value = !v }, { immediate: true })

/* ---------------- 预算计算 ---------------- */

interface BudgetItem { key?: string; name: string; money: number }
type BudgetByCategory = Record<string, BudgetItem[]>

const budgetData = ref<BudgetByCategory>({})
const benchmark = ref<Record<string, number>>({})
const cardLocked = reactive<Record<string, boolean>>({})
categoryOrder.forEach(c => (cardLocked[c] = true))

function recomputeBudget() {
  const { industryIdx, teamSize, shareholder, province, companyType, capital } = formState
  const ts = Math.max(1, teamSize | 0)
  const sh = Math.max(1, shareholder | 0)
  const cap = Math.max(1, capital | 0)

  const baseCostPerPersonPerMonth = 12000
  const durationMonths = 3
  const coreHRBase = ts * baseCostPerPersonPerMonth * durationMonths

  const locMul = (province === 'beijing' || province === 'shanghai') ? 1.45
    : province === 'other' ? 0.8 : 1.0

  let totalWeight = 0
  const weights = costStructure.map(row => {
    const tier = row.values[industryIdx]
    let w = 0.35
    if (tier === '30%以上') w = 3.5
    else if (tier === '10–30%') w = 1.5
    totalWeight += w
    return { cat: row.cat, key: row.key, weight: w }
  })

  const humanCoreW = weights.find(i => i.key === 'coreHR')!.weight
  const initialTotal = (coreHRBase / humanCoreW) * totalWeight

  const next: BudgetByCategory = {}
  const bench: Record<string, number> = {}
  categoryOrder.forEach(c => { next[c] = []; bench[c] = 0 })

  weights.forEach((wi, idx) => {
    let money = (initialTotal / totalWeight) * wi.weight
    if (wi.key === 'officeRent' || wi.key === 'storeFactory') money *= locMul
    if (wi.key === 'regCompliance' || wi.key === 'legalTaxBasic') {
      money += sh * 1500
      if (companyType === 'jsc') money *= 1.3
    }
    if (wi.key === 'insuranceFx' || wi.key === 'legalRiskFine') money += cap * 20

    const noise = Math.sin(idx + industryIdx + ts) * (money * 0.04)
    let final = Math.round(money + noise)
    if (final <= 0) final = Math.round(3500 + Math.abs(Math.sin(idx) * 2000))

    next[wi.cat].push({ key: wi.key, name: itemLabel(wi.key), money: final })
    bench[wi.cat] += final
  })

  budgetData.value = next
  benchmark.value = bench
}

watch(() => ({ ...formState }), recomputeBudget, { immediate: true })

const totalBudget = computed(() =>
  categoryOrder.reduce((s, c) =>
    s + (budgetData.value[c]?.reduce((a, b) => a + b.money, 0) ?? 0), 0)
)
const localeTag = computed(() => (locale.value === 'zh' ? 'zh-CN' : 'en-US'))
const fmt = (n: number) => '¥ ' + Math.round(n).toLocaleString(localeTag.value)

/* ---------------- 卡片编辑 ---------------- */

function toggleLock(cat: string) { cardLocked[cat] = !cardLocked[cat] }
function addItem(cat: string) {
  const seed = Math.round(1200 + Math.random() * 8700)
  budgetData.value[cat].push({ name: t('control.bill.customItem'), money: seed })
}
function deleteItem(cat: string, idx: number) {
  budgetData.value[cat].splice(idx, 1)
}
function updateMoney(cat: string, idx: number, val: string) {
  const n = parseInt(val); budgetData.value[cat][idx].money = isNaN(n) ? 0 : n
}

/* ---------------- 图表 ---------------- */

const pieEl = ref<HTMLCanvasElement | null>(null)
const radarEl = ref<HTMLCanvasElement | null>(null)
const barEl = ref<HTMLCanvasElement | null>(null)
let pie: Chart | null = null
let radar: Chart | null = null
let bar: Chart | null = null

function categorySubtotal(cat: string) {
  return budgetData.value[cat]?.reduce((s, i) => s + i.money, 0) ?? 0
}

function rebuildCharts() {
  const cats = categoryOrder
  const subtotals = cats.map(categorySubtotal)
  const benchSubtotals = cats.map(c => benchmark.value[c] ?? 0)
  const total = subtotals.reduce((a, b) => a + b, 0)

  const pieLabels: string[] = []
  const pieData: number[] = []
  const pieColors: string[] = []
  cats.forEach((c, i) => {
    if (subtotals[i] > 0) {
      pieLabels.push(catLabel(c))
      pieData.push(subtotals[i])
      pieColors.push(categoriesMeta[c].hex)
    }
  })

  const shortLabels = cats.map(c => t('control.categoriesShort.' + c))

  /* doughnut */
  if (pie) {
    pie.data.labels = pieLabels
    pie.data.datasets[0].data = pieData
    ;(pie.data.datasets[0] as any).backgroundColor = pieColors
    pie.update()
  } else if (pieEl.value) {
    pie = new Chart(pieEl.value, {
      type: 'doughnut' as ChartType,
      data: { labels: pieLabels, datasets: [{ data: pieData, backgroundColor: pieColors, borderWidth: 1.5 }] },
      options: {
        responsive: true, maintainAspectRatio: false, cutout: '65%',
        plugins: {
          legend: { position: 'right', labels: { boxWidth: 10, font: { size: 11 } } },
          tooltip: {
            callbacks: {
              label: (ctx: any) => {
                const v = ctx.raw as number
                const pct = total > 0 ? Math.round((v / total) * 100) : 0
                return ` ${ctx.label}: ¥${v.toLocaleString()} (${pct}%)`
              },
            },
          },
        },
      } as any,
    })
  }

  /* radar */
  if (radar) {
    radar.data.labels = shortLabels
    radar.data.datasets[0].data = subtotals
    radar.data.datasets[1].data = benchSubtotals
    radar.update()
  } else if (radarEl.value) {
    radar = new Chart(radarEl.value, {
      type: 'radar',
      data: {
        labels: shortLabels,
        datasets: [
          { label: t('control.charts.current'), data: subtotals, fill: true, backgroundColor: 'rgba(22,119,255,0.15)', borderColor: '#1677ff', borderWidth: 1.8, pointBackgroundColor: '#1677ff' },
          { label: t('control.charts.benchmark'), data: benchSubtotals, fill: false, borderColor: 'rgba(148,163,184,0.7)', borderDash: [4, 4], pointBackgroundColor: '#94a3b8' },
        ],
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        plugins: { legend: { position: 'bottom', labels: { boxWidth: 10, font: { size: 11 } } } },
        scales: { r: { ticks: { display: false }, pointLabels: { font: { size: 10, weight: 'bold' } } } },
      },
    })
  }

  /* top bar */
  const all: BudgetItem[] = []
  cats.forEach(c => budgetData.value[c]?.forEach(n => { if (n.money > 0) all.push(n) }))
  all.sort((a, b) => b.money - a.money)
  const top = all.slice(0, 10)
  if (bar) {
    bar.data.labels = top.map(i => i.name)
    bar.data.datasets[0].data = top.map(i => i.money)
    bar.update()
  } else if (barEl.value) {
    bar = new Chart(barEl.value, {
      type: 'bar',
      data: { labels: top.map(i => i.name), datasets: [{ data: top.map(i => i.money), backgroundColor: '#1677ff', borderRadius: 4 }] },
      options: {
        indexAxis: 'y', responsive: true, maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: { x: { grid: { display: false } }, y: { grid: { display: false }, ticks: { font: { size: 10 } } } },
      },
    })
  }
}

let chartDebounce: number | null = null
watch([budgetData, benchmark], () => {
  if (chartDebounce) clearTimeout(chartDebounce)
  chartDebounce = window.setTimeout(rebuildCharts, 80)
}, { deep: true })

// 语言切换：重算预算（刷新科目本地化名称）并销毁重建图表（数据集 label 仅创建时生效）
watch(locale, () => {
  recomputeBudget()
  pie?.destroy(); radar?.destroy(); bar?.destroy()
  pie = radar = bar = null
  nextTick(rebuildCharts)
})

onMounted(() => { nextTick(rebuildCharts) })
onBeforeUnmount(() => {
  pie?.destroy(); radar?.destroy(); bar?.destroy()
  pie = radar = bar = null
})

/* ---------------- CSV 导出 ---------------- */

function exportCSV() {
  let csv = '﻿'
  csv += t('control.csv.reportTitle') + '\n'
  csv += `${t('control.csv.fullName')},${previewName.value}\n`
  csv += `${t('control.csv.industryZone')},${industries.value[formState.industryIdx]}\n`
  csv += `${t('control.csv.regRegion')},${provinceLabel(formState.province)}\n`
  csv += `${t('control.csv.coreScale')},${formState.teamSize} ${t('control.csv.peopleUnit')}\n\n`
  csv += t('control.csv.header') + '\n'

  let overall = 0
  categoryOrder.forEach(cat => {
    let sub = 0
    const cl = catLabel(cat)
    budgetData.value[cat]?.forEach(n => {
      csv += `"${cl}","${n.name}",${n.money}\n`
      sub += n.money; overall += n.money
    })
    csv += `"${cl}","${t('control.csv.subtotal', { cat: cl })}",${sub}\n`
  })
  csv += `"\n${t('control.csv.grandTotal')}","",${overall}\n`

  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = `LuckyOS_${t('control.csv.fileReport')}_${formState.namePref}_${industries.value[formState.industryIdx]}.csv`
  document.body.appendChild(link); link.click(); document.body.removeChild(link)
}
</script>

<template>
  <div class="ctrl-root">
    <!-- 顶部联动状态条 -->
    <div class="link-bar" :class="{ linked: isLinked && linkedFields.length }">
      <div class="link-left">
        <span class="dot" />
        <template v-if="isLinked && linkedFields.length">
          <span class="link-title">{{ t('control.link.syncedTitle') }}</span>
        </template>
        <template v-else>
          <span class="link-title">{{ t('control.link.notDetected') }}</span>
          <span class="link-fields">{{ t('control.link.manualHint') }}</span>
        </template>
      </div>
      <button v-if="isLinked" class="link-reset" @click="resetLink">{{ t('control.link.resync') }}</button>
    </div>

    <!-- 公司设立登记信息 -->
    <div v-show="setupVisible" class="card setup-card">
      <div class="card-header">
        <div>
          <span class="step-chip">{{ t('control.setup.stepChip') }}</span>
          <h3 class="setup-title">{{ t('control.setup.title') }}</h3>
        </div>
        <span class="ai-badge">{{ t('control.setup.badge') }}</span>
      </div>

      <div class="setup-grid">
        <div class="field col-2">
          <label>{{ t('control.fields.business') }}</label>
          <select v-model.number="formState.industryIdx" @change="markOverride('industryIdx')" class="input">
            <option v-for="(name, i) in industries" :key="i" :value="i">
              {{ String.fromCharCode(65 + i) }} — {{ name }}
            </option>
          </select>
        </div>

        <div class="field">
          <label>{{ t('control.fields.people') }}</label>
          <div class="num-box">
            <input type="number" min="1" max="500" v-model.number="formState.teamSize" @input="markOverride('teamSize')" />
            <span class="unit">{{ t('control.units.people') }}</span>
          </div>
        </div>

        <div class="field">
          <label>{{ t('control.fields.shareholder') }}</label>
          <div class="num-box">
            <input type="number" min="1" max="50" v-model.number="formState.shareholder" @input="markOverride('shareholder')" />
            <span class="unit">{{ t('control.units.shareholder') }}</span>
          </div>
        </div>

        <div class="field">
          <label>{{ t('control.fields.province') }}</label>
          <select v-model="formState.province" @change="markOverride('province')" class="input">
            <option v-for="p in PROVINCE_IDS" :key="p" :value="p">{{ provinceLabel(p) }}</option>
          </select>
        </div>

        <div class="field">
          <label>{{ t('control.fields.companyType') }}</label>
          <select v-model="formState.companyType" @change="markOverride('companyType')" class="input">
            <option v-for="ct in COMPANY_TYPE_IDS" :key="ct" :value="ct">{{ companyTypeLabel(ct) }}</option>
          </select>
        </div>

        <div class="field">
          <label>{{ t('control.fields.namePref') }}</label>
          <input class="input" v-model="formState.namePref" @input="markOverride('namePref')" />
        </div>

        <div class="field">
          <label>{{ t('control.fields.capital') }}</label>
          <div class="num-box">
            <input type="number" min="1" v-model.number="formState.capital" @input="markOverride('capital')" />
            <span class="unit">{{ t('control.units.wan') }}</span>
          </div>
        </div>

        <div class="field col-2">
          <label>{{ t('control.fields.scopeMain') }}</label>
          <input class="input" v-model="formState.scopeMain" @input="markOverride('scopeMain')" />
        </div>

        <div class="field col-2">
          <label>{{ t('control.fields.scopeOthers') }}</label>
          <input class="input" v-model="formState.scopeOthers" @input="markOverride('scopeOthers')" />
        </div>
      </div>
    </div>

    <!-- 总览栏 -->
    <div class="summary-card">
      <div class="sum-left">
        <div class="sum-name">
          <span class="sum-title">{{ previewName }}</span>
          <span class="sum-type">{{ companyTypeLabel(formState.companyType) }}</span>
          <button class="eye-btn" @click="setupVisible = !setupVisible" :title="setupVisible ? t('control.setup.collapse') : t('control.setup.expand')">
            <svg v-if="!setupVisible" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
              <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8S1 12 1 12z" />
              <circle cx="12" cy="12" r="3" />
            </svg>
            <svg v-else viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
              <path d="M17.94 17.94A10.94 10.94 0 0 1 12 20c-7 0-11-8-11-8a19.6 19.6 0 0 1 5.06-5.94" />
              <path d="M9.9 4.24A10.94 10.94 0 0 1 12 4c7 0 11 8 11 8a19.6 19.6 0 0 1-2.16 3.19" />
              <path d="M14.12 14.12a3 3 0 1 1-4.24-4.24" />
              <line x1="1" y1="1" x2="23" y2="23" />
            </svg>
          </button>
        </div>
        <div class="sum-meta">
          {{ t('control.summary.regLoc') }}<b>{{ provinceLabel(formState.province) }}</b>
          <span class="sep">·</span>
          {{ t('control.summary.industryZone') }}<b>{{ industries[formState.industryIdx] }}</b>
          <span class="sep">·</span>
          {{ t('control.summary.orgPre') }}<b class="em">{{ formState.teamSize }}</b>{{ t('control.summary.orgMid') }}<b class="em">{{ formState.shareholder }}</b>{{ t('control.summary.orgPost') }}
        </div>
      </div>
      <div class="sum-right">
        <div class="sum-budget">
          <div class="sum-budget-label">{{ t('control.summary.cashLabel') }}</div>
          <div class="sum-budget-val">{{ fmt(totalBudget) }}</div>
        </div>
        <button class="btn-export" @click="exportCSV">{{ t('control.summary.exportBtn') }}</button>
      </div>
    </div>

    <!-- 图表 -->
    <div class="chart-section">
      <div class="section-title">
        <h3>{{ t('control.charts.title') }}</h3>
        <p>{{ t('control.charts.subtitle') }}</p>
      </div>
      <div class="chart-grid">
        <div class="card chart-card">
          <h4 class="chart-h">{{ t('control.charts.pie') }}</h4>
          <div class="chart-box"><canvas ref="pieEl" /></div>
        </div>
        <div class="card chart-card">
          <h4 class="chart-h">{{ t('control.charts.radar') }}</h4>
          <div class="chart-box"><canvas ref="radarEl" /></div>
        </div>
        <div class="card chart-card">
          <h4 class="chart-h">{{ t('control.charts.bar') }}</h4>
          <div class="chart-box"><canvas ref="barEl" /></div>
        </div>
      </div>
    </div>

    <!-- 卡片明细 -->
    <div class="section-title">
      <h3>{{ t('control.bill.title') }}</h3>
      <p>{{ t('control.bill.subtitle') }}</p>
    </div>

    <div class="bill-grid">
      <div v-for="cat in categoryOrder" :key="cat" class="card bill-card" :class="{ unlocked: !cardLocked[cat] }">
        <div class="bill-head">
          <div class="bill-cat">
            <span class="bill-ico" :style="{ background: categoriesMeta[cat].hex + '1a', color: categoriesMeta[cat].hex }">{{ categoriesMeta[cat].icon }}</span>
            <span class="bill-name">{{ catLabel(cat) }}</span>
          </div>
          <button class="bill-lock" :class="{ on: !cardLocked[cat] }" @click="toggleLock(cat)" :title="cardLocked[cat] ? t('control.bill.unlock') : t('control.bill.lock')">
            {{ cardLocked[cat] ? '🔒' : '🔓' }}
          </button>
        </div>

        <div class="bill-items">
          <template v-if="cardLocked[cat]">
            <div v-for="(node, i) in budgetData[cat]" :key="i" class="item-row">
              <span class="item-name">{{ node.name }}</span>
              <span class="item-money">¥ {{ node.money.toLocaleString(localeTag) }}</span>
            </div>
          </template>
          <template v-else>
            <div v-for="(node, i) in budgetData[cat]" :key="i" class="item-row edit-row">
              <input class="item-name-in" v-model="node.name" />
              <div class="item-money-in">
                <span>¥</span>
                <input type="number" :value="node.money" @input="updateMoney(cat, i, ($event.target as HTMLInputElement).value)" />
              </div>
              <button class="del-btn" @click="deleteItem(cat, i)" :title="t('control.bill.delete')">🗑</button>
            </div>
            <button class="add-btn" @click="addItem(cat)">{{ t('control.bill.addItem') }}</button>
          </template>
        </div>

        <div class="bill-foot">
          {{ t('control.bill.subtotal') }}<b>¥ {{ categorySubtotal(cat).toLocaleString(localeTag) }}</b>
        </div>
      </div>
    </div>

    <div class="cfo-tip">
      <span class="cfo-ico">📊</span>
      <span>
        {{ t('control.cfoPre') }}<strong>{{ t('control.cfoEmph') }}</strong>{{ t('control.cfoPost') }}
      </span>
    </div>

    <div class="ai-disclaimer">
      <span class="ai-disclaimer-icon">⚠️</span>
      <p><b>{{ t('common.aiRiskTitle') }}</b>{{ t('common.aiRiskSep') }}{{ t('common.aiRiskDesc') }}</p>
    </div>
  </div>
</template>

<style scoped>
.ctrl-root { display: flex; flex-direction: column; gap: 20px; }

/* link bar */
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
.eye-btn {
  background: transparent; border: none; cursor: pointer;
  width: 24px; height: 24px; padding: 0; line-height: 0;
  display: inline-flex; align-items: center; justify-content: center;
  border-radius: 4px; color: inherit; opacity: 0.7;
  transition: opacity 0.15s, background 0.15s;
}
.eye-btn:hover { opacity: 1; background: rgba(0,0,0,0.06); }

/* generic card */
.card {
  background: white; border-radius: var(--radius);
  box-shadow: var(--shadow);
  padding: 24px;
}
.card-header {
  display: flex; justify-content: space-between; align-items: flex-start;
  margin-bottom: 20px; padding-bottom: 16px;
  border-bottom: 1px solid var(--border-light);
}
.step-chip {
  display: inline-block;
  background: linear-gradient(135deg, #e6f4ff, #f0f5ff);
  color: var(--primary); font-size: 11px; font-weight: 600;
  padding: 3px 10px; border-radius: 12px; letter-spacing: 0.5px;
  text-transform: uppercase;
}
.setup-title { font-size: 17px; font-weight: 700; margin-top: 8px; color: var(--text); }
.ai-badge {
  background: linear-gradient(135deg, #1677ff, #4096ff);
  color: white; font-size: 11px; padding: 4px 12px; border-radius: 12px;
  font-weight: 500; white-space: nowrap;
}

/* setup grid */
.setup-grid {
  display: grid; gap: 16px;
  grid-template-columns: repeat(4, minmax(0, 1fr));
}
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

/* summary */
.summary-card {
  background: linear-gradient(135deg, #f0f7ff, #e6f4ff 60%, #f5f0ff);
  color: var(--text); border-radius: var(--radius); padding: 24px 28px;
  display: flex; justify-content: space-between; align-items: center;
  gap: 24px; flex-wrap: wrap;
  border: 1px solid #d6e8ff; box-shadow: var(--shadow);
}
.sum-left { display: flex; flex-direction: column; gap: 6px; }
.sum-name { display: flex; align-items: center; gap: 10px; }
.sum-title { font-size: 19px; font-weight: 700; letter-spacing: 0.3px; color: var(--text); }
.sum-type {
  font-size: 11px; padding: 2px 8px; border-radius: 4px;
  background: #e6f4ff; border: 1px solid #91caff; color: var(--primary);
}
.sum-meta { font-size: 12px; color: var(--text-secondary); }
.sum-meta b { color: var(--text); font-weight: 500; }
.sum-meta .em { color: var(--primary); font-weight: 700; }
.sum-meta .sep { margin: 0 8px; opacity: 0.4; }
.sum-right { display: flex; align-items: center; gap: 18px; }
.sum-budget-label { font-size: 10px; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 1px; }
.sum-budget-val { font-size: 28px; font-weight: 800; color: var(--primary); font-variant-numeric: tabular-nums; }
.btn-export {
  background: var(--primary); color: white; border: none;
  padding: 8px 14px; border-radius: 6px; font-size: 13px;
  font-weight: 600; cursor: pointer; transition: all 0.2s;
  box-shadow: 0 2px 8px rgba(22,119,255,0.4);
}
.btn-export:hover { background: var(--primary-hover); transform: translateY(-1px); }

/* charts */
.section-title h3 { font-size: 16px; font-weight: 700; color: var(--text); }
.section-title p { font-size: 12px; color: var(--text-secondary); margin-top: 2px; }
.chart-grid {
  display: grid; gap: 20px; margin-top: 12px;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
}
.chart-card { display: flex; flex-direction: column; height: 320px; padding: 16px 18px; }
.chart-h { font-size: 12px; font-weight: 600; color: var(--text-secondary); margin-bottom: 10px; letter-spacing: 0.3px; }
.chart-box { flex: 1; position: relative; min-height: 0; }

/* bill */
.bill-grid {
  display: grid; gap: 20px;
  grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
}
.bill-card { padding: 0; display: flex; flex-direction: column; overflow: hidden; transition: all 0.2s; }
.bill-card.unlocked { box-shadow: 0 0 0 2px var(--primary), var(--shadow-md); }
.bill-head {
  display: flex; justify-content: space-between; align-items: center;
  background: #fafafa; padding: 12px 16px; border-bottom: 1px solid var(--border-light);
}
.bill-cat { display: flex; align-items: center; gap: 10px; }
.bill-ico {
  width: 26px; height: 26px; border-radius: 6px;
  display: flex; align-items: center; justify-content: center; font-size: 13px;
}
.bill-name { font-size: 14px; font-weight: 600; }
.bill-lock {
  width: 32px; height: 32px; border-radius: 50%;
  border: 1px solid var(--border); background: white; cursor: pointer;
  font-size: 13px; transition: all 0.2s;
}
.bill-lock.on { background: var(--primary); border-color: var(--primary); color: white; }
.bill-items { padding: 14px 18px; display: flex; flex-direction: column; gap: 8px; flex: 1; }
.item-row {
  display: flex; justify-content: space-between; align-items: center;
  font-size: 13px; padding-bottom: 6px; border-bottom: 1px solid #f5f5f5;
}
.item-name { color: var(--text-secondary); }
.item-money { font-weight: 600; color: var(--text); font-variant-numeric: tabular-nums; }
.edit-row { gap: 8px; }
.item-name-in {
  flex: 1; min-width: 0; height: 30px; padding: 0 8px;
  border: 1px solid var(--border-light); background: #fafafa;
  border-radius: 4px; font-size: 12px; outline: none;
}
.item-name-in:focus { background: white; border-color: var(--primary); }
.item-money-in {
  display: flex; align-items: center; gap: 4px; width: 130px; flex-shrink: 0;
  height: 30px; padding: 0 8px; border: 1px solid var(--border-light);
  background: #fafafa; border-radius: 4px;
}
.item-money-in:focus-within { background: white; border-color: var(--primary); }
.item-money-in span { font-size: 11px; color: var(--text-secondary); }
.item-money-in input {
  flex: 1; min-width: 0; height: 100%; border: none; outline: none;
  text-align: right; font-size: 12px; font-weight: 600; background: transparent;
}
.del-btn {
  width: 26px; height: 26px; border: none; background: transparent;
  cursor: pointer; color: var(--text-secondary); border-radius: 4px; font-size: 12px;
}
.del-btn:hover { color: var(--error); background: #fff1f0; }
.add-btn {
  margin-top: 4px; width: 100%; padding: 6px;
  border: 1px dashed var(--border); background: transparent;
  border-radius: 6px; font-size: 12px; color: var(--text-secondary); cursor: pointer;
}
.add-btn:hover { border-color: var(--primary); color: var(--primary); }
.bill-foot {
  background: #fafafa; border-top: 1px solid var(--border-light);
  padding: 10px 18px; text-align: right; font-size: 12px; color: var(--text-secondary);
}
.bill-foot b { color: var(--text); font-size: 13px; }

/* cfo */
.cfo-tip {
  background: #f6ffed; border: 1px solid #eade70; color: #135200;
  padding: 14px 18px; border-radius: var(--radius);
  font-size: 13px; line-height: 1.7; display: flex; gap: 10px; align-items: flex-start;
}
.cfo-ico { font-size: 16px; flex-shrink: 0; }

@media (max-width: 900px) {
  .setup-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .field.col-2 { grid-column: span 2; }
}
@media (max-width: 600px) {
  .setup-grid { grid-template-columns: 1fr; }
  .field.col-2 { grid-column: span 1; }
}
</style>
