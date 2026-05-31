<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import StepPage from './StepPage.vue'
import SummaryPage from './SummaryPage.vue'
import { sharedFormData } from '../store'

const { t, tm } = useI18n()

export interface StepData {
  id: string
  title: string
  icon: string
  options: StepOption[]
}

export interface StepOption {
  label: string
  summary: string
  detail: string
  recommended?: boolean
}

export interface BusinessScope {
  main: string
  others: string[]
}

export interface BaseFormData {
  business: string
  people: number | null
  shareholder: number | null
  companyType: string
  namePref: string
  name: string
  scope: BusinessScope | ''
  capital: string
  address: string
  org: string
}

const currentStep = ref(0)
const hasStarted = ref(false)
const isDissolving = ref(false)
const optionsLoading = ref(false)

const EMPTY_FORM: BaseFormData = {
  business: '',
  people: null,
  shareholder: null,
  companyType: '',
  namePref: '',
  name: '',
  scope: '',
  capital: '',
  address: '',
  org: '',
}

const formData = ref<BaseFormData>({ ...EMPTY_FORM })

watch(formData, (v) => { sharedFormData.value = { ...v } }, { deep: true })

function onAnswer(stepId: string, answer: string | BusinessScope) {
  (formData.value as any)[stepId] = answer
}

function onUpdateFormData(patch: Partial<BaseFormData>) {
  formData.value = { ...formData.value, ...patch }
}

function goNext() {
  if (currentStep.value < steps.value.length - 1) {
    currentStep.value++
  } else {
    currentStep.value = steps.value.length
  }
}

function goPrev() {
  if (currentStep.value > 0) currentStep.value--
}

function goToStep(i: number) {
  if (i <= currentStep.value || (formData.value as any)[steps.value[i - 1]?.id]) {
    currentStep.value = i
  }
}

function startForm() {
  isDissolving.value = true
  setTimeout(() => {
    hasStarted.value = true
    currentStep.value = 0
    isDissolving.value = false
  }, 600)
}

const STEP_SKELETONS = [
  { id: 'name',    icon: '🔍' },
  { id: 'scope',   icon: '📋' },
  { id: 'type',    icon: '🏢' },
  { id: 'capital', icon: '💰' },
  { id: 'address', icon: '📍' },
  { id: 'org',     icon: '🏗️' },
]

// 步骤标题随语言切换；options 在 StepPage 内按需生成，这里恒为空骨架
const steps = computed<StepData[]>(() =>
  STEP_SKELETONS.map(s => ({ ...s, title: t(`reg.steps.${s.id}`), options: [] })),
)

// 欢迎页 12 步流程节点（随语言切换）
const WELCOME_STEPS = computed<string[]>(() => tm('reg.flow') as string[])

function dotStyle(i: number) {
  const h = 210 + (i / (WELCOME_STEPS.value.length - 1)) * 120
  return {
    background: `linear-gradient(to right, hsl(${h}, 78%, 82%), hsl(${h + 18}, 72%, 74%))`,
    animationDelay: i * 0.15 + 's',
  }
}
</script>

