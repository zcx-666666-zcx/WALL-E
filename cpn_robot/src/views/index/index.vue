<script setup>
import { useRouter } from 'vue-router'
const router = useRouter()

const goPage = (path) => router.push(path)
const goToWalleInterface = () => window.open('http://10.188.145.97:5000', '_blank')

const cards = [
  {
    label: '事件管理', sub: '提醒与日程',
    icon: `<svg width="26" height="26" viewBox="0 0 26 26" fill="none"><rect x="3" y="2" width="20" height="22" rx="3" stroke="currentColor" stroke-width="1.7"/><path d="M8 9h10M8 14h10M8 19h6" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg>`,
    action: () => goPage('/elementlist')
  },
  {
    label: 'AI 设置', sub: '人设与对话',
    icon: `<svg width="26" height="26" viewBox="0 0 26 26" fill="none"><rect x="4" y="8" width="18" height="13" rx="2.5" stroke="currentColor" stroke-width="1.7"/><path d="M9 8V6a4 4 0 018 0v2" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"/><circle cx="10" cy="15" r="1.5" fill="currentColor"/><circle cx="16" cy="15" r="1.5" fill="currentColor"/></svg>`,
    action: () => goPage('/Agent')
  },
  {
    label: '命令查询', sub: '指令与记录',
    icon: `<svg width="26" height="26" viewBox="0 0 26 26" fill="none"><rect x="2" y="4" width="22" height="18" rx="3" stroke="currentColor" stroke-width="1.7"/><path d="M7 10l4 4-4 4M15 18h5" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/></svg>`,
    action: () => goPage('/command')
  },
  {
    label: '远程监护', sub: '实时视频',
    icon: `<svg width="26" height="26" viewBox="0 0 26 26" fill="none"><rect x="2" y="6" width="16" height="14" rx="2.5" stroke="currentColor" stroke-width="1.7"/><path d="M18 10l6-3v12l-6-3V10z" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round"/></svg>`,
    action: () => goPage('/video')
  },
  {
    label: '远程遥控', sub: '机器人控制',
    icon: `<svg width="26" height="26" viewBox="0 0 26 26" fill="none"><rect x="7" y="3" width="12" height="20" rx="3" stroke="currentColor" stroke-width="1.7"/><circle cx="13" cy="18" r="2.5" stroke="currentColor" stroke-width="1.5"/><path d="M13 7v3M11.5 8.5h3" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg>`,
    action: () => goToWalleInterface()
  },
  {
    label: '健康监测', sub: '体征与状态',
    icon: `<svg width="26" height="26" viewBox="0 0 26 26" fill="none"><path d="M13 22S3 16 3 10a6 6 0 0110-4.47A6 6 0 0123 10c0 6-10 12-10 12z" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round"/><path d="M7 12h3l2-4 2 8 2-4h3" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>`,
    action: () => goPage('/healthy')
  }
]
</script>

<template>
  <div class="home-root">
    <div class="bg-orb bg-orb-1"></div>
    <div class="bg-orb bg-orb-2"></div>
    <div class="bg-orb bg-orb-3"></div>
    <div class="bg-grid"></div>

    <div class="welcome-area">
      <h1 class="welcome-title">
        欢迎使用
        <span class="title-accent">智能陪伴</span>
        机器人
      </h1>
      <p class="welcome-sub">守护每一位长辈，让关爱触手可及</p>
    </div>

    <div class="cards-grid">
      <div
        v-for="(card, i) in cards"
        :key="card.label"
        class="func-card"
        :style="{ animationDelay: `${i * 0.07}s` }"
        @click="card.action"
      >
        <div class="card-glow"></div>
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
}
.bg-orb-2 {
  width: 400px; height: 400px; bottom: -140px; right: -100px;
  background: radial-gradient(circle, rgba(255,140,100,0.18) 0%, transparent 70%);
}
.bg-orb-3 {
  width: 280px; height: 280px; top: 45%; left: 58%;
  background: radial-gradient(circle, rgba(255,200,160,0.12) 0%, transparent 70%);
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
  margin-bottom: 32px; position: relative; z-index: 1;
  animation: fadeUp 0.7s ease both;
}
.welcome-badge {
  display: inline-flex; align-items: center; gap: 6px;
  background: rgba(255,255,255,0.85); backdrop-filter: blur(10px);
  border: 1px solid rgba(255,160,100,0.22); border-radius: 100px;
  padding: 5px 16px; font-size: 12px; color: #A06040; font-weight: 500;
}
.badge-dot {
  width: 6px; height: 6px; border-radius: 50%;
  background: #5AB060; animation: blink 2s ease infinite;
}
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.35} }

