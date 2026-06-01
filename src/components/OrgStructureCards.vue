<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const props = defineProps<{
  people?: number | null
  compact?: boolean
}>()

const { locale } = useI18n()

type OrgCard = {
  icon: string
  title: string
  badge?: string
  subRole: string
  desc?: string
  descClass?: string
  dutiesLabel?: string
  duties: string[]
  secondaryTitle?: string
  secondaryDuties?: string[]
}

const isZh = computed(() => locale.value === 'zh')
const isOnePerson = computed(() => props.people === 1)

const footer = computed(() => {
  if (isOnePerson.value) {
    return isZh.value
      ? '股东+董事架构 · 精简治理 权责闭环 | 适用于一人有限公司'
      : 'Shareholder + Director structure · Lean governance with closed-loop authority | For one-person limited companies'
  }
  return isZh.value
    ? '公司治理架构 · 权责清晰 合规高效'
    : 'Corporate governance structure · Clear authority, compliant and efficient'
})

const onePersonCard = computed<OrgCard>(() => ({
  icon: '🧑‍💼',
  title: isZh.value ? '股东 + 董事' : 'Shareholder + Director',
  badge: isZh.value ? '权责一体 · 不设监事' : 'Unified authority · No supervisor',
  subRole: isZh.value
    ? '所有者决策 · 经营者执行 | 一人公司治理范式'
    : 'Owner decision-making · Operator execution | One-person company model',
  dutiesLabel: isZh.value ? '董事职责' : 'Director duties',
  duties: isZh.value
    ? ['战略决策', '业务执行监督', '高管聘任与解聘', '风险内控', '代表公司签署文件']
    : ['Strategy decisions', 'Execution oversight', 'Appoint or remove executives', 'Risk control', 'Sign company documents'],
  secondaryTitle: isZh.value ? '股东职责' : 'Shareholder duties',
  secondaryDuties: isZh.value
    ? ['资产收益', '重大事项决议', '选择与罢免董事', '章程修订', '增减资/合并/分立决策']
    : ['Asset returns', 'Major resolutions', 'Select or remove directors', 'Amend articles', 'Capital changes, merger or division'],
  desc: isZh.value
    ? '依据《公司法》一人有限责任公司特别规定，公司可不设监事会或监事，由单一自然人同时履行股东、执行董事及经理职责，实现决策层与执行层高度统一。'
    : 'Under the special rules for one-person limited companies, the company may operate without a board of supervisors or supervisor, with the sole natural person combining shareholder, executive director and manager responsibilities.',
}))

const multiPersonCards = computed<OrgCard[]>(() => [
  {
    icon: '🏛️',
    title: isZh.value ? '股东会' : 'Shareholders Meeting',
    subRole: isZh.value ? '最高权力机构' : 'Highest authority',
    desc: isZh.value
      ? '决定公司增减资、合并、分立、解散等重大事项，按出资比例行使表决权，拥有最终决策权。'
      : 'Decides major matters such as capital changes, merger, division and dissolution, with voting rights generally exercised by capital contribution.',
    descClass: 'shareholder-desc',
    dutiesLabel: isZh.value ? '核心职责' : 'Core duties',
    duties: isZh.value ? ['重大事项决议', '章程修订'] : ['Major resolutions', 'Amend articles'],
  },
  {
    icon: '📋',
    title: isZh.value ? '董事会 / 执行董事' : 'Board / Executive Director',
    subRole: isZh.value ? '经营决策机构' : 'Operating decision body',
    desc: isZh.value
      ? '执行股东会决议，负责公司日常经营决策与业务管理。不设董事会时可设执行董事并兼任经理。'
      : 'Executes shareholder resolutions and handles daily operating decisions and business management. If no board is formed, an executive director may also serve as manager.',
    descClass: 'board-desc',
    dutiesLabel: isZh.value ? '核心职责' : 'Core duties',
    duties: isZh.value ? ['战略制定', '业务执行', '重大经营决策'] : ['Strategy planning', 'Business execution', 'Major operating decisions'],
  },
  {
    icon: '🔍',
    title: isZh.value ? '监事会 / 监事' : 'Supervisory Board / Supervisor',
    subRole: isZh.value ? '独立监督机构' : 'Independent supervisory body',
    desc: isZh.value
      ? '检查公司财务，监督董事及高级管理人员履职行为，维护公司合规与股东利益。不得由董事、经理兼任。'
      : 'Reviews company finances and supervises directors and senior managers to protect compliance and shareholder interests. Directors and managers may not concurrently serve.',
    descClass: 'supervisor-desc',
    dutiesLabel: isZh.value ? '核心职责' : 'Core duties',
    duties: isZh.value ? ['财务稽核', '高管监督', '合规保障'] : ['Financial review', 'Executive supervision', 'Compliance protection'],
  },
])
</script>

