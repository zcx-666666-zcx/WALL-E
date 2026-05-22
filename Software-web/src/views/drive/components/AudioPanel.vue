<template>
  <div class="audio-panel">
    <h3>音效与语音</h3>

    <div v-if="!machine" class="no-device">请先在顶部选择一个机器人设备</div>
    <div v-else-if="!machine.robotIp" class="no-device warn">当前设备未配置 IP 地址</div>

    <template v-else>
      <h4>音效列表</h4>
      <div v-for="audio in audioList" :key="audio.name" class="audio-item" @click="play(audio)">
        <span class="audio-icon">🔊</span>
        <span class="audio-label">{{ audio.label }}</span>
        <span class="audio-dur">{{ audio.duration }}s</span>
      </div>

      <hr />

      <h4>文字转语音 (TTS)</h4>
      <div class="tts-row">
        <input v-model="ttsText" placeholder="输入要让机器人说的话..." @keyup.enter="playTTS" />
        <button @click="playTTS">朗读</button>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { RobotSettingsApi } from '@/api/users'

const props = defineProps({
  machine: { type: Object, default: null }
})

const audioList = ref([
  { name: 'hello', label: '打招呼', duration: 2 },
  { name: 'happy', label: '开心',   duration: 3 },
  { name: 'sad',   label: '悲伤',   duration: 2 },
  { name: 'beep',  label: '哔声',   duration: 1 }
])
const ttsText = ref('')

function play(audio) {
  RobotSettingsApi({
    machineId: props.machine.id,
    type: 'audio',
    value: audio.name
  }).catch(() => {})
}

function playTTS() {
  if (!ttsText.value.trim()) return
  RobotSettingsApi({
    machineId: props.machine.id,
    type: 'tts',
    value: ttsText.value.trim()
  }).catch(() => {})
  ttsText.value = ''
}
</script>

<style scoped>
h3, h4 { margin-bottom: 10px; }

.no-device {
  padding: 40px 20px; color: #B09080; font-size: 14px; text-align: center;
}
.no-device.warn { color: #EF6C00; }

.audio-item {
  display: flex; align-items: center; gap: 10px;
  padding: 10px 12px; border: 1px solid rgba(255,160,120,0.15);
  border-radius: 10px; margin-bottom: 6px;
  cursor: pointer; transition: all 0.15s;
}
.audio-item:hover { background: #FFF5F0; border-color: rgba(255,140,80,0.3); }
.audio-icon { font-size: 18px; }
.audio-label { flex: 1; font-size: 13px; font-weight: 600; color: #5A3020; }
.audio-dur { font-size: 11px; color: #B09080; }

.tts-row { display: flex; gap: 8px; }
.tts-row input {
  flex: 1; height: 38px; border-radius: 10px;
  border: 1px solid rgba(255,160,120,0.3);
  padding: 0 12px; font-size: 13px; font-family: inherit;
  color: #3A2010; background: #FFFAF7; outline: none;
}
.tts-row input:focus { border-color: #FF8A65; }
.tts-row button {
  height: 38px; padding: 0 18px; border-radius: 10px;
  border: none; background: linear-gradient(135deg, #FF9A76, #FF6040);
  color: white; font-size: 13px; font-weight: 700; font-family: inherit;
  cursor: pointer; box-shadow: 0 3px 10px rgba(255,96,64,0.25);
}

hr { border: none; border-top: 1px solid rgba(255,160,120,0.15); margin: 16px 0; }
</style>
