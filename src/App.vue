<script setup lang="ts">
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { setLocale, type Lang } from './i18n'
import RegAdvisor from './components/RegAdvisor.vue'
import FinanceSandbox from './components/FinanceSandbox.vue'
import LegalAssistant from './components/LegalAssistant.vue'
import ControlSandbox from './components/ControlSandbox.vue'
import PolicyEngine from './components/PolicyEngine.vue'

const { t, locale } = useI18n()

type ModuleId = 'reg' | 'finance' | 'control' | 'legal' | 'policy'
const currentModule = ref<ModuleId>('reg')
const modules = computed<{ id: ModuleId; label: string; icon: string }[]>(() => [
  { id: 'reg', label: t('app.module.reg'), icon: '📋' },
  { id: 'control', label: t('app.module.control'), icon: '📊' },
  { id: 'policy', label: t('app.module.policy'), icon: '🎯' },
  { id: 'legal', label: t('app.module.legal'), icon: '⚖️' },
])
const currentLabel = computed(() => modules.value.find(m => m.id === currentModule.value)?.label)

const langs: { id: Lang; label: string }[] = [
  { id: 'en', label: t('app.lang.en') },
  { id: 'zh', label: t('app.lang.zh') },
]
</script>

<template>
  <aside class="sidebar">
    <div class="logo">
      <span class="logo-icon">⚡</span>
      <span>Lucky OS</span>
    </div>
    <nav>
      <button
        v-for="m in modules"
        :key="m.id"
        class="nav-item"
        :class="{ active: currentModule === m.id }"
        @click="currentModule = m.id"
      >
        <span>{{ m.icon }}</span>
        <span>{{ m.label }}</span>
      </button>
    </nav>

    <div class="lang-switch">
      <span class="lang-icon">🌐</span>
      <div class="lang-seg">
        <button
          v-for="l in langs"
          :key="l.id"
          class="lang-opt"
          :class="{ active: locale === l.id }"
          @click="setLocale(l.id)"
        >{{ l.label }}</button>
      </div>
    </div>
  </aside>

  <div class="main-layout">
    <header class="topbar">
      {{ currentLabel }}
    </header>
    <main class="content-area">
      <RegAdvisor v-if="currentModule === 'reg'" />
      <FinanceSandbox v-else-if="currentModule === 'finance'" />
      <ControlSandbox v-else-if="currentModule === 'control'" />
      <PolicyEngine v-else-if="currentModule === 'policy'" />
      <LegalAssistant v-else />
    </main>
  </div>
</template>

<style scoped>
.sidebar {
  position: fixed;
  left: 12px;
  top: 12px;
  bottom: 12px;
  width: var(--sidebar-w);
  background: #ffffff;
  color: var(--text-secondary);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  border-radius: 16px;
  box-shadow: var(--shadow);
  z-index: 100;
  overflow: hidden;
}
.logo {
  height: 56px;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 0 20px;
  border-bottom: 1px solid var(--border-light);
  color: var(--text);
  font-size: 17px;
  font-weight: 700;
  letter-spacing: 0.3px;
}
.logo-icon { font-size: 20px; }
nav { padding: 8px; display: flex; flex-direction: column; gap: 2px; }
.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  background: none;
  border: none;
  color: var(--text);
  font-size: 13.5px;
  cursor: pointer;
  text-align: left;
  transition: all 0.2s;
  width: 100%;
  border-radius: 6px;
}
.nav-item:hover { color: var(--text); background: var(--bg); }
.nav-item.active { background: #e6f4ff; color: var(--primary); font-weight: 600; }

/* language switch — pinned to the bottom of the sidebar */
.lang-switch {
  margin-top: auto;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  border-top: 1px solid var(--border-light);
}
.lang-icon { font-size: 14px; opacity: 0.7; }
.lang-seg {
  display: inline-flex;
  border: 1px solid var(--border);
  border-radius: 8px;
  overflow: hidden;
}
.lang-opt {
  border: none;
  background: white;
  color: var(--text-secondary);
  font-size: 12.5px;
  font-weight: 600;
  padding: 5px 14px;
  cursor: pointer;
  transition: all 0.18s;
}
.lang-opt:not(:last-child) { border-right: 1px solid var(--border); }
.lang-opt:hover { background: var(--bg); color: var(--text); }
.lang-opt.active { background: var(--primary); color: white; }
.main-layout {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  margin-left: calc(var(--sidebar-w) + 24px);
  padding: 12px 12px 12px 0;
  gap: 12px;
}
.topbar {
  height: 56px;
  background: white;
  display: flex;
  align-items: center;
  padding: 0 24px;
  font-size: 15px;
  font-weight: 600;
  color: var(--text);
  flex-shrink: 0;
  border-radius: 16px;
  box-shadow: var(--shadow);
}
.content-area { flex: 1; overflow-y: auto; padding: 24px; }
</style>
