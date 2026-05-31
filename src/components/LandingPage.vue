<script setup lang="ts">
const emit = defineEmits<{ (e: 'start'): void }>()

const steps = [
  '公司名称核准', '经营范围拟定', '公司类型选择', '注册资本认缴',
  '注册地址选择', '组织架构设计', '领取营业执照', '刻章与备案',
  '银行开户', '税务登记', '社保开户', '公司营业',
]

// light gradient that sweeps left → right across the whole row (blue → purple → pink)
function dotStyle(i: number) {
  const h = 210 + (i / (steps.length - 1)) * 120
  return {
    background: `linear-gradient(to right, hsl(${h}, 78%, 82%), hsl(${h + 18}, 72%, 74%))`,
    // stagger the bob so the dots ripple like a gentle wave across the row
    animationDelay: i * 0.15 + 's',
  }
}
</script>

<template>
  <div class="landing">
    <div class="blob blob-1"></div>
    <div class="blob blob-2"></div>
    <div class="blob blob-3"></div>

    <div class="landing-inner">
      <header class="hero">
        <h1 class="title">让公司注册，<span class="grad-text">轻松一步到位</span></h1>
        <p class="subtitle">从核名到开业，全流程智能引导，一站式完成工商注册</p>
      </header>

      <section class="flow">
        <div class="flow-line"></div>
        <div
          v-for="(step, i) in steps"
          :key="i"
          class="node"
          :style="{ animationDelay: i * 0.06 + 's' }"
        >
          <span class="node-dot" :style="dotStyle(i)">{{ i + 1 }}</span>
          <span class="node-label">{{ step }}</span>
        </div>
      </section>

      <button class="cta" @click="emit('start')">立即填写</button>
    </div>
  </div>
</template>

<style scoped>
.landing {
  position: fixed;
  inset: 0;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(120deg, #eef4ff 0%, #f3eeff 35%, #eafaf4 70%, #fff7ee 100%);
  background-size: 300% 300%;
  animation: bg-shift 18s ease infinite;
}
@keyframes bg-shift {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}
/* soft floating color blobs */
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
.landing-inner {
  position: relative;
  z-index: 1;
  width: 100%;
  max-width: 1480px;
  padding: 40px;
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
  margin: 64px auto 64px;
  max-width: 1440px;
  padding: 0;
}
/* the connecting line behind the dots — ends align to the first/last dot centres (½ node width = 100%/24) */
.flow-line {
  position: absolute;
  top: 30px;
  left: calc(100% / 24);
  right: calc(100% / 24);
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
  /* drop the wave on hover so the lift/scale transition takes over cleanly */
  animation: none;
  transform: translateY(-6px) scale(1.18);
  box-shadow: 0 12px 24px rgba(22, 119, 255, 0.42);
}
@keyframes bob {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-5px); }
}
.node-label {
  font-size: 14.5px;
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
@media (max-width: 640px) {
  .title { font-size: 32px; }
  .flow { margin: 32px auto 40px; }
}
</style>