<template>
  <section class="org-cards" :class="{ compact, 'is-one-person': isOnePerson }">
    <div v-if="isOnePerson" class="single-card-container">
      <article class="governance-card">
        <header class="card-header">
          <div class="card-title">
            <span class="title-main">
              <span class="title-icon">{{ onePersonCard.icon }}</span>
              <span class="title-text">{{ onePersonCard.title }}</span>
            </span>
            <span class="title-badge">{{ onePersonCard.badge }}</span>
          </div>
          <div class="sub-role">{{ onePersonCard.subRole }}</div>
        </header>
        <div class="card-content">
          <div class="dual-responsibilities">
            <div class="resp-col">
              <h4>📌 {{ onePersonCard.dutiesLabel }}</h4>
              <div class="duties-list">
                <span v-for="duty in onePersonCard.duties" :key="duty" class="duty-tag">{{ duty }}</span>
              </div>
            </div>
            <div class="resp-col">
              <h4>💰 {{ onePersonCard.secondaryTitle }}</h4>
              <div class="duties-list">
                <span v-for="duty in onePersonCard.secondaryDuties" :key="duty" class="duty-tag">{{ duty }}</span>
              </div>
            </div>
          </div>
          <div class="legal-note">
            <span class="note-icon">⚖️</span>
            <span>{{ onePersonCard.desc }}</span>
          </div>
        </div>
      </article>
    </div>

    <div v-else class="governance-grid">
      <article
        v-for="card in multiPersonCards"
        :key="card.title"
        class="governance-card"
      >
        <header class="card-header">
          <div class="card-title">
            <span class="title-main">
              <span class="title-icon">{{ card.icon }}</span>
              <span class="title-text">{{ card.title }}</span>
            </span>
          </div>
          <div class="sub-role">{{ card.subRole }}</div>
        </header>
        <div class="card-content">
          <div class="institution-desc" :class="card.descClass">
            <p>{{ card.desc }}</p>
          </div>
          <div class="duties-section">
            <div class="duties-label">{{ card.dutiesLabel }}</div>
            <div class="duties-list">
              <span v-for="duty in card.duties" :key="duty" class="duty-tag">{{ duty }}</span>
            </div>
          </div>
        </div>
      </article>
    </div>

    <footer class="org-footer">{{ footer }}</footer>
  </section>
</template>

<style scoped>
.org-cards {
  width: 100%;
  padding: 20px;
  background: #f0f2f5;
  border: 1px solid var(--border-light);
  border-radius: 8px;
}

.org-cards.compact {
  padding: 16px;
}

.single-card-container {
  max-width: 720px;
  width: 100%;
  margin: 0 auto;
}

.governance-grid {
  width: 100%;
  margin: 0 auto;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 18px;
  align-items: stretch;
}

.governance-card {
  background: #ffffff;
  border-radius: 16px;
  box-shadow: 0 8px 18px rgba(0, 0, 0, 0.07), 0 1px 3px rgba(0, 0, 0, 0.02);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
}

.governance-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 14px 24px rgba(0, 0, 0, 0.11);
}

.card-header {
  padding: 18px 18px 10px;
  border-bottom: 2px solid #eef2f6;
}

.card-title {
  font-size: clamp(17px, 1.6vw, 22px);
  font-weight: 700;
  letter-spacing: 0;
  line-height: 1.25;
  margin-bottom: 6px;
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  color: #111827;
}

.title-icon {
  flex-shrink: 0;
  line-height: 1.25;
}

.title-main {
  display: inline-grid;
  grid-template-columns: auto minmax(0, 1fr);
  align-items: start;
  gap: 8px;
  min-width: 0;
  max-width: 100%;
}

.title-text {
  min-width: 0;
  overflow-wrap: anywhere;
}

