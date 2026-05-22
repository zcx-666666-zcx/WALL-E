<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
const router = useRouter()

const goPage = (path) => router.push(path)
const timeGreeting = ref('')

onMounted(() => {
  const h = new Date().getHours()
  if (h < 6) timeGreeting.value = '夜深了'
  else if (h < 9) timeGreeting.value = '早上好'
  else if (h < 12) timeGreeting.value = '上午好'
  else if (h < 14) timeGreeting.value = '中午好'
  else if (h < 18) timeGreeting.value = '下午好'
  else timeGreeting.value = '晚上好'
})

const cards = [
  {
    label: '事件管理', sub: '提醒与日程',
    icon: `<svg width="26" height="26" viewBox="0 0 26 26" fill="none"><rect x="3" y="2" width="20" height="22" rx="3" stroke="currentColor" stroke-width="1.7"/><path d="M8 9h10M8 14h10M8 19h6" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg>`,
    color: '#FF6040', action: () => goPage('/elementlist')
  },
  {
    label: 'AI 设置', sub: '人设与对话',
    icon: `<svg width="26" height="26" viewBox="0 0 26 26" fill="none"><rect x="4" y="8" width="18" height="13" rx="2.5" stroke="currentColor" stroke-width="1.7"/><path d="M9 8V6a4 4 0 018 0v2" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"/><circle cx="10" cy="15" r="1.5" fill="currentColor"/><circle cx="16" cy="15" r="1.5" fill="currentColor"/></svg>`,
    color: '#7B61FF', action: () => goPage('/Agent')
  },
  {
    label: '命令查询', sub: '指令与记录',
    icon: `<svg width="26" height="26" viewBox="0 0 26 26" fill="none"><rect x="2" y="4" width="22" height="18" rx="3" stroke="currentColor" stroke-width="1.7"/><path d="M7 10l4 4-4 4M15 18h5" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/></svg>`,
    color: '#FF9800', action: () => goPage('/command')
  },
  {
    label: '远程监护', sub: '实时视频',
    icon: `<svg width="26" height="26" viewBox="0 0 26 26" fill="none"><rect x="2" y="6" width="16" height="14" rx="2.5" stroke="currentColor" stroke-width="1.7"/><path d="M18 10l6-3v12l-6-3V10z" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round"/></svg>`,
    color: '#2196F3', action: () => goPage('/video')
  },
  {
    label: '远程遥控', sub: '机器人控制',
    icon: `<svg width="26" height="26" viewBox="0 0 26 26" fill="none"><rect x="7" y="3" width="12" height="20" rx="3" stroke="currentColor" stroke-width="1.7"/><circle cx="13" cy="18" r="2.5" stroke="currentColor" stroke-width="1.5"/><path d="M13 7v3M11.5 8.5h3" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg>`,
    color: '#4CAF50', action: () => goPage('/drive')
  },
  {
    label: '健康监测', sub: '体征与状态',
    icon: `<svg width="26" height="26" viewBox="0 0 26 26" fill="none"><path d="M13 22S3 16 3 10a6 6 0 0110-4.47A6 6 0 0123 10c0 6-10 12-10 12z" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round"/><path d="M7 12h3l2-4 2 8 2-4h3" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>`,
    color: '#E53935', action: () => goPage('/healthy')
  }
]

const stats = [
  { value: '事件管理', label: '智能提醒', desc: '定时语音播报' },
  { value: 'AI 陪聊', label: '情感陪伴', desc: '个性化人设' },
  { value: '远程监护', label: '实时守护', desc: '视频 + 健康数据' },
  { value: '远程遥控', label: '移动操控', desc: '方向 + 动作' },
]
</script>

<template>
  <div class="home-root">
    <div class="bg-orb bg-orb-1"></div>
    <div class="bg-orb bg-orb-2"></div>
    <div class="bg-orb bg-orb-3"></div>
    <div class="bg-grid"></div>

    <!-- 欢迎区域 -->
    <div class="welcome-area">
      <div class="welcome-badge">
        <span class="badge-dot"></span>
        系统运行中
      </div>
      <h1 class="welcome-title">
        {{ timeGreeting }}，欢迎使用
        <span class="title-accent">智能陪伴</span>
      </h1>
      <p class="welcome-sub">守护每一位长辈，让关爱触手可及</p>
    </div>

    <!-- 功能统计条 -->
    <div class="stats-row">
      <div
        v-for="(s, i) in stats"
        :key="s.label"
        class="stat-item"
        :style="{ animationDelay: `${0.2 + i * 0.08}s` }"
      >
        <div class="stat-value">{{ s.value }}</div>
        <div class="stat-label">{{ s.label }}</div>
        <div class="stat-desc">{{ s.desc }}</div>
      </div>
    </div>

    <!-- 功能卡片网格 -->
    <div class="cards-grid">
      <div
        v-for="(card, i) in cards"
        :key="card.label"
        class="func-card"
        :style="{ animationDelay: `${0.35 + i * 0.06}s` }"
        @click="card.action"
      >
        <div class="card-glow"></div>
        <div class="card-accent" :style="{ background: card.color }"></div>
        <div class="card-icon" v-html="card.icon"></div>
        <div class="card-text">
          <div class="card-label">{{ card.label }}</div>
          <div class="card-sub">{{ card.sub }}</div>
        </div>
        <div class="card-arrow">
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
            <path d="M3 7h8M7 3l4 4-4 4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
      </div>
    </div>

    <div class="footer-bar">
      <span>智能陪伴机器人控制平台</span>
      <span class="footer-sep">·</span>
      <span>安全 · 贴心 · 专业</span>
    </div>
  </div>
