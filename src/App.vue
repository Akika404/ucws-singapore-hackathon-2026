<script setup lang="ts">
import { ref } from 'vue'
import RegAdvisor from './components/RegAdvisor.vue'
import FinanceSandbox from './components/FinanceSandbox.vue'
import LegalAssistant from './components/LegalAssistant.vue'
import ControlSandbox from './components/ControlSandbox.vue'
import PolicyEngine from './components/PolicyEngine.vue'

type ModuleId = 'reg' | 'finance' | 'control' | 'legal' | 'policy'
const currentModule = ref<ModuleId>('reg')
const modules: { id: ModuleId; label: string; icon: string }[] = [
  { id: 'reg', label: '智能工商注册顾问', icon: '📋' },
  { id: 'control', label: '开业成本预估', icon: '📊' },
  { id: 'policy', label: '扶持政策检索', icon: '🎯' },
  { id: 'legal', label: '法务合规与合同助手', icon: '⚖️' },
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
  </aside>

  <div class="main-layout">
    <header class="topbar">
      {{ modules.find(m => m.id === currentModule)?.label }}
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