<template>
  <!-- Welcome page -->
  <div v-if="!hasStarted" class="welcome-page" :class="{ dissolving: isDissolving }">
    <div class="blob blob-1"></div>
    <div class="blob blob-2"></div>
    <div class="blob blob-3"></div>

    <div class="welcome-inner">
      <header class="hero">
        <h1 class="title">{{ t('reg.welcome.titleLead') }}<span class="grad-text">{{ t('reg.welcome.titleHighlight') }}</span></h1>
        <p class="subtitle">{{ t('reg.welcome.subtitle') }}</p>
      </header>

      <section class="flow">
        <div class="flow-line"></div>
        <div
          v-for="(label, i) in WELCOME_STEPS"
          :key="i"
          class="node"
          :style="{ animationDelay: i * 0.06 + 's' }"
        >
          <span class="node-dot" :style="dotStyle(i)">{{ i + 1 }}</span>
          <span class="node-label">{{ label }}</span>
        </div>
      </section>

      <button class="cta" @click="startForm">
        <span>🚀</span>
        <span>{{ t('reg.welcome.cta') }}</span>
      </button>
    </div>
  </div>

  <SummaryPage
    v-else-if="steps.length > 0 && currentStep === steps.length"
    :steps="steps"
    :form-data="formData"
    @restart="currentStep = 0; formData = { ...{ business: '', people: null, shareholder: null, companyType: '', namePref: '', name: '', scope: '', capital: '', address: '', org: '' } }; hasStarted = false"
  />

  <div v-else-if="steps.length" class="advisor-wrapper">
    <div class="advisor-layout">
      <div class="sidebar-placeholder">
        <div class="progress-sidebar">
          <div class="progress-sidebar-inner">
            <button
              v-for="(s, i) in steps"
              :key="s.id"
              class="prog-step"
              :class="{
                active: i === currentStep,
                done: i < currentStep,
                reachable: i <= currentStep || !!(formData as any)[steps[i-1]?.id]
              }"
              @click="goToStep(i)"
            >
              <div class="prog-dot-wrap">
                <span class="prog-dot">
                  <span v-if="(formData as any)[s.id] !== undefined && (formData as any)[s.id] !== '' && i !== currentStep">✓</span>
                  <span v-else>{{ i + 1 }}</span>
                </span>
                <span class="prog-line" v-if="i < steps.length - 1" />
              </div>
              <span class="prog-label">{{ s.title }}</span>
            </button>
          </div>
        </div>
      </div>

      <StepPage
        class="advisor-content"
        :step="steps[currentStep]"
        :step-index="currentStep"
        :total-steps="steps.length"
        :selected="(formData as any)[steps[currentStep]?.id]"
        :is-last="currentStep === steps.length - 1"
        :options-loading="optionsLoading"
        :form-data="formData"
        @answer="onAnswer"
        @update-form-data="onUpdateFormData"
        @next="goNext"
        @prev="goPrev"
      />
    </div>

    <div class="ai-disclaimer">
      <span class="ai-disclaimer-icon">⚠️</span>
      <p><b>{{ t('common.aiRiskTitle') }}</b>{{ t('common.aiRiskSep') }}{{ t('common.aiRiskDesc') }}</p>
    </div>
  </div>
</template>

