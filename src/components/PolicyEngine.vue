<script setup lang="ts">
import { ref, computed, reactive, watch } from 'vue'
import { sharedFormData } from '../store'

/* ---------------- 基础配置 ---------------- */

const industries = [
  '信息传输、软件和信息技术服务业',
  '科学研究和技术服务业',
  '制造业',
  '批发和零售业',
  '住宿和餐饮业',
  '金融业',
  '建筑业',
  '文化、体育和娱乐业',
  '其他服务业',
]

const PROVINCES = ['上海市', '北京市', '广东省', '浙江省', '其他区域']

type CategoryKey = '全部政策' | '资金补贴' | '税收减免' | '场地免租' | '金融信贷' | '人才落户'

interface CategoryStyle {
  hex: string
  light: string
  border: string
}

const policyCategories: Record<CategoryKey, CategoryStyle> = {
  '全部政策': { hex: '#475569', light: '#f1f5f9', border: '#cbd5e1' },
  '资金补贴': { hex: '#e11d48', light: '#fff1f2', border: '#fecdd3' },
  '税收减免': { hex: '#059669', light: '#ecfdf5', border: '#a7f3d0' },
  '场地免租': { hex: '#0891b2', light: '#ecfeff', border: '#a5f3fc' },
  '金融信贷': { hex: '#1677ff', light: '#e6f4ff', border: '#91caff' },
  '人才落户': { hex: '#7c3aed', light: '#f5f3ff', border: '#ddd6fe' },
}
const categoryKeys = Object.keys(policyCategories) as CategoryKey[]

type Priority = 'P0' | 'P1' | 'P2'
const priorityStyles: Record<Priority, { text: string; weight: number; color: string; bg: string; border: string }> = {
  P0: { text: 'P0 立即申请',   weight: 3, color: '#b91c1c', bg: '#fef2f2', border: '#fecaca' },
  P1: { text: 'P1 本季度重点', weight: 2, color: '#c2410c', bg: '#fff7ed', border: '#fed7aa' },
  P2: { text: 'P2 长期规划',   weight: 1, color: '#475569', bg: '#f8fafc', border: '#e2e8f0' },
}

interface PolicyDef {
  id: string
  title: string
  category: Exclude<CategoryKey, '全部政策'>
  maxValue: number | string
  valueUnit: string
  typeValue: number
  department: string
  prob: number
  cycle: string
  deadlineDays: number
  priority: Priority
  reqProv: string
  reqSizeMin: number
  reqCapMin: number
  reqInd: 'all' | number[]
  desc: string
}

