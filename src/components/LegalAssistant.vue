<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { apiFetch } from '../api/client'

const { t, tm } = useI18n()

type DocumentMeta = {
  id: string
  title: string
  filename: string
  downloadUrl: string
  available: boolean
}

type TemplateCard = {
  icon: string
  fileId: string
}

type TemplateGroup = {
  icon: string
  id: string
  cards: TemplateCard[]
}

const today = new Date()
const currentYear = ref(today.getFullYear())
const currentMonth = ref(today.getMonth())

const monthName = computed(() =>
  t('legal.monthLabel', { year: currentYear.value, month: (tm('legal.months') as string[])[currentMonth.value] }),
)

function prevMonth() {
  if (currentMonth.value === 0) { currentMonth.value = 11; currentYear.value-- }
  else currentMonth.value--
}
function nextMonth() {
  if (currentMonth.value === 11) { currentMonth.value = 0; currentYear.value++ }
  else currentMonth.value++
}

const eventDays = computed(() => {
  const daysInMonth = new Date(currentYear.value, currentMonth.value + 1, 0).getDate()
  return new Set([1, 15, daysInMonth])
})

function daysUntil(month: number, day: number): number {
  const todayMs = new Date(today.getFullYear(), today.getMonth(), today.getDate()).getTime()
  let target = new Date(today.getFullYear(), month, day)
  if (target.getTime() < todayMs) target = new Date(today.getFullYear() + 1, month, day)
  return Math.round((target.getTime() - todayMs) / 86400000)
}

const reminders = computed(() => {
  const base = new Date(today.getFullYear(), today.getMonth(), today.getDate()).getTime()
  let next15 = new Date(today.getFullYear(), today.getMonth(), 15)
  if (next15.getTime() <= base) next15 = new Date(today.getFullYear(), today.getMonth() + 1, 15)
  const taxDays = Math.round((next15.getTime() - base) / 86400000)
  return [
    { label: t('legal.reminders.annualReport.label'), date: t('legal.reminders.annualReport.date'), days: daysUntil(5, 30), icon: '📆' },
    { label: t('legal.reminders.taxFiling.label'), date: t('legal.reminders.taxFiling.date'), days: taxDays, icon: '📊' },
    { label: t('legal.reminders.socialSecurity.label'), date: t('legal.reminders.socialSecurity.date'), days: taxDays, icon: '🏦' },
  ]
})

const weekdays = computed(() => tm('legal.weekdays') as string[])

const calendarDays = computed(() => {
  const year = currentYear.value
  const month = currentMonth.value
  const firstDow = new Date(year, month, 1).getDay()
  const daysInMonth = new Date(year, month + 1, 0).getDate()
  const isCurrentMonth = year === today.getFullYear() && month === today.getMonth()
  const todayDate = today.getDate()
  const cells: Array<{ day: number | null; hasEvent: boolean; isToday: boolean }> = []
  // Mon-first offset
  const offset = firstDow === 0 ? 6 : firstDow - 1
  for (let i = 0; i < offset; i++) cells.push({ day: null, hasEvent: false, isToday: false })
  for (let d = 1; d <= daysInMonth; d++)
    cells.push({ day: d, hasEvent: eventDays.value.has(d), isToday: isCurrentMonth && d === todayDate })
  return cells
})

const documents = ref<Record<string, DocumentMeta>>({})
const documentsLoading = ref(true)

// 分组与卡片：id/icon/fileId 稳定，标题/副标题随语言切换（走 t('legal.groups.*') / t('legal.cards.<fileId>.*')）
const groups: TemplateGroup[] = [
  {
    icon: 'fas fa-user-check', id: 'hire',
    cards: [
      { icon: 'fas fa-envelope-open-text', fileId: 'offer-letter' },
      { icon: 'fas fa-clipboard-list', fileId: 'employment-condition' },
      { icon: 'fas fa-id-card', fileId: 'onboarding-form' },
      { icon: 'fas fa-pen-to-square', fileId: 'application-form' },
    ],
  },
  {
    icon: 'fas fa-handshake', id: 'contract',
    cards: [
      { icon: 'fas fa-file-contract', fileId: 'labor-contract' },
      { icon: 'fas fa-user-friends', fileId: 'part-time-agreement' },
      { icon: 'fas fa-lock', fileId: 'confidentiality-agreement' },
      { icon: 'fas fa-ban', fileId: 'non-compete-agreement' },
    ],
  },
  {
    icon: 'fas fa-chart-simple', id: 'manage',
    cards: [
      { icon: 'fas fa-table-list', fileId: 'salary-table' },
      { icon: 'fas fa-calendar-week', fileId: 'attendance-sheet' },
      { icon: 'fas fa-book', fileId: 'attendance-leave-policy' },
      { icon: 'fas fa-address-book', fileId: 'employee-roster' },
      { icon: 'fas fa-building', fileId: 'employee-handbook' },
      { icon: 'fas fa-chart-line', fileId: 'performance-review' },
    ],
  },
  {
    icon: 'fas fa-door-open', id: 'offboard',
    cards: [
      { icon: 'fas fa-user-minus', fileId: 'resignation-approval' },
      { icon: 'fas fa-user-xmark', fileId: 'dismissal-approval' },
      { icon: 'fas fa-certificate', fileId: 'departure-certificate' },
      { icon: 'fas fa-file-circle-xmark', fileId: 'contract-termination-notice' },
    ],
  },
]

