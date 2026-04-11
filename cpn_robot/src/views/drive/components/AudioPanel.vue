<template>
  <div>
    <h3>音效控制</h3>

    <!-- 音效列表 -->
    <div>
      <h4>音效列表</h4>

      <div
        v-for="audio in audioList"
        :key="audio.name"
        class="audio-item"
        @click="play(audio)"
      >
        {{ audio.label }} | {{ audio.duration }}s
      </div>
    </div>

    <hr />

    <!-- TTS -->
    <div>
      <h4>文字转语音 (TTS)</h4>

      <input
        v-model="ttsText"
        placeholder="输入要说的话..."
      />

      <button @click="playTTS">
        朗读
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

/* ---------------- 数据 ---------------- */

// 👉 先写死（后面再从后端拿）
const audioList = ref([
  { name: 'hello', label: '打招呼', duration: 2 },
  { name: 'happy', label: '开心', duration: 3 },
  { name: 'sad', label: '悲伤', duration: 2 },
  { name: 'beep', label: '哔声', duration: 1 }
])

const ttsText = ref('')

/* ---------------- 方法 ---------------- */

function play(audio) {
  console.log('播放音效:', audio)

  // 👉 方式1：你原来的 JS
  if (window.playAudio) {
    window.playAudio(audio.name, audio.duration)
    return
  }

  // 👉 方式2：API
  fetch(`/api/audio?name=${audio.name}`)
}

function playTTS() {
  console.log('TTS:', ttsText.value)

  if (!ttsText.value) return

  // 👉 方式1：旧系统
  if (window.playTTS) {
    window.playTTS(ttsText.value)
    return
  }

  // 👉 方式2：API
  fetch('/api/tts', {
    method: 'POST',
    body: JSON.stringify({ text: ttsText.value })
  })
}
</script>

<style scoped>
.audio-item {
  padding: 8px;
  border: 1px solid #ccc;
  margin-bottom: 5px;
  cursor: pointer;
}

.audio-item:hover {
  background: #f5f5f5;
}
</style>