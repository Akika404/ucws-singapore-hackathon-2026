<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { StepData, BaseFormData } from './RegAdvisor.vue'

const { t } = useI18n()

const props = defineProps<{
  steps: StepData[]
  formData: BaseFormData
}>()

const emit = defineEmits<{ restart: [] }>()

// 公司人数为 1 人时展示 image_2，否则展示 image_1
const orgImage = computed(() => (props.formData.people === 1 ? '/image_2.png' : '/image_1.png'))

function getStepValue(stepId: string): string {
  const key = stepId === 'type' ? 'companyType' : stepId
  const v = (props.formData as any)[key]
  if (v == null || v === '') return '—'
  if (stepId === 'scope' && typeof v === 'object') {
    const others = Array.isArray(v.others) ? v.others.join(t('summary.othersSep')) : ''
    return others
      ? t('summary.scopeWithOthers', { main: v.main, others })
      : t('summary.scopeMain', { main: v.main })
  }
  return String(v)
}

const NON_ORG_STEPS = ['name', 'type', 'scope', 'capital', 'address']

// 完整流程 12 步：id/icon 稳定，title/desc 随语言切换
const FULL_FLOW = computed(() =>
  [
    { id: 'name', icon: '🔍' }, { id: 'scope', icon: '📋' }, { id: 'type', icon: '🏢' },
    { id: 'capital', icon: '💰' }, { id: 'address', icon: '📍' }, { id: 'org', icon: '🏗️' },
    { id: 'license', icon: '📄' }, { id: 'seal', icon: '🔏' }, { id: 'bank', icon: '🏦' },
    { id: 'tax', icon: '🧾' }, { id: 'social', icon: '🛡️' }, { id: 'operate', icon: '🚀' },
  ].map(s => ({ ...s, title: t(`summary.flow.${s.id}.title`), desc: t(`summary.flow.${s.id}.desc`) })),
)

function exportPdf() {
  window.print()
}
</script>

<template>
  <div class="summary-wrap">
    <!-- Header -->
    <div class="header-card">
      <div class="header-left">
        <div class="header-badge">{{ t('summary.badge') }}</div>
        <h1 class="header-title">{{ t('summary.title') }}</h1>
        <p class="header-sub">{{ t('summary.subtitle') }}</p>
      </div>
      <div class="header-actions">
        <button class="btn-ghost no-print" @click="emit('restart')">{{ t('summary.reconfigure') }}</button>
        <button class="btn-export no-print" @click="exportPdf">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
          {{ t('summary.exportPdf') }}
        </button>
      </div>
    </div>

    <!-- Full registration flow -->
    <div class="flow-panel">
      <div class="panel-title">{{ t('summary.fullFlowTitle') }}</div>
      <div class="flow-list">
        <div
          v-for="(step, i) in FULL_FLOW"
          :key="step.id"
          class="flow-card"
          :class="{ 'flow-card-org': step.id === 'org' }"
        >
          <div class="flow-num">{{ i + 1 }}</div>
          <div class="flow-head">
            <span class="flow-icon">{{ step.icon }}</span>
            <span class="flow-title">{{ step.title }}</span>
          </div>
          <div class="flow-desc">{{ step.desc }}</div>
        </div>
      </div>
    </div>

    <!-- Info + Org layout (vertical stack) -->
    <div class="main-layout">
      <!-- step results -->
      <div class="info-panel">
        <div class="panel-title">{{ t('summary.detailTitle') }}</div>
        <div
          v-for="step in steps.filter(s => NON_ORG_STEPS.includes(s.id))"
          :key="step.id"
          class="info-row"
        >
          <div class="row-meta">
            <span class="row-icon">{{ step.icon }}</span>
            <span class="row-label">{{ t(`summary.labels.${step.id}`) }}</span>
          </div>
          <div class="row-value">{{ getStepValue(step.id) }}</div>
        </div>
      </div>

      <!-- org chart -->
      <div class="org-panel">
        <div class="panel-title">{{ t('summary.orgTitle') }}</div>
        <div class="org-img-wrap">
          <img :src="orgImage" :alt="t('summary.orgAlt')" class="org-img" />
        </div>
      </div>
    </div>

    <!-- Footer -->
    <div class="footer-note">
      <span class="note-dot">💡</span>
      {{ t('summary.footer') }}
    </div>
  </div>