const cardTitle = (fileId: string) => t(`legal.cards.${fileId}.title`)
const cardSub = (fileId: string) => t(`legal.cards.${fileId}.sub`)

const toastMessage = ref('')
let toastTimer: number | undefined

function showToast(message: string) {
  toastMessage.value = message
  if (toastTimer) window.clearTimeout(toastTimer)
  toastTimer = window.setTimeout(() => { toastMessage.value = '' }, 2800)
}

function startDownload(url: string, filename?: string) {
  const link = document.createElement('a')
  link.href = url
  if (filename) link.download = filename
  document.body.appendChild(link)
  link.click()
  link.remove()
}

function isCardAvailable(card: TemplateCard) {
  const document = documents.value[card.fileId]
  return documentsLoading.value || document?.available === true
}

async function loadDocuments() {
  try {
    const response = await apiFetch('/api/documents')
    if (!response.ok) throw new Error('documents catalog load failed')
    const payload = await response.json() as { documents: DocumentMeta[] }
    documents.value = Object.fromEntries(payload.documents.map(document => [document.id, document]))
  } catch (error) {
    console.error(error)
    showToast(t('legal.toast.catalogFail'))
  } finally {
    documentsLoading.value = false
  }
}

function handleDocumentDownload(card: TemplateCard) {
  const document = documents.value[card.fileId]
  if (!isCardAvailable(card)) {
    showToast(t('legal.toast.notFound', { title: cardTitle(card.fileId) }))
    return
  }

  startDownload(document?.downloadUrl ?? `/api/documents/${card.fileId}/download`, document?.filename)
  showToast(t('legal.toast.downloading', { title: cardTitle(card.fileId) }))
}

function handleDownloadAll() {
  startDownload('/api/documents/download-all', t('legal.download.zipName'))
  showToast(t('legal.download.toastAll'))
}

onMounted(loadDocuments)
</script>

