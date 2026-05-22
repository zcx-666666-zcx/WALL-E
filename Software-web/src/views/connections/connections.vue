<script setup>
import { ref } from 'vue'

const features = [
  {
    icon: `<svg width="22" height="22" viewBox="0 0 22 22" fill="none"><circle cx="11" cy="11" r="8" stroke="currentColor" stroke-width="1.6"/><path d="M7 11h2.5l1-4 2 8 1.5-4H15" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>`,
    label: '蓝牙连接', sub: '近距离设备配对',
    status: '开发中', color: '#2196F3'
  },
  {
    icon: `<svg width="22" height="22" viewBox="0 0 22 22" fill="none"><path d="M6 7.5A5.5 5.5 0 0117 7M8 10.5a3 3 0 015.5 0" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/><circle cx="11" cy="15" r="2" fill="currentColor"/></svg>`,
    label: 'Wi-Fi 配置', sub: '网络连接管理',
    status: '开发中', color: '#4CAF50'
  },
  {
    icon: `<svg width="22" height="22" viewBox="0 0 22 22" fill="none"><rect x="4" y="4" width="14" height="14" rx="2.5" stroke="currentColor" stroke-width="1.6"/><path d="M8 9h6M8 12.5h4M8 16h2" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/></svg>`,
    label: 'MQTT 消息', sub: 'IoT 消息队列',
    status: '开发中', color: '#FF9800'
  },
  {
    icon: `<svg width="22" height="22" viewBox="0 0 22 22" fill="none"><circle cx="11" cy="11" r="9" stroke="currentColor" stroke-width="1.6"/><circle cx="11" cy="11" r="3.5" stroke="currentColor" stroke-width="1.3"/><path d="M11 2v3.5M11 16.5V20M2 11h3.5M16.5 11H20" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/></svg>`,
    label: '卫星定位', sub: 'GPS/北斗定位',
    status: '规划中', color: '#9C27B0'
  },
  {
    icon: `<svg width="22" height="22" viewBox="0 0 22 22" fill="none"><rect x="5" y="3" width="12" height="16" rx="2.5" stroke="currentColor" stroke-width="1.6"/><path d="M8 17h6" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/></svg>`,
    label: '手机绑定', sub: '移动端扫码绑定',
    status: '开发中', color: '#E91E63'
  },
  {
    icon: `<svg width="22" height="22" viewBox="0 0 22 22" fill="none"><path d="M9 2a7 7 0 017 7c0 5-7 10.5-7 10.5S2 14 2 9a7 7 0 017-7z" stroke="currentColor" stroke-width="1.6"/><circle cx="9" cy="9" r="2" stroke="currentColor" stroke-width="1.3"/></svg>`,
    label: '地理围栏', sub: '电子围栏告警',
    status: '规划中', color: '#795548'
  }
]
</script>

<template>
  <div class="conn-root">

    <div class="page-header">
      <div class="page-header-left">
        <div class="page-title-icon">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <circle cx="8" cy="8" r="6" stroke="white" stroke-width="1.4"/>
            <path d="M8 4v4l3 2" stroke="white" stroke-width="1.3" stroke-linecap="round"/>
          </svg>
        </div>
        <div>
          <div class="page-title">更多连接</div>
          <div class="page-sub">扩展连接方式与高级功能</div>
        </div>
      </div>
    </div>

    <div class="cards-grid">
      <div
        v-for="(item, i) in features"
        :key="item.label"
        class="conn-card"
        :style="{ animationDelay: `${i * 0.05}s` }"
      >
        <div class="card-icon" :style="{ color: item.color }" v-html="item.icon"></div>
        <div class="card-text">
          <div class="card-label">{{ item.label }}</div>
          <div class="card-sub">{{ item.sub }}</div>
        </div>
        <span class="card-badge" :style="{ background: item.color + '15', color: item.color, borderColor: item.color + '30' }">
          {{ item.status }}
        </span>
      </div>
    </div>

    <div class="footer-note">
      <svg width="14" height="14" viewBox="0 0 14 14" fill="none" style="flex-shrink:0">
        <circle cx="7" cy="7" r="6" stroke="#C4A898" stroke-width="1.2"/>
        <path d="M7 6v3.5M7 4.5v.5" stroke="#C4A898" stroke-width="1.3" stroke-linecap="round"/>
      </svg>
      更多连接方式正在开发中，敬请期待
    </div>

  </div>
</template>

<style scoped>
.conn-root {
  width: 100%; height: 100%;
  padding: 20px 24px; box-sizing: border-box;
  display: flex; flex-direction: column; gap: 20px;
  overflow: hidden;
  font-family: "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
}

.page-header { display: flex; align-items: center; justify-content: space-between; flex-shrink: 0; }
.page-header-left { display: flex; align-items: center; gap: 12px; }
.page-title-icon {
  width: 40px; height: 40px; border-radius: 12px;
  background: linear-gradient(135deg, #FF9A76, #FF6040);
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 4px 12px rgba(255,96,64,0.28); flex-shrink: 0;
}
.page-title { font-size: 18px; font-weight: 700; color: #3A2010; letter-spacing: 0.01em; }
.page-sub { font-size: 12px; color: #B09080; margin-top: 2px; }

.cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 12px;
  flex: 1; overflow-y: auto; align-content: start;
}

.conn-card {
  background: #FFFFFF;
  border: 1px solid rgba(255,160,120,0.12);
  border-radius: 16px; padding: 20px;
  display: flex; align-items: center; gap: 14px;
  box-shadow: 0 2px 12px rgba(200,90,50,0.05);
  transition: all 0.25s cubic-bezier(0.34, 1.4, 0.64, 1);
  animation: cardIn 0.5s ease both;
  cursor: default;
}
@keyframes cardIn {
  from { opacity: 0; transform: translateY(12px); }
  to   { opacity: 1; transform: translateY(0); }
}
.conn-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 24px rgba(200,90,50,0.1);
  border-color: rgba(255,140,80,0.25);
}

.card-icon {
  width: 48px; height: 48px; border-radius: 14px;
  background: #FFFAF7;
  border: 1px solid rgba(255,160,120,0.12);
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0; transition: transform 0.3s ease;
}
.conn-card:hover .card-icon { transform: scale(1.05); }

.card-text { flex: 1; min-width: 0; }
.card-label { font-size: 14px; font-weight: 700; color: #3A2010; }
.card-sub { font-size: 11.5px; color: #B09080; margin-top: 3px; }

.card-badge {
  font-size: 11px; font-weight: 600;
  border-radius: 100px; padding: 3px 10px;
  border: 1px solid transparent; flex-shrink: 0;
  white-space: nowrap;
}

.footer-note {
  display: flex; align-items: center; gap: 7px;
  font-size: 12px; color: #C4A898; flex-shrink: 0;
  padding: 0 4px;
}
</style>
