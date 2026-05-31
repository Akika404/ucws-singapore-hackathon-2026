<script setup lang="ts">
import { ref } from 'vue'
import type { BaseFormData } from './RegAdvisor.vue'

defineProps<{ loading: boolean }>()
const emit = defineEmits<{ generate: [data: BaseFormData] }>()

const business = ref('数字化营销 + 电商代运营')
const people = ref(28)
const namePref = ref('星禾云创')
function submit() {
  emit('generate', {
    business: business.value,
    people: people.value,
    shareholder: null,
    companyType: people.value < 50 ? '有限责任公司' : '股份有限公司',
    namePref: namePref.value,
    name: '',
    scope: '',
    capital: '',
    address: '',
    org: '',
  })
}

const extra = ref('')
</script>

<template>
  <div class="card">
    <div class="card-header">
      <div>
        <div class="card-title">业务基座配置</div>
        <div class="card-subtitle">填写基本信息，AI 将为您生成定制化注册方案</div>
      </div>
      <span class="ai-badge">✨ AI 驱动</span>
    </div>

    <div class="form-row">
      <div class="form-item">
        <label>公司主营业务</label>
        <input v-model="business" class="input" placeholder="如：电商零售、SaaS、科技研发..." />
      </div>
      <div class="form-item form-item--sm">
        <label>预计团队人数</label>
        <input v-model.number="people" type="number" class="input" placeholder="人数" min="1" />
      </div>
      <div class="form-item">
        <label>公司名称偏好</label>
        <input v-model="namePref" class="input" placeholder="如：智云科技" />
      </div>
    </div>

    <div class="form-row">
      <div class="form-item">
        <label>补充信息</label>
        <textarea v-model="extra" class="input textarea" placeholder="如有其他需要说明的情况，请在此补充..." />
      </div>
    </div>

    <div class="form-footer">
      <div class="hint">
        <span class="hint-icon">💡</span>
        填写越详细，AI 生成的方案越精准
      </div>
      <button class="btn-primary" :disabled="loading" @click="submit">
        <span v-if="loading" class="spinner"></span>
        <span v-else>🚀</span>
        {{ loading ? 'AI 正在生成方案...' : '生成定制化注册方案' }}
      </button>
    </div>
  </div>
</template>

<style scoped>
.card {
  background: white;
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  padding: 28px;
  margin-bottom: 20px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border-light);
}
.card-title { font-size: 17px; font-weight: 700; color: var(--text); }
.card-subtitle { font-size: 13px; color: var(--text-secondary); margin-top: 4px; }
.ai-badge {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  font-size: 12px;
  padding: 4px 12px;
  border-radius: 20px;
  font-weight: 500;
  white-space: nowrap;
}

.form-row { display: flex; gap: 20px; margin-bottom: 20px; flex-wrap: wrap; }
.form-item { flex: 1; display: flex; flex-direction: column; min-width: 200px; }
.form-item--sm { flex: 0 0 140px; min-width: 140px; }
label { font-size: 13px; font-weight: 500; color: var(--text); margin-bottom: 8px; }
.input {
  height: 36px;
  padding: 0 12px;
  border: 1px solid var(--border);
  border-radius: 6px;
  font-size: 14px;
  color: var(--text);
  background: white;
  transition: all 0.2s;
  outline: none;
}
.input:focus { border-color: var(--primary); box-shadow: 0 0 0 2px rgba(22,119,255,0.15); }
.textarea { height: 80px; padding: 8px 12px; resize: vertical; line-height: 1.5; }

.form-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 8px;
  padding-top: 20px;
  border-top: 1px solid var(--border-light);
}
.hint { font-size: 13px; color: var(--text-secondary); display: flex; align-items: center; gap: 6px; }
.hint-icon { font-size: 15px; }

.btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: linear-gradient(135deg, #1677ff, #4096ff);
  color: white;
  border: none;
  padding: 0 24px;
  height: 40px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 2px 8px rgba(22,119,255,0.3);
}
.btn-primary:hover:not(:disabled) { transform: translateY(-1px); box-shadow: 0 4px 12px rgba(22,119,255,0.4); }
.btn-primary:disabled { opacity: 0.7; cursor: not-allowed; }

.spinner {
  width: 14px; height: 14px;
  border: 2px solid rgba(255,255,255,0.4);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 16px;
}
.info-card {
  background: white;
  border: 1px solid var(--border-light);
  border-radius: var(--radius);
  padding: 20px;
  display: flex;
  gap: 14px;
  align-items: flex-start;
  box-shadow: var(--shadow);
  transition: box-shadow 0.2s;
}
.info-card:hover { box-shadow: var(--shadow-md); }
.info-icon { font-size: 24px; flex-shrink: 0; }
.info-title { font-size: 14px; font-weight: 600; color: var(--text); margin-bottom: 4px; }
.info-desc { font-size: 12px; color: var(--text-secondary); line-height: 1.5; }
</style>