<template>
  <div class="legal-root">
    <!-- 主网格：左侧模板区 + 右侧边栏 -->
    <div class="main-grid">
      <!-- 左侧：高频合同与文书 -->
      <div class="templates-section">
        <div class="section-header">
          <h2 class="section-h2"><i class="fas fa-file-signature"></i> {{ t('legal.sectionTitle') }}</h2>
        </div>

        <div v-for="g in groups" :key="g.id" class="group-block">
          <div class="group-title"><i :class="g.icon"></i> {{ t('legal.groups.' + g.id) }}</div>
          <div class="cards-grid">
            <button
              v-for="c in g.cards"
              :key="c.fileId"
              class="template-card"
              :class="{ unavailable: !isCardAvailable(c) }"
              :disabled="!isCardAvailable(c)"
              type="button"
              @click="handleDocumentDownload(c)"
            >
              <i :class="c.icon"></i>
              <h4>{{ cardTitle(c.fileId) }}</h4>
              <p>{{ cardSub(c.fileId) }}</p>
            </button>
          </div>
        </div>

        <div class="ai-disclaimer compact">
          <span class="ai-disclaimer-icon">⚠️</span>
          <p><b>{{ t('common.aiRiskTitle') }}</b>{{ t('common.aiRiskSep') }}{{ t('legal.disclaimer') }}</p>
        </div>
      </div>

      <!-- 右侧边栏 -->
      <div class="right-sidebar">
        <!-- 合规倒计时 -->
        <div class="sidebar-card">
          <div class="card-head">
            <span><i class="fas fa-hourglass-half"></i> {{ t('legal.sidebar.countdownTitle') }}</span>
            <i class="fas fa-bell"></i>
          </div>
          <div class="deadline-list">
            <div v-for="r in reminders" :key="r.label" class="deadline-item">
              <div>
                <span class="deadline-title">{{ r.icon }} {{ r.label }}</span><br>
                <span class="deadline-date">{{ r.date }}</span>
              </div>
              <div :class="['countdown', r.days <= 7 ? 'urgent' : r.days <= 15 ? 'soon' : '']">
                {{ r.days }}{{ t('legal.daysSuffix') }}
              </div>
            </div>
          </div>
          <div class="deadline-hint">{{ t('legal.sidebar.countdownHint') }}</div>
        </div>

        <!-- 合规日历 -->
        <div class="sidebar-card">
          <div class="card-head">
            <span><i class="fas fa-calendar-alt"></i> {{ t('legal.sidebar.calendarTitle') }}</span>
            <span class="view-link" style="background:none;padding:0;font-size:12px;">{{ t('legal.sidebar.viewAll') }} <i class="fas fa-chevron-right"></i></span>
          </div>
          <div class="cal-nav">
            <span class="cal-month-label">{{ monthName }}</span>
            <div class="cal-btns">
              <button class="cal-btn" @click="prevMonth">‹</button>
              <button class="cal-btn" @click="nextMonth">›</button>
            </div>
          </div>
          <div class="cal-grid">
            <div v-for="(d, di) in weekdays" :key="di" class="cal-weekday">{{ d }}</div>
            <div
              v-for="(cell, i) in calendarDays" :key="i"
              :class="['cal-day', { event: cell.hasEvent && !cell.isToday, today: cell.isToday, empty: !cell.day }]"
            >{{ cell.day ?? '' }}</div>
          </div>
          <div class="cal-legend">
            <span class="legend-item"><span class="dot event-dot"></span>{{ t('legal.sidebar.legendDeadline') }}</span>
            <span class="legend-item"><span class="dot today-dot"></span>{{ t('legal.sidebar.legendToday') }}</span>
          </div>
        </div>

        <!-- 一键下载 -->
        <div class="download-card">
          <button class="download-btn" @click="handleDownloadAll">
            <i class="fas fa-download"></i>
            <span>{{ t('legal.download.btn') }}</span>
            <i class="fas fa-arrow-right arrow-icon"></i>
          </button>
          <div class="download-hint">
            <i class="fas fa-file-zipper"></i> {{ t('legal.download.hint') }}
          </div>
        </div>
      </div>
    </div>

    <!-- Toast -->
    <Transition name="toast">
      <div v-if="toastMessage" class="toast">
        ⚡ {{ toastMessage }}
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.legal-root { display: flex; flex-direction: column; gap: 0; position: relative; }

.main-grid { display: grid; grid-template-columns: 1fr 300px; gap: 20px; }

/* ---- 左侧 ---- */
.templates-section { display: flex; flex-direction: column; gap: 20px; }

.section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px; }
.section-h2 { font-size: 16px; font-weight: 700; color: var(--text); display: inline-flex; align-items: center; gap: 8px; }
.section-h2 i { color: var(--primary); }
.view-link { font-size: 12px; font-weight: 500; color: var(--primary); cursor: default; }

.group-block { display: flex; flex-direction: column; gap: 10px; }
.group-title {
  font-size: 16px; font-weight: 600; color: var(--text);
  border-left: 3px solid var(--primary); padding-left: 10px;
  display: flex; align-items: center; gap: 8px;
}
.group-title i { color: var(--primary); }

.cards-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 14px; }
.template-card {
  background: white;
  border: 1px solid var(--border-light);
  border-radius: var(--radius); padding: 20px 16px 16px;
  cursor: pointer; transition: all 0.15s; box-shadow: var(--shadow);
  text-align: left; font-family: inherit;
}
.template-card i { font-size: 28px; color: var(--primary); margin-bottom: 12px; display: block; }
.template-card h4 { font-size: 14px; font-weight: 600; color: var(--text); margin-bottom: 4px; }
.template-card p { font-size: 12px; color: var(--text-secondary); }
.template-card:hover { border-color: var(--primary); box-shadow: var(--shadow-md); transform: translateY(-2px); }
.template-card:focus-visible { outline: 2px solid var(--primary); outline-offset: 2px; }
.template-card.unavailable {
  cursor: not-allowed; opacity: 0.55; transform: none;
}
.template-card.unavailable:hover { border-color: var(--border-light); box-shadow: var(--shadow); }

/* ---- 右侧 ---- */
.right-sidebar { display: flex; flex-direction: column; gap: 16px; }

