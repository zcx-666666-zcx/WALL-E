<script setup>
import { ref } from 'vue'

import CameraPanel from './components/CameraPanel.vue'
import ControlPanel from './components/ControlPanel.vue'
import ServoPanel from './components/ServoPanel.vue'
import AnimationPanel from './components/AnimationPanel.vue'
import AudioPanel from './components/AudioPanel.vue'
import SettingsPanel from './components/SettingsPanel.vue'

const tabs = ['摄像头','遥控','舵机','动画','音效','设置']
const currentTab = ref('舵机') // 默认先看舵机
</script>

<template>
  <div class="page">
    <h2>WALL·E 控制台</h2>

    <!-- tabs -->
    <div class="tabs">
      <button
        v-for="t in tabs"
        :key="t"
        @click="currentTab = t"
      >
        {{ t }}
      </button>
    </div>

    <!-- 内容 -->
    <div class="panel">
      <CameraPanel v-if="currentTab==='摄像头'" />
      <ControlPanel v-if="currentTab==='遥控'" />
      <ServoPanel v-if="currentTab==='舵机'" />
      <AnimationPanel v-if="currentTab==='动画'" />
      <AudioPanel v-if="currentTab==='音效'" />
      <SettingsPanel v-if="currentTab==='设置'" />
    </div>
  </div>
</template>

<style scoped>
.page {
  padding: 20px;
}

.tabs button {
  margin-right: 10px;
  padding: 6px 12px;
  cursor: pointer;
}

.panel {
  margin-top: 20px;
}
</style>