<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount, watch, nextTick, reactive } from 'vue'
import { Chart, registerables } from 'chart.js'
import type { ChartType } from 'chart.js'
import { sharedFormData } from '../store'

Chart.register(...registerables)

/* ---------------- 行业 / 成本矩阵 ---------------- */

const industries = [
  '农、林、牧、渔业', '采矿业', '制造业', '电力、热力、燃气及水生产和供应业', '建筑业',
  '批发和零售业', '交通运输、仓储和邮政业', '住宿和餐饮业', '信息传输、软件和信息技术服务业', '金融业',
  '房地产业', '租赁和商务服务业', '科学研究和技术服务业', '水利、环境和公共设施管理业', '居民服务、修理和其他服务业',
  '教育', '卫生和社会工作', '文化、体育和娱乐业', '公共管理、社会保障和社会组织', '国际组织',
]

type Tier = '0–10%' | '10–30%' | '30%以上'

interface CostRow {
  category: string
  item: string
  values: Tier[]
}

function normTier(v: string): Tier {
  if (v.includes('30%')) return '30%以上'
  if (v.includes('10')) return '10–30%'
  return '0–10%'
}

const RAW_STRUCTURE: { category: string; item: string; values: string[] }[] = [
  { category: '合规与制度成本', item: '注册/设立/基础合规', values: ['10–30%','30%以上','10–30%','30%以上','10–30%','0–10%','10–30%','10–30%','10–30%','30%以上','30%以上','10–30%','10–30%','30%以上','0–10%','10–30%','30%以上','10–30%','30%以上','30%以上'] },
  { category: '合规与制度成本', item: '行业资质/许可证', values: ['10–30%','30%以上','30%以上','30%以上','30%以上','0–10%','30%以上','30%以上','10–30%','30%以上','30%以上','10–30%','10–30%','30%以上','10–30%','30%以上','30%以上','10–30%','30%以上','30%以上'] },
  { category: '合规与制度成本', item: '法律/税务基础服务', values: ['10–30%','30%以上','10–30%','10–30%','10–30%','10–30%','10–30%','10–30%','10–30%','30%','30%以上','10–30%','10–30%','10–30%','0–10%','10–30%','10–30%','10–30%','30%以上','30%以上'] },
  { category: '空间与基础设施成本', item: '办公租金', values: ['0–10%','10–30%','10–30%','10–30%','10–30%','30%以上','10–30%','30%以上','10–30%','30%以上','30%以上','30%以上','10–30%','10–30%','10–30%','10–30%','30%以上','10–30%','10–30%','10–30%'] },
  { category: '空间与基础设施成本', item: '门店/工厂/仓库', values: ['10–30%','30%以上','30%以上','30%以上','10–30%','30%以上','30%以上','30%以上','0–10%','0–10%','30%以上','10–30%','0–10%','10–30%','10–30%','0–10%','30%以上','10–30%','0–10%','0–10%'] },
  { category: '空间与基础设施成本', item: '设备折旧/硬件资产', values: ['10–30%','30%以上','30%以上','30%以上','10–30%','10–30%','30%以上','10–30%','0–10%','10–30%','10–30%','0–10%','10–30%','30%以上','10–30%','10–30%','30%以上','10–30%','10–30%','10–30%'] },
  { category: '空间与基础设施成本', item: '仓储/冷链/物理设施', values: ['30%以上','10–30%','30%以上','10–30%','10–30%','30%以上','30%以上','10–30%','0–10%','0–10%','10–30%','0–10%','0–10%','10–30%','0–10%','0–10%','10–30%','0–10%','0–10%','0–10%'] },
  { category: '数字化与软件成本', item: 'SaaS订阅（CRM/ERP/HRM）', values: ['0–10%','0–10%','10–30%','10–30%','10–30%','10–30%','10–30%','0–10%','30%以上','30%以上','10–30%','30%以上','30%以上','10–30%','10–30%','10–30%','10–30%','10–30%','10–30%','10–30%'] },
  { category: '数字化与软件成本', item: '云服务/服务器/CDN', values: ['0–10%','0–10%','0–10%','0–10%','0–10%','0–10%','10–30%','0–10%','30%以上','30%以上','10–30%','10–30%','30%以上','10–30%','0–10%','10–30%','10–30%','30%以上','10–30%','30%以上'] },
  { category: '数字化与软件成本', item: '系统开发/DevOps/IT工具', values: ['0–10%','0–10%','10–30%','10–30%','0–10%','0–10%','10–30%','0–10%','30%以上','30%以上','10–30%','10–30%','30%以上','10–30%','0–10%','10–30%','10–30%','30%以上','10–30%','30%以上'] },
  { category: '数字化与软件成本', item: 'API/AI工具/自动化', values: ['0–10%','0–10%','0–10%','0–10%','0–10%','0–10%','10–30%','0–10%','30%以上','30%以上','10–30%','10–30%','30%以上','10–30%','0–10%','10–30%','10–30%','30%以上','10–30%','30%以上'] },
  { category: '人力与组织运营成本', item: '人力成本（核心团队）', values: ['10–30%','10–30%','10–30%','10–30%','30%以上','10–30%','10–30%','30%以上','30%以上','30%以上','10–30%','30%以上','30%以上','10–30%','30%以上','30%以上','30%以上','30%以上','30%以上','30%以上'] },
  { category: '人力与组织运营成本', item: '客服/售后', values: ['0–10%','0–10%','10–30%','10–30%','10–30%','30%以上','30%以上','30%以上','10–30%','30%以上','10–30%','10–30%','10–30%','10–30%','30%以上','10–30%','30%以上','10–30%','10–30%','10–30%'] },
  { category: '人力与组织运营成本', item: '运营管理成本', values: ['10–30%','10–30%','10–30%','10–30%','30%以上','10–30%','30%','30%以上','30%以上','30%以上','30%以上','30%以上','30%以上','30%以上','10–30%','30%以上','30%以上','30%以上','30%以上','30%以上'] },
  { category: '人力与组织运营成本', item: '差旅/培训', values: ['0–10%','10–30%','10–30%','0–10%','30%以上','0–10%','10–30%','0–10%','10–30%','10–30%','10–30%','10–30%','30%以上','10–30%','0–10%','10–30%','10–30%','10–30%','10–30%','30%以上'] },
  { category: '增长与市场获取成本', item: '广告投放/获客', values: ['0–10%','0–10%','10–30%','0–10%','0–10%','30%以上','10–30%','30%以上','30%以上','10–30%','10–30%','10–30%','10–30%','0–10%','10–30%','30%以上','0–10%','30%以上','0–10%','0–10%'] },
  { category: '增长与市场获取成本', item: '渠道/平台佣金', values: ['0–10%','0–10%','10–30%','0–10%','0–10%','30%以上','10–30%','30%以上','10–30%','0–10%','0–10%','10–30%','0–10%','0–10%','10–30%','10–30%','0–10%','30%以上','0–10%','0–10%'] },
  { category: '增长与市场获取成本', item: '销售佣金', values: ['0–10%','10–30%','10–30%','10–30%','10–30%','30%以上','10–30%','10–30%','30%以上','30%以上','30%以上','30%以上','10–30%','0–10%','10–30%','10–30%','0–10%','30%以上','0–10%','0–10%'] },
  { category: '增长与市场获取成本', item: '品牌/内容营销', values: ['0–10%','0–10%','0–10%','0–10%','0–10%','10–30%','10–30%','30%以上','30%以上','10–30%','10–30%','10–30%','10–30%','0–10%','10–30%','30%以上','0–10%','30%以上','0–10%','10–30%'] },
  { category: '风险与损耗成本', item: '退货/损耗/坏账', values: ['30%以上','10–30%','10–30%','0–10%','10–30%','30%以上','10–30%','30%以上','0–10%','10–30%','10–30%','0–10%','0–10%','0–10%','10–30%','0–10%','10–30%','10–30%','0–10%','0–10%'] },
  { category: '风险与损耗成本', item: '库存积压/浪费', values: ['30%以上','10–30%','30%以上','10–30%','0–10%','30%以上','10–30%','30%以上','0–10%','0–10%','30%以上','0–10%','0–10%','0–10%','0–10%','0–10%','10–30%','0–10%','0–10%','0–10%'] },
  { category: '风险与损耗成本', item: '法律风险/罚款', values: ['10–30%','30%以上','10–30%','30%以上','30%以上','10–30%','10–30%','10–30%','30%以上','30%以上','30%以上','10–30%','10–30%','30%以上','10–30%','10–30%','30%以上','10–30%','30%以上','30%以上'] },
  { category: '风险与损耗成本', item: '保险/汇率/波动损失', values: ['30%以上','30%以上','10–30%','10–30%','10–30%','10–30%','30%以上','10–30%','0–10%','30%以上','10–30%','10–30%','0–10%','10–30%','0–10%','0–10%','10–30%','10–30%','0–10%','30%以上'] },
]