.sidebar-card {
  background: white; border: 1px solid var(--border-light);
  border-radius: var(--radius); padding: 16px 18px; box-shadow: var(--shadow);
}
.card-head {
  display: flex; justify-content: space-between; align-items: center;
  font-weight: 600; font-size: 14px; color: var(--text);
  margin-bottom: 14px; padding-bottom: 12px; border-bottom: 1px solid var(--border-light);
}
.card-head i { color: var(--primary); }

.deadline-list { display: flex; flex-direction: column; gap: 8px; }
.deadline-item {
  display: flex; justify-content: space-between; align-items: center;
  background: #fafafa; padding: 9px 12px; border-radius: 6px;
  border: 1px solid var(--border-light);
}
.deadline-title { font-weight: 600; font-size: 13px; color: var(--text); }
.deadline-date { font-size: 11px; color: var(--text-secondary); margin-top: 2px; }
.countdown {
  font-weight: 700; font-size: 13px; background: var(--primary); color: white;
  padding: 2px 10px; border-radius: 4px; min-width: 44px; text-align: center;
}
.countdown.soon { background: var(--warning); }
.countdown.urgent { background: var(--error); }
.deadline-hint {
  font-size: 11px; color: var(--text-secondary); text-align: center;
  margin-top: 10px; padding-top: 10px; border-top: 1px solid var(--border-light);
}

/* calendar */
.cal-nav { display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px; }
.cal-month-label { font-weight: 600; font-size: 13px; color: var(--text); }
.cal-btns { display: flex; gap: 4px; }
.cal-btn {
  width: 26px; height: 26px; background: none; border: 1px solid var(--border);
  border-radius: 6px; cursor: pointer; font-size: 15px; color: var(--text-secondary);
  display: flex; align-items: center; justify-content: center;
}
.cal-btn:hover { border-color: var(--primary); color: var(--primary); }
.cal-grid { display: grid; grid-template-columns: repeat(7, 1fr); gap: 3px; }
.cal-weekday { text-align: center; font-size: 11px; color: var(--text-secondary); font-weight: 500; padding: 4px 0; }
.cal-day {
  aspect-ratio: 1; display: flex; align-items: center; justify-content: center;
  font-size: 12px; color: var(--text); border-radius: 6px;
}
.cal-day.event { background: #fff7ed; color: #c2410c; font-weight: 600; }
.cal-day.today { background: var(--primary); color: white; font-weight: 600; }
.cal-day.empty { pointer-events: none; }
.cal-legend { display: flex; gap: 12px; margin-top: 10px; padding-top: 10px; border-top: 1px solid var(--border-light); }
.legend-item { display: flex; align-items: center; gap: 5px; font-size: 11px; color: var(--text-secondary); }
.dot { width: 8px; height: 8px; border-radius: 50%; }
.event-dot { background: #fff7ed; border: 1px solid #fed7aa; }
.today-dot { background: var(--primary); }

/* download */
.download-card {
  background: white; border: 1px solid var(--border-light);
  border-radius: var(--radius); padding: 14px 16px; box-shadow: var(--shadow);
}
.download-btn {
  display: flex; align-items: center; gap: 10px;
  background: var(--primary); border: none; width: 100%;
  padding: 10px 16px; border-radius: var(--radius);
  color: white; font-weight: 600; font-size: 13px;
  cursor: pointer; transition: all 0.15s; font-family: inherit;
  box-shadow: 0 2px 8px rgba(22,119,255,0.35);
}
.download-btn i:first-child { font-size: 15px; }
.download-btn span { flex: 1; text-align: left; }
.arrow-icon { transition: transform 0.15s; font-size: 13px; }
.download-btn:hover { background: var(--primary-hover); transform: translateY(-1px); box-shadow: 0 4px 12px rgba(22,119,255,0.4); }
.download-btn:hover .arrow-icon { transform: translateX(4px); }
.download-hint { font-size: 11px; text-align: center; margin-top: 8px; color: var(--text-secondary); }

/* toast */
.toast {
  position: fixed; bottom: 28px; left: 50%; transform: translateX(-50%);
  background: var(--text); color: white;
  padding: 10px 22px; border-radius: 6px;
  font-size: 13px; font-weight: 500;
  box-shadow: var(--shadow-md); z-index: 9999; white-space: nowrap;
}
.toast-enter-active, .toast-leave-active { transition: opacity 0.25s, transform 0.25s; }
.toast-enter-from, .toast-leave-to { opacity: 0; transform: translateX(-50%) translateY(8px); }

@media (max-width: 900px) { .main-grid { grid-template-columns: 1fr; } }

.ai-disclaimer.compact { margin-top: 8px; }
</style>