</template>

<style scoped>
.home-root {
  width: 100%; height: 100%;
  background: linear-gradient(150deg, #FFF9F5 0%, #FFF1E8 50%, #FFE8D8 100%);
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  padding: 32px 40px; box-sizing: border-box;
  overflow: hidden; position: relative;
  font-family: "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
}

/* 背景装饰 */
.bg-orb {
  position: absolute; border-radius: 50%; pointer-events: none; filter: blur(70px);
}
.bg-orb-1 {
  width: 520px; height: 520px; top: -200px; left: -140px;
  background: radial-gradient(circle, rgba(255,180,140,0.25) 0%, transparent 70%);
  animation: orbFloat 8s ease-in-out infinite;
}
.bg-orb-2 {
  width: 400px; height: 400px; bottom: -140px; right: -100px;
  background: radial-gradient(circle, rgba(255,140,100,0.18) 0%, transparent 70%);
  animation: orbFloat 10s ease-in-out 2s infinite;
}
.bg-orb-3 {
  width: 280px; height: 280px; top: 45%; left: 58%;
  background: radial-gradient(circle, rgba(255,200,160,0.12) 0%, transparent 70%);
  animation: orbFloat 9s ease-in-out 4s infinite;
}
@keyframes orbFloat {
  0%, 100% { transform: translate(0, 0) scale(1); }
  33%  { transform: translate(25px, -18px) scale(1.04); }
  66%  { transform: translate(-18px, 12px) scale(0.96); }
}

.bg-grid {
  position: absolute; inset: 0; pointer-events: none;
  background-image:
    linear-gradient(rgba(255,150,90,0.045) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255,150,90,0.045) 1px, transparent 1px);
  background-size: 52px 52px;
}

/* 欢迎区 */
.welcome-area {
  display: flex; flex-direction: column; align-items: center; gap: 10px;
  margin-bottom: 28px; position: relative; z-index: 1;
  animation: fadeUp 0.7s ease both;
}
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(14px); }
  to   { opacity: 1; transform: translateY(0); }
}

.welcome-badge {
  display: inline-flex; align-items: center; gap: 6px;
  background: rgba(255,255,255,0.88); backdrop-filter: blur(10px);
  border: 1px solid rgba(255,160,100,0.22); border-radius: 100px;
  padding: 6px 18px; font-size: 12px; color: #A06040; font-weight: 500;
  animation: fadeUp 0.6s ease both 0.1s;
}
.badge-dot {
  width: 7px; height: 7px; border-radius: 50%;
  background: #5AB060;
  box-shadow: 0 0 8px rgba(90,176,96,0.4);
  animation: blink 2s ease infinite;
}
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.35} }

