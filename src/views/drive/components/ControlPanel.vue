<template>
  <div class="control-panel">
    <h3>遥控控制</h3>

    <!-- 手柄状态 -->
    <div class="status">
      <span>手柄状态：</span>
      <span :class="connected ? 'ok' : 'bad'">
        {{ connected ? '已连接' : '未连接' }}
      </span>
    </div>

    <!-- 坐标显示 -->
    <div class="coords">
      x: {{ x }} | y: {{ y }}
    </div>

    <!-- 虚拟摇杆 -->
    <div class="joystick-container">
      <div
        class="joystick-base"
        @mousedown="startDrag"
        @mousemove="onDrag"
        @mouseup="stopDrag"
        @mouseleave="stopDrag"
      >
        <div
          class="joystick-stick"
          :style="stickStyle"
        ></div>
      </div>
    </div>

    <!-- 控制按钮（备用） -->
    <div class="buttons">
      <button @click="move('forward')">前进</button>
      <button @click="move('backward')">后退</button>
      <button @click="move('left')">左转</button>
      <button @click="move('right')">右转</button>
      <button @click="move('stop')">停止</button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

/* ---------------- 状态 ---------------- */

const connected = ref(false)
let lastSend = 0

const dragging = ref(false)
const x = ref(0)
const y = ref(0)

/* ---------------- 样式 ---------------- */

const stickStyle = computed(() => {
  return {
    transform: `translate(${x.value}px, ${y.value}px)`
  }
})

/* ---------------- 方法 ---------------- */

function sendMotor(motor) {
  const now = Date.now()
  if (now - lastSend < 50) return // 20fps
  lastSend = now
  
  fetch('/api/motor', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(motor)
  })
}

function stopDrag() {
  dragging.value = false

  x.value = 0
  y.value = 0

  sendMotor({ left: 0, right: 0 }) // 停车
}

function calculateMotor(x, y) {
  // 归一化（假设最大 75px）
  const max = 75

  let nx = x / max
  let ny = -y / max

  let left = ny + nx
  let right = ny - nx

  left = Math.max(-1, Math.min(1, left))
  right = Math.max(-1, Math.min(1, right))

  return {
    left: Math.round(left * 255),
    right: Math.round(right * 255)
  }
}

function startDrag(e) {
  dragging.value = true
  connected.value = true
}

function onDrag(e) {
  if (!dragging.value) return

  const rect = e.currentTarget.getBoundingClientRect()

  const centerX = rect.width / 2
  const centerY = rect.height / 2

  let dx = e.offsetX - centerX
  let dy = e.offsetY - centerY

  const maxRadius = rect.width / 2

  // ✅ 限制在圆内
  const distance = Math.sqrt(dx * dx + dy * dy)

  if (distance > maxRadius) {
    dx = (dx / distance) * maxRadius
    dy = (dy / distance) * maxRadius
  }

  // ✅ Deadzone（中心10px内不动）
  const deadzone = 10
  if (Math.abs(dx) < deadzone) dx = 0
  if (Math.abs(dy) < deadzone) dy = 0

  x.value = dx
  y.value = dy

  const motor = calculateMotor(x.value, y.value)
  sendMotor(motor)
}

function move(dir) {
  console.log('移动:', dir)
}
</script>

<style scoped>
.control-panel {
  text-align: center;
}

.status {
  margin-bottom: 10px;
}

.ok {
  color: green;
}

.bad {
  color: red;
}

.coords {
  margin-bottom: 10px;
}

/* 摇杆 */
.joystick-container {
  display: flex;
  justify-content: center;
  margin: 20px 0;
}

.joystick-base {
  width: 150px;
  height: 150px;
  border: 2px solid #ccc;
  border-radius: 50%;
  position: relative;
}

.joystick-stick {
  width: 40px;
  height: 40px;
  background: #333;
  border-radius: 50%;
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

/* 按钮 */
.buttons button {
  margin: 5px;
  padding: 6px 12px;
}
</style>