const costStructure: CostRow[] = RAW_STRUCTURE.map(r => ({
  category: r.category,
  item: r.item,
  values: r.values.map(normTier) as Tier[],
}))

interface CategoryMeta { icon: string; color: string; hex: string }
const categoriesMeta: Record<string, CategoryMeta> = {
  '合规与制度成本':     { icon: '⚖️', color: '#6366f1', hex: '#6366f1' },
  '空间与基础设施成本': { icon: '🏢', color: '#3b82f6', hex: '#3b82f6' },
  '数字化与软件成本':   { icon: '💻', color: '#06b6d4', hex: '#06b6d4' },
  '人力与组织运营成本': { icon: '👥', color: '#10b981', hex: '#10b981' },
  '增长与市场获取成本': { icon: '📈', color: '#f59e0b', hex: '#f59e0b' },
  '风险与损耗成本':     { icon: '🛡️', color: '#f43f5e', hex: '#f43f5e' },
}
const categoryOrder = Object.keys(categoriesMeta)

/* ---------------- 表单状态 + 联动 ---------------- */

const PROVINCES = ['北京市', '上海市', '广东省', '浙江省', '其他区域']
const COMPANY_TYPES = ['有限责任公司', '股份有限公司', '合伙企业']

const formState = reactive({
  industryIdx: 8,
  teamSize: 10,
  shareholder: 3,
  province: '北京市',
  companyType: '有限责任公司',
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

function matchIndustryIdx(text: string): number {
  if (!text) return 8
  const lower = text.toLowerCase()
  const aliases: { kws: string[]; idx: number }[] = [
    { kws: ['农', '林', '牧', '渔'], idx: 0 },
    { kws: ['矿'], idx: 1 },
    { kws: ['制造', '工厂'], idx: 2 },
    { kws: ['电力', '燃气', '水务'], idx: 3 },
    { kws: ['建筑', '工程'], idx: 4 },
    { kws: ['批发', '零售', '电商'], idx: 5 },
    { kws: ['物流', '仓储', '运输', '邮政'], idx: 6 },
    { kws: ['餐饮', '酒店', '住宿'], idx: 7 },
    { kws: ['软件', '互联网', 'saas', 'it', '信息', '科技', '数字'], idx: 8 },
    { kws: ['金融', '银行', '保险', '证券'], idx: 9 },
    { kws: ['房地产', '地产'], idx: 10 },
    { kws: ['租赁', '商务服务', '咨询'], idx: 11 },
    { kws: ['科研', '研究', '技术服务'], idx: 12 },
    { kws: ['环境', '环保', '公共设施'], idx: 13 },
    { kws: ['居民服务', '维修', '修理'], idx: 14 },
    { kws: ['教育', '培训'], idx: 15 },
    { kws: ['卫生', '医疗', '社会工作'], idx: 16 },
    { kws: ['文化', '体育', '娱乐'], idx: 17 },
    { kws: ['公共管理', '社保'], idx: 18 },
    { kws: ['国际组织'], idx: 19 },
  ]
  for (const a of aliases) if (a.kws.some(k => lower.includes(k.toLowerCase()))) return a.idx
  return 8
}

function matchProvince(addr: string): string {
  if (!addr) return '其他区域'
  if (addr.includes('北京')) return '北京市'
  if (addr.includes('上海')) return '上海市'
  if (addr.includes('广东') || addr.includes('深圳') || addr.includes('广州')) return '广东省'
  if (addr.includes('浙江') || addr.includes('杭州') || addr.includes('宁波')) return '浙江省'
  return '其他区域'
}

function matchCompanyType(t: string): string {
  if (!t) return '有限责任公司'
  if (t.includes('股份')) return '股份有限公司'
  if (t.includes('合伙')) return '合伙企业'
  return '有限责任公司'
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
  if (f.business && !overridden.industryIdx) arr.push('行业')
  if (typeof f.people === 'number' && f.people > 0 && !overridden.teamSize) arr.push('团队规模')
  if (typeof f.shareholder === 'number' && f.shareholder > 0 && !overridden.shareholder) arr.push('股东人数')
  if (f.address && !overridden.province) arr.push('注册区域')
  if (f.companyType && !overridden.companyType) arr.push('公司类型')
  if (f.namePref && !overridden.namePref) arr.push('企业字号')
  if (f.capital && !overridden.capital) arr.push('认缴资本')
  if (f.scope && typeof f.scope === 'object') {
    if (f.scope.main && !overridden.scopeMain) arr.push('主营范围')
    if (f.scope.others?.length && !overridden.scopeOthers) arr.push('兼营范围')
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

const previewName = computed(() => `${formState.namePref}科技${formState.companyType === '股份有限公司' ? '股份' : ''}有限公司`)

const setupVisible = ref(false)
watch(isLinked, v => { setupVisible.value = !v }, { immediate: true })

/* ---------------- 预算计算 ---------------- */

interface BudgetItem { name: string; money: number }
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

  const locMul = (province === '北京市' || province === '上海市') ? 1.45
    : province === '其他区域' ? 0.8 : 1.0

  let totalWeight = 0
  const weights = costStructure.map(row => {
    const tier = row.values[industryIdx]
    let w = 0.35
    if (tier === '30%以上') w = 3.5
    else if (tier === '10–30%') w = 1.5
    totalWeight += w
    return { category: row.category, item: row.item, weight: w }
  })

  const humanCoreW = weights.find(i => i.item === '人力成本（核心团队）')!.weight
  const initialTotal = (coreHRBase / humanCoreW) * totalWeight

  const next: BudgetByCategory = {}
  const bench: Record<string, number> = {}
  categoryOrder.forEach(c => { next[c] = []; bench[c] = 0 })

  weights.forEach((wi, idx) => {
    let money = (initialTotal / totalWeight) * wi.weight
    if (wi.item === '办公租金' || wi.item === '门店/工厂/仓库') money *= locMul
    if (wi.item === '注册/设立/基础合规' || wi.item === '法律/税务基础服务') {
      money += sh * 1500
      if (companyType === '股份有限公司') money *= 1.3
    }
    if (wi.item === '保险/汇率/波动损失' || wi.item === '法律风险/罚款') money += cap * 20

    const noise = Math.sin(idx + industryIdx + ts) * (money * 0.04)
    let final = Math.round(money + noise)
    if (final <= 0) final = Math.round(3500 + Math.abs(Math.sin(idx) * 2000))

    next[wi.category].push({ name: wi.item, money: final })
    bench[wi.category] += final
  })

  budgetData.value = next
  benchmark.value = bench
}

watch(() => ({ ...formState }), recomputeBudget, { immediate: true })

const totalBudget = computed(() =>
  categoryOrder.reduce((s, c) =>
    s + (budgetData.value[c]?.reduce((a, b) => a + b.money, 0) ?? 0), 0)
)
const fmt = (n: number) => '¥ ' + Math.round(n).toLocaleString('zh-CN')

/* ---------------- 卡片编辑 ---------------- */

function toggleLock(cat: string) { cardLocked[cat] = !cardLocked[cat] }
function addItem(cat: string) {
  const seed = Math.round(1200 + Math.random() * 8700)
  budgetData.value[cat].push({ name: '自定义新增科目', money: seed })
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
      pieLabels.push(c)
      pieData.push(subtotals[i])
      pieColors.push(categoriesMeta[c].hex)
    }
  })

  const shortLabels = cats.map(c =>
    c.replace('与基础设施成本', '')
      .replace('与组织运营成本', '')
      .replace('与市场获取成本', '')
      .replace('与制度成本', '')
      .replace('与软件成本', ''))

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
          { label: '当前方案', data: subtotals, fill: true, backgroundColor: 'rgba(22,119,255,0.15)', borderColor: '#1677ff', borderWidth: 1.8, pointBackgroundColor: '#1677ff' },
          { label: '行业基准', data: benchSubtotals, fill: false, borderColor: 'rgba(148,163,184,0.7)', borderDash: [4, 4], pointBackgroundColor: '#94a3b8' },
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

onMounted(() => { nextTick(rebuildCharts) })
onBeforeUnmount(() => {
  pie?.destroy(); radar?.destroy(); bar?.destroy()
  pie = radar = bar = null
})

/* ---------------- CSV 导出 ---------------- */

function exportCSV() {
  let csv = '﻿'
  csv += 'Lucky OS 工商数据联动一键生成成本预算报告\n'
  csv += `拟申报公司全称,${previewName.value}\n`
  csv += `对标行业分区,${industries[formState.industryIdx]}\n`
  csv += `拟注册地域,${formState.province}\n`
  csv += `规划核心规模,${formState.teamSize} 人\n\n`
  csv += '"成本一级体系","明细科目名称","预估首季现金流量(元)"\n'

  let overall = 0
  categoryOrder.forEach(cat => {
    let sub = 0
    budgetData.value[cat]?.forEach(n => {
      csv += `"${cat}","${n.name}",${n.money}\n`
      sub += n.money; overall += n.money
    })
    csv += `"${cat}","[${cat} - 小计汇总]",${sub}\n`
  })
  csv += `"\n[新公司开办首季启动资产储备总需求]","",${overall}\n`

  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = `LuckyOS_预算报告_${formState.namePref}_${industries[formState.industryIdx]}.csv`
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
          <span class="link-title">已同步「智能工商注册顾问」数据</span>
        </template>
        <template v-else>
          <span class="link-title">未检测到工商注册数据</span>
          <span class="link-fields">您可以直接在下方手动设置每个数值</span>
        </template>
      </div>
      <button v-if="isLinked" class="link-reset" @click="resetLink">↻ 重新同步</button>
    </div>

    <!-- 公司设立登记信息 -->
    <div v-show="setupVisible" class="card setup-card">
      <div class="card-header">
        <div>
          <span class="step-chip">第一步 · 规划基础行业与规模</span>
          <h3 class="setup-title">新公司设立登记信息</h3>
        </div>
        <span class="ai-badge">📡 表单动态追随</span>
      </div>

      <div class="setup-grid">
        <div class="field col-2">
          <label>对应标准行业 (business)</label>
          <select v-model.number="formState.industryIdx" @change="markOverride('industryIdx')" class="input">
            <option v-for="(name, i) in industries" :key="i" :value="i">
              {{ String.fromCharCode(65 + i) }} — {{ name }}
            </option>
          </select>
        </div>

        <div class="field">
          <label>团队规模 (people)</label>
          <div class="num-box">
            <input type="number" min="1" max="500" v-model.number="formState.teamSize" @input="markOverride('teamSize')" />
            <span class="unit">人</span>
          </div>
        </div>

        <div class="field">
          <label>股东人数 (shareholder)</label>
          <div class="num-box">
            <input type="number" min="1" max="50" v-model.number="formState.shareholder" @input="markOverride('shareholder')" />
            <span class="unit">个</span>
          </div>
        </div>

        <div class="field">
          <label>注册区域 (province)</label>
          <select v-model="formState.province" @change="markOverride('province')" class="input">
            <option v-for="p in PROVINCES" :key="p" :value="p">{{ p }}</option>
          </select>
        </div>

        <div class="field">
          <label>公司类型 (companyType)</label>
          <select v-model="formState.companyType" @change="markOverride('companyType')" class="input">
            <option v-for="t in COMPANY_TYPES" :key="t" :value="t">{{ t }}</option>
          </select>
        </div>

        <div class="field">
          <label>企业字号 (namePref)</label>
          <input class="input" v-model="formState.namePref" @input="markOverride('namePref')" />
        </div>

        <div class="field">
          <label>认缴资本 (capital)</label>
          <div class="num-box">
            <input type="number" min="1" v-model.number="formState.capital" @input="markOverride('capital')" />
            <span class="unit">万元</span>
          </div>
        </div>

        <div class="field col-2">
          <label>主营经营范围 (scope.main)</label>
          <input class="input" v-model="formState.scopeMain" @input="markOverride('scopeMain')" />
        </div>

        <div class="field col-2">
          <label>兼营范围摘要 (scope.others)</label>
          <input class="input" v-model="formState.scopeOthers" @input="markOverride('scopeOthers')" />
        </div>
      </div>
    </div>

    <!-- 总览栏 -->
    <div class="summary-card">
      <div class="sum-left">
        <div class="sum-name">
          <span class="sum-title">{{ previewName }}</span>
          <span class="sum-type">{{ formState.companyType }}</span>
          <button class="eye-btn" @click="setupVisible = !setupVisible" :title="setupVisible ? '收起设立信息' : '展开设立信息'">
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
          注册地：<b>{{ formState.province }}</b>
          <span class="sep">·</span>
          行业分区：<b>{{ industries[formState.industryIdx] }}</b>
          <span class="sep">·</span>
          组织配置：规模 <b class="em">{{ formState.teamSize }}</b> 人 / 股东 <b class="em">{{ formState.shareholder }}</b> 人
        </div>
      </div>
      <div class="sum-right">
        <div class="sum-budget">
          <div class="sum-budget-label">实时申报首季现金储备需求</div>
          <div class="sum-budget-val">{{ fmt(totalBudget) }}</div>
        </div>
        <button class="btn-export" @click="exportCSV">📄 导出报告</button>
      </div>
    </div>

    <!-- 图表 -->
    <div class="chart-section">
      <div class="section-title">
        <h3>预算流数据智能看板</h3>
        <p>多维度解构预算重心，实时透视与标准模型的偏离度</p>
      </div>
      <div class="chart-grid">
        <div class="card chart-card">
          <h4 class="chart-h">🥧 6 大成本体系结构占比</h4>
          <div class="chart-box"><canvas ref="pieEl" /></div>
        </div>
        <div class="card chart-card">
          <h4 class="chart-h">🛰️ 行业对标偏差雷达 (RMB)</h4>
          <div class="chart-box"><canvas ref="radarEl" /></div>
        </div>
        <div class="card chart-card">
          <h4 class="chart-h">📊 成本 Top 驱动项 (RMB)</h4>
          <div class="chart-box"><canvas ref="barEl" /></div>
        </div>
      </div>
    </div>

    <!-- 卡片明细 -->
    <div class="section-title">
      <h3>决策级科目细分账单（随上方表单实时重算）</h3>
      <p>点 🔓 即可进入沙盒自定义；更改省份或人数将自动基于矩阵权重全盘洗牌。</p>
    </div>

    <div class="bill-grid">
      <div v-for="cat in categoryOrder" :key="cat" class="card bill-card" :class="{ unlocked: !cardLocked[cat] }">
        <div class="bill-head">
          <div class="bill-cat">
            <span class="bill-ico" :style="{ background: categoriesMeta[cat].hex + '1a', color: categoriesMeta[cat].hex }">{{ categoriesMeta[cat].icon }}</span>
            <span class="bill-name">{{ cat }}</span>
          </div>
          <button class="bill-lock" :class="{ on: !cardLocked[cat] }" @click="toggleLock(cat)" :title="cardLocked[cat] ? '解锁编辑' : '锁定'">
            {{ cardLocked[cat] ? '🔒' : '🔓' }}
          </button>
        </div>

        <div class="bill-items">
          <template v-if="cardLocked[cat]">
            <div v-for="(node, i) in budgetData[cat]" :key="i" class="item-row">
              <span class="item-name">{{ node.name }}</span>
              <span class="item-money">¥ {{ node.money.toLocaleString() }}</span>
            </div>
          </template>
          <template v-else>
            <div v-for="(node, i) in budgetData[cat]" :key="i" class="item-row edit-row">
              <input class="item-name-in" v-model="node.name" />
              <div class="item-money-in">
                <span>¥</span>
                <input type="number" :value="node.money" @input="updateMoney(cat, i, ($event.target as HTMLInputElement).value)" />
              </div>
              <button class="del-btn" @click="deleteItem(cat, i)" title="删除">🗑</button>
            </div>
            <button class="add-btn" @click="addItem(cat)">+ 添加细分预算科目</button>
          </template>
        </div>

        <div class="bill-foot">
          小计：<b>¥ {{ categorySubtotal(cat).toLocaleString() }}</b>
        </div>
      </div>
    </div>

    <div class="cfo-tip">
      <span class="cfo-ico">📊</span>
      <span>
        以上成本为基于行业矩阵的<strong>模拟推演</strong>，实际支出因城市、供应商及谈判能力差异较大，建议逐项询价后修正。
      </span>
    </div>

    <div class="ai-disclaimer">
      <span class="ai-disclaimer-icon">⚠️</span>
      <p><b>AI生成风险提示</b>：内容基于现行法律法规，具体操作请结合当地市场监管部门、银行及税务机关的最新要求执行，建议在重大决策前咨询专业律师或行业顾问。</p>
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