<style scoped>
/* ---------- Welcome page ---------- */
.welcome-page {
  position: relative;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: calc(100vh - 104px);
  margin: -24px;
  padding: 40px 24px;
  background: linear-gradient(120deg, #eef4ff 0%, #f3eeff 35%, #eafaf4 70%, #fff7ee 100%);
  background-size: 300% 300%;
  animation: bg-shift 18s ease infinite;
  border-radius: 16px;
}
@keyframes bg-shift {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}
.blob {
  position: absolute;
  border-radius: 50%;
  filter: blur(70px);
  opacity: 0.55;
  pointer-events: none;
}
.blob-1 { width: 460px; height: 460px; background: #c6dcff; top: -120px; left: -100px; animation: float-1 16s ease-in-out infinite; }
.blob-2 { width: 520px; height: 520px; background: #e3d2ff; bottom: -160px; right: -120px; animation: float-2 20s ease-in-out infinite; }
.blob-3 { width: 380px; height: 380px; background: #c8f3df; top: 30%; right: 18%; animation: float-3 22s ease-in-out infinite; }
@keyframes float-1 { 0%,100% { transform: translate(0,0); } 50% { transform: translate(60px,40px); } }
@keyframes float-2 { 0%,100% { transform: translate(0,0); } 50% { transform: translate(-50px,-30px); } }
@keyframes float-3 { 0%,100% { transform: translate(0,0); } 50% { transform: translate(-40px,50px); } }
.welcome-inner {
  position: relative;
  z-index: 1;
  width: 100%;
  max-width: 1280px;
  text-align: center;
}
.hero { animation: rise 0.7s ease both; }
.logo-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 700;
  color: var(--primary);
  background: rgba(255, 255, 255, 0.7);
  padding: 6px 16px;
  border-radius: 999px;
  backdrop-filter: blur(6px);
  margin-bottom: 24px;
}
.title {
  font-size: 44px;
  font-weight: 800;
  line-height: 1.25;
  color: var(--text);
  letter-spacing: 0.5px;
}
.grad-text {
  background: linear-gradient(90deg, #1677ff, #9254de, #36cfc9);
  background-size: 200% auto;
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  animation: grad-move 6s linear infinite;
}
@keyframes grad-move { to { background-position: 200% center; } }
.subtitle {
  margin-top: 16px;
  font-size: 16px;
  color: var(--text-secondary);
}
.flow {
  position: relative;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin: 56px auto 56px;
  max-width: 1400px;
  padding: 0 32px;
}
.flow-line {
  position: absolute;
  top: 30px;
  left: calc(100% / 12);
  right: calc(100% / 12);
  height: 2px;
  background: linear-gradient(90deg, #1677ff, #9254de, #36cfc9);
  opacity: 0.35;
  z-index: 0;
}
.node {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 14px;
  flex: 1;
  padding: 0 12px;
  animation: rise 0.5s ease both;
}
.node-dot {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 62px;
  height: 62px;
  border-radius: 50%;
  background: linear-gradient(135deg, #1677ff, #9254de);
  color: #fff;
  font-size: 23px;
  font-weight: 700;
  box-shadow: 0 6px 16px rgba(22, 119, 255, 0.32);
  border: 2px solid rgba(255, 255, 255, 0.75);
  transition: transform 0.25s cubic-bezier(0.34, 1.56, 0.64, 1), box-shadow 0.25s ease;
  will-change: transform;
  animation: bob 3s ease-in-out infinite;
}
.node:hover .node-dot {
  animation: none;
  transform: translateY(-6px) scale(1.18);
  box-shadow: 0 12px 24px rgba(22, 119, 255, 0.42);
}
@keyframes bob {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-5px); }
}
.node-label {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-secondary);
  text-align: center;
  line-height: 1.4;
  white-space: nowrap;
}
.cta {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 15px 48px;
  font-size: 17px;
  font-weight: 700;
  color: #fff;
  border: none;
  border-radius: 999px;
  cursor: pointer;
  background: linear-gradient(135deg, #1677ff, #9254de);
  background-size: 180% auto;
  box-shadow: 0 8px 24px rgba(22, 119, 255, 0.35);
  transition: transform 0.2s, box-shadow 0.2s, background-position 0.4s;
  animation: rise 0.7s ease 0.3s both, pulse 2.6s ease-in-out infinite 1s;
}
.cta:hover {
  transform: translateY(-2px);
  background-position: right center;
  box-shadow: 0 12px 30px rgba(22, 119, 255, 0.45);
}
.cta:active { transform: translateY(0); }
@keyframes rise {
  from { opacity: 0; transform: translateY(16px); }
  to { opacity: 1; transform: translateY(0); }
}
@keyframes pulse {
  0%, 100% { box-shadow: 0 8px 24px rgba(22, 119, 255, 0.35); }
  50% { box-shadow: 0 8px 32px rgba(22, 119, 255, 0.5); }
}
/* ---------- Fade-out on start ---------- */
.welcome-page.dissolving {
  transition: opacity 0.6s ease-out;
  opacity: 0;
  pointer-events: none;
}
@media (max-width: 900px) {
  .flow { flex-wrap: wrap; gap: 24px; justify-content: center; }
  .flow-line { display: none; }
  .node { flex: 0 0 30%; }
  .title { font-size: 32px; }
}
@media (max-width: 640px) {
  .title { font-size: 28px; }
  .node { flex: 0 0 45%; }
}

/* ---------- Advisor ---------- */
.advisor-wrapper { display: flex; flex-direction: column; gap: 20px; width: 100%; }
.ai-disclaimer { margin-left: 216px; }
.advisor-layout {
  display: flex;
  gap: 20px;
  align-items: flex-start;
  width: 100%;
}
.sidebar-placeholder {
  width: 196px;
  flex-shrink: 0;
}
.progress-sidebar {
  display: flex;
  flex-direction: column;
  background: white;
  border-radius: 16px;
  box-shadow: var(--shadow);
  width: 196px;
  position: fixed;
  top: 80px;
  left: 244px;
  height: calc(100vh - 104px);
  overflow: hidden;
}
.progress-sidebar-inner {
  padding: 32px 28px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  height: 100%;
}
.advisor-content {
  flex: 1;
  min-width: 0;
}
.prog-step {
  display: flex;
  flex-direction: row;
  align-items: stretch;
  gap: 10px;
  background: none;
  border: none;
  cursor: default;
  padding: 0;
  text-align: left;
  flex: 1;
}
.prog-step.reachable { cursor: pointer; }
.prog-dot-wrap {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex-shrink: 0;
}
.prog-line {
  width: 2px;
  flex: 1;
  min-height: 20px;
  background: var(--border-light);
  margin: 2px 0;
}
.prog-step.done .prog-line,
.prog-step.active .prog-line {
  background: var(--primary);
}
.prog-dot {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  border: 2px solid var(--border);
  background: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary);
  transition: all 0.2s;
}
.prog-step.active .prog-dot {
  border-color: var(--primary);
  background: var(--primary);
  color: white;
}
.prog-step.done .prog-dot {
  border-color: var(--primary);
  background: #e6f4ff;
  color: var(--primary);
}
.prog-label {
  font-size: 12px;
  color: var(--text);
  padding-top: 5px;
  line-height: 1.3;
}
.prog-step.active .prog-label { color: var(--primary); font-weight: 600; }
.prog-step.done .prog-label { color: var(--text); }
</style>
