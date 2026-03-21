<template>
  <div>
    <h3>舵机控制</h3>

    <!-- 模式 -->
    <div>
      <label>
        <input type="radio" value="auto" v-model="mode" @change="setMode">
        自动
      </label>

      <label>
        <input type="radio" value="manual" v-model="mode" @change="setMode">
        手动
      </label>
    </div>

    <hr />

    <!-- 头部 -->
    <div>
      <div>头部旋转: {{ head }}</div>
      <input type="range" min="0" max="100" v-model="head" @change="updateServo('G', head)" />
    </div>

    <!-- 脖子 -->
    <div>
      <div>脖子(上): {{ neckTop }}</div>
      <input type="range" min="0" max="100" v-model="neckTop" @change="updateServo('T', neckTop)" />
    </div>

    <div>
      <div>脖子(下): {{ neckBottom }}</div>
      <input type="range" min="0" max="100" v-model="neckBottom" @change="updateServo('B', neckBottom)" />
    </div>

    <!-- 预设 -->
    <div>
      <button @click="preset('f')">抬头</button>
      <button @click="preset('g')">回正</button>
      <button @click="preset('h')">低头</button>
    </div>

    <hr />

    <!-- 手臂 -->
    <div>
      <div>左臂: {{ armLeft }}</div>
      <input type="range" min="0" max="100" v-model="armLeft" @change="updateServo('L', armLeft)" />
    </div>

    <div>
      <div>右臂: {{ armRight }}</div>
      <input type="range" min="0" max="100" v-model="armRight" @change="updateServo('R', armRight)" />
    </div>

    <!-- 眼睛 -->
    <div>
      <div>左眼: {{ eyeLeft }}</div>
      <input type="range" min="0" max="100" v-model="eyeLeft" @change="updateServo('E', eyeLeft)" />
    </div>

    <div>
      <div>右眼: {{ eyeRight }}</div>
      <input type="range" min="0" max="100" v-model="eyeRight" @change="updateServo('U', eyeRight)" />
    </div>

  </div>
</template>

<script setup>
import { ref } from 'vue'

/* 状态 */
const mode = ref('manual')

const head = ref(50)
const neckTop = ref(50)
const neckBottom = ref(50)

const armLeft = ref(50)
const armRight = ref(50)

const eyeLeft = ref(50)
const eyeRight = ref(50)

/* 方法 */

function setMode() {
  console.log('模式:', mode.value)

  // 接后端
  fetch('/api/settings', {
    method: 'POST',
    body: JSON.stringify({ animeMode: mode.value === 'auto' ? 1 : 0 })
  })
}

function updateServo(type, value) {
  console.log('servo:', type, value)

  // 👉 你原来的接口可以接这里
  fetch(`/api/servo?type=${type}&value=${value}`)
}

function preset(code) {
  console.log('preset:', code)

  fetch(`/api/preset?code=${code}`)
}
</script>

<style scoped>
h3 {
  margin-bottom: 10px;
}

div {
  margin-bottom: 10px;
}

input[type="range"] {
  width: 200px;
}
</style>