.title-badge {
  background: #eef2ff;
  padding: 2px 9px;
  border-radius: 40px;
  font-size: 11px;
  font-weight: 600;
  color: #1e3a8a;
}

.sub-role {
  font-size: 12px;
  color: #5b6e8c;
  background: #f8fafc;
  display: inline-block;
  padding: 3px 10px;
  border-radius: 20px;
  margin-top: 4px;
  font-weight: 600;
  line-height: 1.45;
}

.card-content {
  padding: 15px 18px 18px;
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.institution-desc {
  background: #f9fafb;
  padding: 11px 13px;
  border-radius: 12px;
  font-size: 12px;
  color: #1e2a3e;
  border-left: 4px solid;
  line-height: 1.55;
}

.institution-desc p {
  margin: 0;
}

.shareholder-desc { border-left-color: #2c6e9e; }
.board-desc { border-left-color: #2c7a4d; }
.supervisor-desc { border-left-color: #b45353; }

.duties-section {
  margin-top: 2px;
}

.duties-label {
  font-size: 11px;
  text-transform: uppercase;
  font-weight: 800;
  letter-spacing: 0.5px;
  color: #4a5b7a;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.duties-label::before {
  content: "▍";
  font-size: 16px;
  font-weight: normal;
}

.duties-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.duty-tag {
  background: #f1f5f9;
  padding: 4px 11px;
  border-radius: 30px;
  font-size: 12px;
  font-weight: 600;
  color: #1f3a5f;
  line-height: 1.35;
  transition: all 0.1s ease;
}

.duty-tag:hover {
  background: #e2e8f0;
  transform: scale(1.02);
}

.dual-responsibilities {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.resp-col {
  flex: 1 1 240px;
  background: #ffffff;
  border-radius: 12px;
  border: 1px solid #eef2f6;
  padding: 10px 13px;
}

.resp-col h4 {
  font-size: 13px;
  font-weight: 700;
  margin: 0 0 8px;
  display: flex;
  align-items: center;
  gap: 6px;
  color: #1f3a5f;
}

.legal-note {
  background: #eef2ff;
  border-left: 4px solid #1e4a76;
  border-radius: 10px;
  padding: 11px 13px;
  font-size: 12px;
  color: #0c2b4b;
  font-weight: 600;
  line-height: 1.55;
  display: flex;
  align-items: flex-start;
  gap: 8px;
}

.note-icon {
  font-size: 15px;
  flex-shrink: 0;
}

.org-footer {
  text-align: center;
  font-size: 11px;
  color: #8a99b0;
  margin-top: 18px;
  line-height: 1.5;
}

.compact .governance-grid {
  gap: 14px;
}

.compact .card-header {
  padding: 16px 16px 9px;
}

.compact .card-content {
  padding: 13px 16px 16px;
}

.compact .card-title {
  font-size: clamp(16px, 1.5vw, 20px);
}

@media (max-width: 1000px) {
  .governance-grid {
    gap: 14px;
  }

  .card-title {
    font-size: 18px;
  }

  .card-content {
    padding: 13px 16px 16px;
  }
}

@media (max-width: 780px) {
  .org-cards {
    padding: 14px;
  }

  .governance-grid {
    display: flex;
    flex-direction: column;
    gap: 14px;
    max-width: 560px;
  }

  .governance-card {
    width: 100%;
  }
}

@media (max-width: 560px) {
  .org-cards {
    padding: 12px;
  }

  .dual-responsibilities {
    flex-direction: column;
    gap: 10px;
  }

  .card-header {
    padding: 16px 15px 9px;
  }

  .card-content {
    padding: 13px 15px 15px;
  }

  .card-title {
    font-size: 17px;
  }
}

@media print {
  .org-cards {
    padding: 12px;
    break-inside: avoid;
  }

  .governance-card {
    box-shadow: none;
    border: 1px solid #e5e7eb;
    break-inside: avoid;
  }

  .governance-grid {
    gap: 10px;
  }

  .card-header {
    padding: 12px 12px 8px;
  }

  .card-content {
    padding: 10px 12px 12px;
  }

  .card-title {
    font-size: 15px;
  }

  .sub-role,
  .institution-desc,
  .duty-tag,
  .legal-note,
  .org-footer {
    font-size: 9px;
  }
}
</style>
