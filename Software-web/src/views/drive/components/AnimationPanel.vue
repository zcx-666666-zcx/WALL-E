<template>
  <div class="animation-panel">
    <h3>动画控制</h3>

    <div v-if="!machine" class="no-device">请先在顶部选择一个机器人设备</div>
    <div v-else-if="!machine.robotIp" class="no-device warn">当前设备未配置 IP 地址</div>

    <template v-else>
      <div class="anim-grid">
        <button
          v-for="anim in animations"
          :key="anim.clip"
          class="anim-btn"
          @click="play(anim.clip)"
        >
          <span class="anim-icon">{{ anim.icon }}</span>
          <span class="anim-label">{{ anim.label }}</span>
        </button>
      </div>
    </template>
  </div>
</template>

<script setup>
import { RobotAnimateApi } from '@/api/users'

const props = defineProps({
  machine: { type: Object, default: null }
})

const animations = [
  { clip: 0, icon: '🏠', label: '复位' },
  { clip: 1, icon: '🚀', label: '启动' },
  { clip: 2, icon: '🤔', label: '好奇' },
  { clip: 3, icon: '😊', label: '开心' },
  { clip: 4, icon: '👋', label: '挥手' },
  { clip: 5, icon: '😢', label: '难过' },
]

function play(clip) {
  RobotAnimateApi({
    machineId: props.machine.id,
    clip: String(clip)
  }).catch(() => {})
}
</script>

<style scoped>
h3 { margin-bottom: 14px; }

.no-device { padding: 40px 20px; color: #B09080; font-size: 14px; text-align: center; }
.no-device.warn { color: #EF6C00; }

.anim-grid {
  display: grid; grid-template-columns: repeat(3, 1fr);
  gap: 10px; max-width: 360px;
}
.anim-btn {
  display: flex; flex-direction: column; align-items: center; gap: 6px;
  height: 90px; border-radius: 14px;
  border: 1px solid rgba(255,160,120,0.2);
  background: #FFFFFF; cursor: pointer;
  transition: all 0.2s ease; font-family: inherit;
}
.anim-btn:hover {
  background: #FFF5F0; border-color: rgba(255,140,80,0.4);
  transform: translateY(-2px); box-shadow: 0 4px 14px rgba(255,96,64,0.15);
}
.anim-btn:active { transform: scale(0.95); }
.anim-icon { font-size: 28px; }
.anim-label { font-size: 12px; font-weight: 600; color: #5A3020; }
</style>