.welcome-title {
  font-size: clamp(26px, 3.8vw, 46px);
  font-weight: 800; color: #2A1408;
  letter-spacing: -0.01em; line-height: 1.2;
  text-align: center; margin: 0;
}
.title-accent {
  background: linear-gradient(90deg, #FF6030, #FF9A60);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
}
.welcome-sub { font-size: 14px; color: #B08060; margin: 0; letter-spacing: 0.04em; }

/* 卡片网格 */
.cards-grid {
  width: 100%; max-width: 840px;
  display: grid; grid-template-columns: repeat(3, 1fr);
  gap: 12px; position: relative; z-index: 1;
}

/* 功能卡片 */
.func-card {
  background: rgba(255,255,255,0.88);
  border: 1px solid rgba(255,160,100,0.16);
  border-radius: 20px; padding: 20px 18px;
  display: flex; align-items: center; gap: 14px;
  cursor: pointer; position: relative; overflow: hidden;
  backdrop-filter: blur(14px);
  box-shadow: 0 4px 18px rgba(200,100,60,0.07);
  transition: all 0.28s cubic-bezier(0.34, 1.4, 0.64, 1);
  animation: cardIn 0.55s ease both;
}
@keyframes cardIn {
  from { opacity: 0; transform: translateY(18px); }
  to   { opacity: 1; transform: translateY(0); }
}
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(14px); }
  to   { opacity: 1; transform: translateY(0); }
}

.card-glow {
  position: absolute; inset: 0; border-radius: 20px; pointer-events: none;
  background: radial-gradient(circle at 30% 50%, rgba(255,140,80,0.09) 0%, transparent 65%);
  opacity: 0; transition: opacity 0.3s ease;
}
.func-card:hover { transform: translateY(-5px) scale(1.015); border-color: rgba(255,140,80,0.32); box-shadow: 0 14px 38px rgba(200,100,60,0.15); background: rgba(255,255,255,0.97); }
.func-card:hover .card-glow { opacity: 1; }
.func-card:active { transform: translateY(-2px) scale(1.005); }

/* 图标 */
.card-icon {
  width: 52px; height: 52px; border-radius: 14px;
  background: linear-gradient(135deg, #FFF0E8, #FFDECA);
  border: 1px solid rgba(255,160,100,0.22);
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0; color: #D86030;
  transition: all 0.28s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.func-card:hover .card-icon {
  background: linear-gradient(135deg, #FF9A76, #FF5A30);
  color: white; border-color: transparent;
  box-shadow: 0 6px 20px rgba(255,90,50,0.35);
  transform: scale(1.08) rotate(-4deg);
}

/* 文字 */
.card-text { flex: 1; min-width: 0; }
.card-label { font-size: 15px; font-weight: 700; color: #2A1408; letter-spacing: 0.01em; transition: color 0.2s; }
.func-card:hover .card-label { color: #C04820; }
.card-sub { font-size: 11.5px; color: #B09080; margin-top: 3px; }

/* 箭头 */
.card-arrow { color: rgba(200,140,100,0.28); transition: all 0.25s ease; flex-shrink: 0; }
.func-card:hover .card-arrow { color: #D86030; transform: translateX(4px); }

/* 页脚 */
.footer-bar {
  display: flex; align-items: center; gap: 10px;
  margin-top: 24px; font-size: 11.5px; color: rgba(160,100,70,0.45);
  position: relative; z-index: 1;
  animation: fadeUp 0.7s ease 0.5s both;
}
.footer-sep { opacity: 0.35; }
</style>