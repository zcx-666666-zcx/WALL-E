<template>
  <div class="control-panel">
    <div v-if="!machine" class="no-device">请选择设备</div>
    <div v-else-if="!machine.robotIp" class="no-device warn">未配置 IP</div>

    <template v-else>
      <div class="coords">
        <span class="coord-x">X: {{ stickX.toFixed(2) }}</span>
        <span class="coord-y">Y: {{ stickY.toFixed(2) }}</span>
      </div>

      <div class="joystick-container">
        <div
          class="joystick-base"
          @mousedown="startDrag"
          @mousemove="onDrag"
          @mouseup="stopDrag"
          @mouseleave="stopDrag"
          @touchstart.prevent="startTouch"
          @touchmove.prevent="onTouch"
          @touchend.prevent="stopDrag"
        >
          <div class="joystick-stick" :style="stickStyle"></div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { RobotMotorApi } from '@/api/users'

const props = defineProps({
  machine: { type: Object, default: null }
})

let lastSend = 0
const dragging = ref(false)
const x = ref(0)
const y = ref(0)
const stickX = ref(0)
const stickY = ref(0)

const stickStyle = computed(() => ({
  transform: `translate(${x.value}px, ${y.value}px)`
}))

function sendMotor(sx, sy) {
  if (!props.machine?.id) return
  const now = Date.now()
  if (now - lastSend < 50) return
  lastSend = now
  RobotMotorApi({
    machineId: props.machine.id,
    stickX: +sx.toFixed(2),
    stickY: +sy.toFixed(2)
  }).catch(() => {})
}

function beginDrag() {
  dragging.value = true
}

function doDrag(cx, cy, rect) {
  if (!dragging.value) return
  const centerX = rect.width / 2
  const centerY = rect.height / 2
  let dx = cx - centerX
  let dy = cy - centerY

  const maxRadius = rect.width / 2
  const distance = Math.sqrt(dx * dx + dy * dy)
  if (distance > maxRadius) {
    dx = (dx / distance) * maxRadius
    dy = (dy / distance) * maxRadius
  }

  const deadzone = 10
  if (Math.abs(dx) < deadzone) dx = 0
  if (Math.abs(dy) < deadzone) dy = 0

  x.value = dx
  y.value = dy

  const max = 75
  const sX = dx / max
  const sY = -dy / max
  stickX.value = Math.max(-1, Math.min(1, sX))
  stickY.value = Math.max(-1, Math.min(1, sY))

  sendMotor(stickX.value, stickY.value)
}

function startDrag(e) {
  beginDrag()
  const rect = e.currentTarget.getBoundingClientRect()
  doDrag(e.clientX - rect.left, e.clientY - rect.top, rect)
}
function onDrag(e) {
  if (!dragging.value) return
  const rect = e.currentTarget.getBoundingClientRect()
  doDrag(e.clientX - rect.left, e.clientY - rect.top, rect)
}

function startTouch(e) {
  beginDrag()
  const touch = e.touches[0]
  const rect = e.currentTarget.getBoundingClientRect()
  doDrag(touch.clientX - rect.left, touch.clientY - rect.top, rect)
}
function onTouch(e) {
  const touch = e.touches[0]
  const rect = e.currentTarget.getBoundingClientRect()
  doDrag(touch.clientX - rect.left, touch.clientY - rect.top, rect)
}

function stopDrag() {
  dragging.value = false
  x.value = 0
  y.value = 0
  stickX.value = 0
  stickY.value = 0
  sendMotor(0, 0)
}
</script>

<style scoped>
.control-panel { text-align: center; }

.no-device { padding: 20px 10px; color: #B09080; font-size: 13px; }
.no-device.warn { color: #EF6C00; }

.coords {
  font-family: monospace; font-size: 12px; color: #7A5040;
  margin-bottom: 16px; display: flex; gap: 14px; justify-content: center;
}
.coord-x, .coord-y { background: #FFF5F0; padding: 4px 10px; border-radius: 6px; }

.joystick-container { display: flex; justify-content: center; }
.joystick-base {
  width: 160px; height: 160px; border-radius: 50%;
  background: radial-gradient(circle at center, #FFF5F0, #FFE0CC);
  border: 2px solid rgba(255,140,80,0.3);
  position: relative; cursor: pointer; user-select: none;
  touch-action: none;
}
.joystick-stick {
  width: 46px; height: 46px; border-radius: 50%;
  background: linear-gradient(135deg, #FF9A76, #FF6040);
  box-shadow: 0 3px 12px rgba(255,96,64,0.35);
  position: absolute; top: 50%; left: 50%;
  margin: -23px 0 0 -23px;
  transition: transform 0.02s linear;
}
</style>