</template>

<style scoped>
.summary-wrap {
  display: flex;
  flex-direction: column;
  gap: 20px;
  width: 100%;
  max-width: 1080px;
  margin: 0 auto;
}

/* ── Header ── */
.header-card {
  position: relative;
  overflow: hidden;
  background: linear-gradient(135deg, #0f52ba 0%, #1677ff 55%, #4096ff 100%);
  border-radius: var(--radius);
  padding: 32px 36px;
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 24px;
  color: white;
  box-shadow: 0 6px 24px rgba(22,119,255,0.35);
}
.header-card::before {
  content: '';
  position: absolute;
  top: -40px; right: -40px;
  width: 200px; height: 200px;
  border-radius: 50%;
  background: rgba(255,255,255,0.06);
  pointer-events: none;
}
.header-card::after {
  content: '';
  position: absolute;
  bottom: -60px; right: 80px;
  width: 160px; height: 160px;
  border-radius: 50%;
  background: rgba(255,255,255,0.04);
  pointer-events: none;
}
.header-badge {
  display: inline-flex;
  align-items: center;
  height: 22px;
  padding: 0 12px;
  background: rgba(255,255,255,0.18);
  border: 1px solid rgba(255,255,255,0.3);
  border-radius: 999px;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.8px;
  margin-bottom: 10px;
}
.header-title { font-size: 24px; font-weight: 800; margin: 0 0 6px; line-height: 1.2; }
.header-sub { font-size: 13px; opacity: 0.8; margin: 0; }
.header-actions { display: flex; gap: 10px; flex-shrink: 0; align-items: center; position: relative; z-index: 1; }

.btn-ghost {
  background: rgba(255,255,255,0.12);
  border: 1px solid rgba(255,255,255,0.35);
  color: white;
  padding: 0 16px;
  height: 36px;
  border-radius: 8px;
  font-size: 13px;
  cursor: pointer;
  transition: background 0.2s;
}
.btn-ghost:hover { background: rgba(255,255,255,0.22); }
.btn-export {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  background: white;
  color: #1677ff;
  border: none;
  padding: 0 20px;
  height: 36px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  box-shadow: 0 2px 10px rgba(0,0,0,0.15);
  transition: box-shadow 0.2s, transform 0.15s;
}
.btn-export:hover { transform: translateY(-1px); box-shadow: 0 4px 16px rgba(0,0,0,0.2); }

/* ── Main layout (vertical stack) ── */
.main-layout {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* ── Org panel: constrain image width so it doesn't stretch full-width ── */
.org-img-wrap {
  padding: 20px;
  background: #f8fafc;
  display: flex;
  justify-content: center;
}
.org-img {
  display: block;
  max-width: 760px;
  width: 100%;
  border-radius: 8px;
  border: 1px solid var(--border-light);
  object-fit: contain;
}

/* ── Shared panel ── */
.info-panel,
.org-panel,
.flow-panel {
  background: white;
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  overflow: hidden;
}
.panel-title {
  font-size: 13px;
  font-weight: 700;
  color: var(--text-secondary);
  letter-spacing: 0.4px;
  padding: 16px 22px 14px;
  border-bottom: 1px solid var(--border-light);
  background: #fafbfc;
}

/* ── Info rows ── */
.info-row {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 16px 22px;
  border-bottom: 1px solid var(--border-light);
  transition: background 0.15s;
}
.info-row:last-child { border-bottom: none; }
.info-row:hover { background: #f8faff; }
.row-meta {
  display: flex;
  align-items: center;
  gap: 7px;
}
.row-icon { font-size: 14px; }
.row-label {
  font-size: 11.5px;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.row-value {
  font-size: 14px;
  font-weight: 600;
  color: var(--text);
  line-height: 1.6;
  padding-left: 21px;
  word-break: break-all;
}

/* ── Flow timeline (horizontal cards) ── */
.flow-list {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  align-items: stretch;
  column-gap: 26px;
  row-gap: 28px;
  padding: 36px 28px 40px;
}
.flow-card {
  position: relative;
  background: linear-gradient(160deg, #ffffff 0%, #f5f8ff 100%);
  border: 1px solid var(--border-light);
  border-radius: 14px;
  padding: 18px 14px 16px;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  box-shadow: 0 2px 8px rgba(15, 38, 86, 0.05);
  transition: border-color 0.18s, box-shadow 0.18s, transform 0.18s;
}
/* Connector arrow centered in the gap to the right of each card */
.flow-card::after {
  content: '';
  position: absolute;
  left: 100%;
  top: 50%;
  width: 8px;
  height: 8px;
  margin-left: 9px;
  border-top: 2px solid #4096ff;
  border-right: 2px solid #4096ff;
  transform: translateY(-50%) rotate(45deg);
}
/* No arrow after the last card in each row (6 cols) or the very last card */
.flow-card:nth-child(6n)::after,
.flow-card:last-child::after {
  display: none;
}
@media (hover: hover) {
  .flow-card:hover {
    border-color: #91caff;
    box-shadow: 0 8px 20px rgba(22,119,255,0.16);
    transform: translateY(-3px);
  }
}
/* ── Org step card: highlighted blue border + soft glow ── */
.flow-card-org {
  border: 1.5px solid #69b1ff;
  box-shadow: 0 0 0 4px rgba(22,119,255,0.08), 0 6px 16px rgba(22,119,255,0.16);
}
.flow-num {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  height: 20px;
  padding: 0 10px;
  border-radius: 999px;
  background: linear-gradient(135deg, #1677ff 0%, #4096ff 100%);
  color: #fff;
  font-size: 10.5px;
  font-weight: 700;
  letter-spacing: 0.5px;
  margin-bottom: 12px;
  box-shadow: 0 2px 6px rgba(22,119,255,0.3);
}
.flow-num::before {
  content: 'STEP';
  font-size: 9px;
  opacity: 0.85;
}
.flow-icon {
  font-size: 22px;
  line-height: 1;
}
.flow-head {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 7px;
  margin-bottom: 8px;
}
.flow-title {
  font-size: 13.5px;
  font-weight: 700;
  color: var(--text);
  line-height: 1.3;
}
.flow-desc {
  font-size: 11.5px;
  color: var(--text-secondary);
  line-height: 1.5;
}
@media (max-width: 900px) {
  .flow-list { grid-template-columns: repeat(3, 1fr); }
  .flow-card:nth-child(6n)::after { display: block; }
  .flow-card:nth-child(3n)::after { display: none; }
}
@media (max-width: 560px) {
  .flow-list { grid-template-columns: repeat(2, 1fr); }
  .flow-card::after { display: none; }
}

/* ── Footer ── */
.footer-note {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 13px 18px;
  background: #fffbe6;
  border: 1px solid #ffe58f;
  border-radius: 8px;
  font-size: 12px;
  color: #8c6d1f;
  line-height: 1.7;
}
.note-dot { flex-shrink: 0; }

/* ── Print ── */
@media print {
  .no-print { display: none !important; }
  .summary-wrap { max-width: 100% !important; }
  .header-card {
    background: #1677ff !important;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }
  .info-panel, .org-panel, .flow-panel { box-shadow: none; border: 1px solid #ddd; break-inside: avoid; }
  .flow-card { break-inside: avoid; }
  /* Print: 6-column grid on A4 portrait */
  .flow-list {
    grid-template-columns: repeat(6, 1fr);
    column-gap: 6px;
    row-gap: 10px;
    padding: 14px 10px 18px;
  }
  .flow-card {
    padding: 8px 4px 6px;
    border-radius: 8px;
  }
  .flow-card::after {
    width: 5px;
    height: 5px;
    margin-left: 1px;
    border-width: 1.5px;
  }
  .flow-card:nth-child(6n)::after { display: none; }
  .flow-num {
    height: 16px;
    padding: 0 6px;
    font-size: 9px;
    margin-bottom: 6px;
  }
  .flow-num::before { font-size: 7.5px; }
  .flow-icon { font-size: 14px; }
  .flow-head { gap: 3px; margin-bottom: 4px; }
  .flow-title { font-size: 9.5px; }
  .flow-desc { font-size: 8px; line-height: 1.35; }
  /* Keep enlarged org image within a single page */
  .org-img { max-width: 100%; max-height: 360px; }
}
</style>