const policyDatabase: PolicyDef[] = [
  {
    id: 'P-FUND-01', title: '首次创业一次性补贴', category: '资金补贴',
    maxValue: 8000, valueUnit: '户', typeValue: 8000,
    department: '上海市人社局', prob: 95, cycle: '2-3周', deadlineDays: 120,
    priority: 'P1',
    reqProv: '上海市', reqSizeMin: 1, reqCapMin: 0, reqInd: 'all',
    desc: '面向在上海市首次创办小微企业、个体工商户的本市户籍人员及符合条件的非本市户籍人员。企业注册成立满 6 个月且至少吸纳 1 名本市劳动者就业即可申请。',
  },
  {
    id: 'P-FUND-02', title: '稳岗扩岗及一次性吸纳就业补贴', category: '资金补贴',
    maxValue: 50000, valueUnit: '年', typeValue: 50000,
    department: '各地人社局', prob: 99, cycle: '免申即享', deadlineDays: 15,
    priority: 'P0',
    reqProv: 'all', reqSizeMin: 15, reqCapMin: 0, reqInd: 'all',
    desc: '鼓励企业吸纳高校毕业生及登记失业人员，当社保缴纳人数达标即可触发该项补贴，部分地区已实现后台比对"免申即享"。',
  },
  {
    id: 'P-SPACE-01', title: '初创期创业场地房租补贴', category: '场地免租',
    maxValue: 30000, valueUnit: '年', typeValue: 30000,
    department: '各区就业促进中心', prob: 80, cycle: '1-2个月', deadlineDays: 60,
    priority: 'P1',
    reqProv: 'all', reqSizeMin: 1, reqCapMin: 0, reqInd: 'all',
    desc: '针对入驻本市市级创业孵化示范基地的初创企业或创业团队。补贴标准最高2.8元/平方米/天，企业最长可享受 3 年补贴。',
  },
  {
    id: 'P-LOAN-01', title: '创业担保贷款及贴息', category: '金融信贷',
    maxValue: 3000000, valueUnit: '最高额度', typeValue: 300000,
    department: '市财政局 / 合作银行', prob: 65, cycle: '3-4周', deadlineDays: 365,
    priority: 'P2',
    reqProv: 'all', reqSizeMin: 1, reqCapMin: 0, reqInd: 'all',
    desc: '为缓解小微企业融资难，由政府提供担保基金并给予全额或部分贴息。小微企业最高可申请 300 万元，按时还本付息后可申请利息补贴。',
  },
  {
    id: 'P-TAX-01', title: '小微企业普惠性税收减免', category: '税收减免',
    maxValue: '全额返还', valueUnit: '企税优惠', typeValue: 150000,
    department: '国家税务总局', prob: 100, cycle: '汇算清缴期', deadlineDays: 45,
    priority: 'P1',
    reqProv: 'all', reqSizeMin: 1, reqCapMin: 0, reqInd: 'all',
    desc: '降低小微企业运营成本的普惠性国家与地方叠加政策。月销售额10万元以下小规模纳税人免征增值税；科技型中小企业研发费用加计扣除 100%。',
  },
  {
    id: 'P-TAX-02', title: '经济园区集群注册与返税', category: '税收减免',
    maxValue: '40%', valueUnit: '财政扶持', typeValue: 200000,
    department: '各区经济园区管委会', prob: 90, cycle: '按季度返还', deadlineDays: 365,
    priority: 'P2',
    reqProv: '上海市', reqSizeMin: 1, reqCapMin: 0, reqInd: 'all',
    desc: '郊区经济园区特有政策，适合轻资产服务型企业。提供免费虚拟注册地址，免除初期硬成本，并根据企业实际缴纳税额给予一定比例财政奖励。',
  },
  {
    id: 'P-TALENT-01', title: '临港/张江重点产业人才落户', category: '人才落户',
    maxValue: '3-5年', valueUnit: '居转户缩短', typeValue: 0,
    department: '临港管委会/人社局', prob: 50, cycle: '2-3个月', deadlineDays: 20,
    priority: 'P0',
    reqProv: '上海市', reqSizeMin: 5, reqCapMin: 100, reqInd: [0, 1, 2],
    desc: '针对特定区域和重点产业创业的核心团队。用人单位引进的紧缺急需人才可直接落户，享受专属人才公寓及租房补贴。',
  },
]

/* ---------------- 表单状态 + 联动 ---------------- */

const formState = reactive({
  industryIdx: 0,
  province: '上海市',
  namePref: '星禾云创',
  teamSize: 25,
  capital: 150,
})

const overridden = reactive<Record<keyof typeof formState, boolean>>({
  industryIdx: false, province: false, namePref: false, teamSize: false, capital: false,
})

