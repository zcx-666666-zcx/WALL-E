<template>
  <div class="servo-panel">
    <h3>舵机控制</h3>

    <div v-if="!machine" class="no-device">请先在顶部选择一个机器人设备</div>
    <div v-else-if="!machine.robotIp" class="no-device warn">当前设备未配置 IP 地址</div>

    <template v-else>
      <div class="mode-row">
        <label><input type="radio" value="manual" v-model="mode" @change="setMode"> 手动</label>
        <label><input type="radio" value="auto" v-model="mode" @change="setMode"> 自动</label>
      </div>

      <hr />

      <div v-for="s in servos" :key="s.id" class="servo-row">
        <div class="servo-label">{{ s.label }}: {{ s.val }}</div>
        <input type="range" min="0" max="100" v-model.number="s.val" @change="updateServo(s.id, s.val)" />
      </div>

      <hr />

      <div class="preset-row">
        <button @click="updateServo('G', 50); updateServo('T', 50); updateServo('B', 50)">头部回正</button>
        <button @click="updateServo('G', 50); updateServo('T', 30); updateServo('B', 70)">抬头</button>
        <button @click="updateServo('G', 50); updateServo('T', 70); updateServo('B', 30)">低头</button>
      </div>

      <hr />

      <div class="servo-row">
        <div class="servo-label">左臂: {{ armLeft }}</div>
        <input type="range" min="0" max="100" v-model.number="armLeft" @change="updateServo('L', armLeft)" />
      </div>
      <div class="servo-row">
        <div class="servo-label">右臂: {{ armRight }}</div>
        <input type="range" min="0" max="100" v-model.number="armRight" @change="updateServo('R', armRight)" />
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { RobotServoApi, RobotSettingsApi } from '@/api/users'

const props = defineProps({
  machine: { type: Object, default: null }
})

const mode = ref('manual')

const servos = reactive([
  { id: 'G', label: '头部旋转', val: 50 },
  { id: 'T', label: '脖子(上)', val: 50 },
  { id: 'B', label: '脖子(下)', val: 50 },
  { id: 'E', label: '左眼',     val: 50 },
  { id: 'U', label: '右眼',     val: 50 },
])
const armLeft = ref(50)
const armRight = ref(50)

function setMode() {
  RobotSettingsApi({
    machineId: props.machine.id,
    type: 'animeMode',
    value: mode.value === 'auto' ? 1 : 0
  }).catch(() => {})
}

function updateServo(type, value) {
  RobotServoApi({
    machineId: props.machine.id,
    servo: type,
    value: value
  }).catch(() => {})
}
</script>

<style scoped>
h3 { margin-bottom: 14px; }

.no-device {
  padding: 40px 20px; color: #B09080; font-size: 14px; text-align: center;
}
.no-device.warn { color: #EF6C00; }

.mode-row { display: flex; gap: 20px; font-size: 13px; margin-bottom: 10px; }
.mode-row label { cursor: pointer; color: #5A3020; }

.servo-row { margin-bottom: 12px; }
.servo-label { font-size: 13px; color: #5A3020; font-weight: 600; margin-bottom: 4px; }
.servo-row input[type="range"] { width: 220px; }

.preset-row { display: flex; gap: 8px; margin-bottom: 10px; }
.preset-row button {
  height: 32px; padding: 0 14px; border-radius: 8px;
  border: 1px solid rgba(255,140,80,0.3);
  background: #FFF5F0; color: #D06030; font-size: 12.5px;
  font-weight: 600; font-family: inherit; cursor: pointer;
  transition: all 0.15s;
}
.preset-row button:hover { background: #FFE8DC; }

hr { border: none; border-top: 1px solid rgba(255,160,120,0.15); margin: 14px 0; }
</style>