.welcome-title {
  font-size: clamp(26px, 3.8vw, 42px);
  font-weight: 800; color: #2A1408;
  letter-spacing: -0.01em; line-height: 1.2;
  text-align: center; margin: 0;
  animation: fadeUp 0.6s ease both 0.15s;
}
.title-accent {
  background: linear-gradient(135deg, #FF6030, #FF9A60);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
}
.welcome-sub {
  font-size: 14px; color: #B08060; margin: 0; letter-spacing: 0.04em;
  animation: fadeUp 0.6s ease both 0.2s;
}

/* 统计条 */
.stats-row {
  display: flex; gap: 12px;
  width: 100%; max-width: 840px;
  margin-bottom: 20px; position: relative; z-index: 1;
}
.stat-item {
  flex: 1;
  background: rgba(255,255,255,0.78);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255,160,100,0.14);
  border-radius: 16px;
  padding: 14px 12px; text-align: center;
  animation: cardIn 0.5s ease both;
  transition: all 0.25s ease;
}
.stat-item:hover {
  transform: translateY(-3px);
  background: rgba(255,255,255,0.95);
  box-shadow: 0 8px 24px rgba(200,100,60,0.1);
  border-color: rgba(255,140,80,0.25);
}
.stat-value { font-size: 14px; font-weight: 700; color: #E06030; letter-spacing: 0.02em; }
.stat-label { font-size: 12px; color: #7A5040; font-weight: 600; margin-top: 2px; }
.stat-desc { font-size: 10.5px; color: #B09080; margin-top: 2px; }

/* 卡片网格 */
.cards-grid {
  width: 100%; max-width: 840px;
  display: grid; grid-template-columns: repeat(3, 1fr);
  gap: 12px; position: relative; z-index: 1;
}

/* 功能卡片 */
.func-card {
  background: rgba(255,255,255,0.85);
  border: 1px solid rgba(255,160,100,0.16);
  border-radius: 20px; padding: 20px 18px;
  display: flex; align-items: center; gap: 14px;
  cursor: pointer; position: relative; overflow: hidden;
  backdrop-filter: blur(14px);
  box-shadow: 0 4px 18px rgba(200,100,60,0.07);
  transition: all 0.3s cubic-bezier(0.34, 1.4, 0.64, 1);
  animation: cardIn 0.55s ease both;
}
@keyframes cardIn {
  from { opacity: 0; transform: translateY(18px); }
  to   { opacity: 1; transform: translateY(0); }
}

/* 顶部彩色装饰条 */
.card-accent {
  position: absolute; top: 0; left: 12px; right: 12px;
  height: 3px; border-radius: 0 0 3px 3px;
  opacity: 0; transform: scaleX(0.5);
  transition: all 0.3s cubic-bezier(0.34, 1.4, 0.64, 1);
}
.func-card:hover .card-accent {
  opacity: 1; transform: scaleX(1);
}

.card-glow {
  position: absolute; inset: 0; border-radius: 20px; pointer-events: none;
  background: radial-gradient(circle at 30% 50%, rgba(255,140,80,0.09) 0%, transparent 65%);
  opacity: 0; transition: opacity 0.3s ease;
}
.func-card:hover {
  transform: translateY(-6px) scale(1.02);
  border-color: rgba(255,140,80,0.32);
  box-shadow: 0 16px 40px rgba(200,100,60,0.15);
  background: rgba(255,255,255,0.97);
}
.func-card:hover .card-glow { opacity: 1; }
.func-card:active { transform: translateY(-2px) scale(0.99); }

/* 图标 */
.card-icon {
  width: 52px; height: 52px; border-radius: 14px;
  background: linear-gradient(135deg, #FFF0E8, #FFDECA);
  border: 1px solid rgba(255,160,100,0.22);
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0; color: #D86030;
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.func-card:hover .card-icon {
  background: linear-gradient(135deg, #FF9A76, #FF5A30);
  color: white; border-color: transparent;
  box-shadow: 0 8px 24px rgba(255,90,50,0.35);
  transform: scale(1.1) rotate(-5deg);
}

/* 文字 */
.card-text { flex: 1; min-width: 0; }
.card-label { font-size: 15px; font-weight: 700; color: #2A1408; letter-spacing: 0.01em; transition: color 0.2s; }
.func-card:hover .card-label { color: #C04820; }
.card-sub { font-size: 11.5px; color: #B09080; margin-top: 3px; }

/* 箭头 */
.card-arrow { color: rgba(200,140,100,0.25); transition: all 0.25s ease; flex-shrink: 0; }
.func-card:hover .card-arrow { color: #D86030; transform: translateX(5px); }

/* 页脚 */
.footer-bar {
  display: flex; align-items: center; gap: 10px;
  margin-top: 24px; font-size: 11.5px; color: rgba(160,100,70,0.45);
  position: relative; z-index: 1;
  animation: fadeUp 0.7s ease 0.6s both;
}
.footer-sep { opacity: 0.35; }

@media (max-width: 768px) {
  .home-root { padding: 20px 16px; justify-content: flex-start; padding-top: 40px; }
  .stats-row { flex-wrap: wrap; gap: 8px; }
  .stat-item { flex: 1 1 calc(50% - 8px); min-width: 0; padding: 12px 8px; }
  .cards-grid { grid-template-columns: 1fr; max-width: 100%; gap: 10px; }
  .func-card { padding: 16px 14px; }
  .welcome-title { font-size: 22px; }
  .welcome-sub { font-size: 12px; }
}
@media (min-width: 769px) and (max-width: 1024px) {
  .cards-grid { grid-template-columns: repeat(2, 1fr); }
  .stats-row { flex-wrap: wrap; }
  .stat-item { flex: 1 1 calc(50% - 8px); }
}
</style>