function matchIndustryIdx(text: string): number {
  if (!text) return 0
  const lower = text.toLowerCase()
  const map: { kws: string[]; idx: number }[] = [
    { kws: ['软件', '互联网', 'saas', 'it', '信息', '科技', '数字'], idx: 0 },
    { kws: ['科研', '研究', '技术服务'], idx: 1 },
    { kws: ['制造', '工厂'], idx: 2 },
    { kws: ['批发', '零售', '电商'], idx: 3 },
    { kws: ['餐饮', '酒店', '住宿'], idx: 4 },
    { kws: ['金融', '银行', '保险', '证券'], idx: 5 },
    { kws: ['建筑', '工程'], idx: 6 },
    { kws: ['文化', '体育', '娱乐'], idx: 7 },
  ]
  for (const a of map) if (a.kws.some(k => lower.includes(k.toLowerCase()))) return a.idx
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
  if (f.business && !overridden.industryIdx) arr.push('行业')
  if (f.address && !overridden.province) arr.push('注册地')
  if (f.namePref && !overridden.namePref) arr.push('企业字号')
  if (typeof f.people === 'number' && f.people > 0 && !overridden.teamSize) arr.push('团队规模')
  if (f.capital && !overridden.capital) arr.push('认缴资本')
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

const currentCategory = ref<CategoryKey>('全部政策')
type PriorityFilter = 'ALL' | Priority
const currentPriority = ref<PriorityFilter>('ALL')
type SortMethod = 'priority' | 'amountDesc' | 'probDesc' | 'deadlineAsc'
const currentSort = ref<SortMethod>('priority')

interface MatchedPolicy extends PolicyDef {
  reasons: string[]
}

const matchedPolicies = computed<MatchedPolicy[]>(() => {
  const { industryIdx, province, teamSize, capital } = formState
  const industryName = industries[industryIdx] ?? ''

  const list: MatchedPolicy[] = []
  policyDatabase.forEach(policy => {
    if (policy.reqProv !== 'all' && policy.reqProv !== province) return
    if (teamSize < policy.reqSizeMin) return
    if (capital < policy.reqCapMin) return
    if (policy.reqInd !== 'all' && !policy.reqInd.includes(industryIdx)) return
    if (currentCategory.value !== '全部政策' && policy.category !== currentCategory.value) return
    if (currentPriority.value !== 'ALL' && policy.priority !== currentPriority.value) return

    const reasons: string[] = []
    if (policy.reqProv !== 'all') reasons.push(`${province} 属地注册`)
    if (policy.reqSizeMin > 1)    reasons.push(`规模 ${teamSize} 人 (要求≥${policy.reqSizeMin}人)`)
    if (policy.reqCapMin > 0)     reasons.push(`资本 ${capital} 万 (要求≥${policy.reqCapMin}万)`)
    if (policy.reqInd !== 'all')  reasons.push(`所属 ${industryName.substring(0, 4)} 等重点行业`)
    if (reasons.length === 0)     reasons.push('符合国家普惠性中小微企业标准')

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

const previewName = computed(() => `${formState.namePref || '未命名'}科技有限公司`)

function setCategory(c: CategoryKey) { currentCategory.value = c }

function formatValue(p: PolicyDef): { prefix: string; value: string } {
  if (typeof p.maxValue === 'number') {
    return { prefix: '最高预估', value: `¥ ${p.maxValue.toLocaleString()}` }
  }
  return { prefix: '', value: String(p.maxValue) }
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
          <span class="link-title">已同步「智能工商注册顾问」数据</span>
          <span class="link-fields">联动字段：{{ linkedFields.join(' / ') }}</span>
        </template>
        <template v-else>
          <span class="link-title">未检测到工商注册数据</span>
          <span class="link-fields">您可以在下方手动设置每个数值，触发匹配引擎</span>
        </template>
      </div>
      <button v-if="isLinked" class="link-reset" @click="resetLink">↻ 重新同步</button>
    </div>

    <!-- 沙盘参数（已联动则默认隐藏） -->
    <div v-show="setupVisible" class="card setup-card">
      <div class="card-header">
        <div>
          <span class="step-chip">1 / 完善企业画像，精准触发政策</span>
          <h3 class="setup-title">动态沙盘模拟参数</h3>
          <p class="setup-sub">修改下方参数，系统将毫秒级重算您的专属扶持政策与预估红利。</p>
        </div>
        <span class="ai-badge">📡 表单动态追随</span>
      </div>

      <div class="setup-grid">
        <div class="field col-2">
          <label>所属行业 (Industry)</label>
          <select v-model.number="formState.industryIdx" @change="markOverride('industryIdx')" class="input">
            <option v-for="(name, i) in industries" :key="i" :value="i">{{ name }}</option>
          </select>
        </div>

        <div class="field">
          <label>注册地 (Location)</label>
          <select v-model="formState.province" @change="markOverride('province')" class="input">
            <option v-for="p in PROVINCES" :key="p" :value="p">{{ p }}</option>
          </select>
        </div>

        <div class="field">
          <label>企业字号 (Name)</label>
          <input class="input" v-model="formState.namePref" @input="markOverride('namePref')" />
        </div>

        <div class="field">
          <label>当前规模 (Team Size)</label>
          <div class="num-box">
            <input type="number" min="1" v-model.number="formState.teamSize" @input="markOverride('teamSize')" />
            <span class="unit">人</span>
          </div>
        </div>

        <div class="field">
          <label>认缴资本 (Capital)</label>
          <div class="num-box">
            <input type="number" min="1" v-model.number="formState.capital" @input="markOverride('capital')" />
            <span class="unit">万元</span>
          </div>
        </div>

        <div class="field col-2 ready-strip">
          <span class="ready-text">📡 数据已按最新 <b>2026</b> 年度政务标准就绪</span>
          <span class="ready-pulse"><span /><span /><span /></span>
        </div>
      </div>
    </div>

    <!-- 总览看板 -->
    <div class="summary-card">
      <div class="sum-left">
        <div class="sum-name">
          <span class="sum-title">{{ previewName }}</span>
          <button class="eye-btn" @click="setupVisible = !setupVisible" :title="setupVisible ? '收起参数' : '展开参数'">
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
          注册地：<b>{{ formState.province }}</b>
          <span class="sep">·</span>
          行业：<b>{{ industries[formState.industryIdx] }}</b>
          <span class="sep">·</span>
          规模 <b class="em">{{ formState.teamSize }}</b> 人
          <span class="sep">·</span>
          认缴 <b class="em">{{ formState.capital }}</b> 万
        </div>
      </div>

      <div class="sum-right">
        <div class="sum-stat">
          <div class="sum-stat-label">匹配政策总数</div>
          <div class="sum-stat-val">{{ matchedPolicies.length }} <span>项</span></div>
        </div>
        <div class="sum-stat danger">
          <div class="sum-stat-label">可触达最高红利</div>
          <div class="sum-stat-val red">¥ {{ matchedSum.toLocaleString() }}</div>
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
        >{{ cat }}</button>
      </div>

      <div class="filters">
        <div class="select-wrap">
          <select v-model="currentPriority" class="input">
            <option value="ALL">全部优先级</option>
            <option value="P0">P0 立即申请</option>
            <option value="P1">P1 本季度重点</option>
            <option value="P2">P2 长期规划</option>
          </select>
        </div>
        <div class="select-wrap">
          <select v-model="currentSort" class="input">
            <option value="priority">默认排序 (按优先级)</option>
            <option value="amountDesc">红利金额 (从高到低)</option>
            <option value="probDesc">获批概率 (从高到低)</option>
            <option value="deadlineAsc">截止日期 (从近到远)</option>
          </select>
        </div>
      </div>
    </div>

    <!-- 政策卡片 -->
    <div v-if="matchedPolicies.length === 0" class="empty">
      <div class="empty-ico">📭</div>
      <h4>当前筛选条件下暂无匹配政策</h4>
      <p>尝试放宽优先级或切换政策类别，也可以在沙盘中调整企业参数以解锁更多政策。</p>
    </div>

    <div v-else class="policy-grid">
      <div
        v-for="policy in matchedPolicies"
        :key="policy.id"
        class="policy-card"
        :style="{ borderLeftColor: policyCategories[policy.category].hex }"
      >
        <div class="pc-head">
          <h4 class="pc-title">{{ policy.title }}</h4>
          <span
            class="pc-priority"
            :style="{ color: priorityStyles[policy.priority].color, background: priorityStyles[policy.priority].bg, borderColor: priorityStyles[policy.priority].border }"
          >{{ priorityStyles[policy.priority].text }}</span>
        </div>

        <div class="pc-board">
          <div class="pc-board-top">
            <div class="pc-value">
              <span v-if="formatValue(policy).prefix" class="pc-value-prefix">{{ formatValue(policy).prefix }}</span>
              <span class="pc-value-num" :style="{ color: policyCategories[policy.category].hex }">{{ formatValue(policy).value }}</span>
              <span class="pc-value-unit">/ {{ policy.valueUnit }}</span>
            </div>
            <div class="pc-deadline">
              <div class="pc-deadline-label">距截止</div>
              <div class="pc-deadline-num" :style="{ color: deadlineColor(policy.deadlineDays) }">
                <span v-if="policy.deadlineDays <= 15" class="fire">🔥</span>{{ policy.deadlineDays }} <span class="dim">天</span>
              </div>
            </div>
          </div>
          <div class="pc-board-bottom">
            <span>通过率：<b :style="{ color: probColor(policy.prob) }">{{ policy.prob }}%</b></span>
            <span class="sep">·</span>
            <span>周期：<b>{{ policy.cycle }}</b></span>
          </div>
        </div>

        <div class="pc-reasons">
          <div class="pc-reasons-title">✨ AI 动态参数匹配</div>
          <div class="pc-reasons-list">
            <span v-for="(r, idx) in policy.reasons" :key="idx" class="pc-reason">
              <span class="check">✓</span>{{ r }}
            </span>
          </div>
        </div>

        <p class="pc-desc">{{ policy.desc }}</p>

        <div class="pc-foot">
          <div class="pc-dept" :style="{ color: policyCategories[policy.category].hex }">
            🏛️ <span>{{ policy.department }}</span>
          </div>
          <button class="pc-apply">启动申报 →</button>
        </div>
      </div>
    </div>

    <div class="ai-disclaimer">
      <span class="ai-disclaimer-icon">⚠️</span>
      <p><b>AI生成风险提示</b>：内容基于现行法律法规，具体操作请结合当地市场监管部门、银行及税务机关的最新要求执行，建议在重大决策前咨询专业律师或行业顾问。</p>
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
