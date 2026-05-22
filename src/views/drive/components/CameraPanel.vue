<template>
  <div class="camera-panel">
    <h3>实时画面</h3>

    <div v-if="!machine" class="placeholder">请先在顶部选择一个机器人设备</div>
    <div v-else-if="!machine.id" class="placeholder">设备信息不完整</div>
    <div v-else-if="loading && frameCount === 0" class="placeholder">正在连接摄像头...</div>
    <div v-else-if="error" class="placeholder err">{{ error }}</div>
    <img
      v-show="streamUrl && !error"
      :src="streamUrl"
      class="video-stream"
      @load="onLoad"
      @error="onError"
    />
  </div>
</template>

<script setup>
import { ref, watch, onBeforeUnmount } from 'vue'

const props = defineProps({
  machine: { type: Object, default: null }
})

const streamUrl = ref('')
const loading = ref(false)
const error = ref('')
const frameCount = ref(0)
let pollTimer = null

watch(() => props.machine?.id, (id) => {
  stopPoll()
  error.value = ''
  frameCount.value = 0
  if (!id) { streamUrl.value = ''; return }
  loading.value = true
  streamUrl.value = ''
  // 树莓派通过 Socket.IO 推送帧到 Java 后端 (2fps, base64 JPEG)
  // 前端每 500ms 拉一次最新帧，无需 MJPEG 长连接
  fetchFrame()
  pollTimer = setInterval(fetchFrame, 500)
}, { immediate: true })

function fetchFrame() {
  const id = props.machine?.id
  if (!id) return
  // 加时间戳防浏览器缓存
  streamUrl.value = `/api/robot/camera-frame/${id}?t=${Date.now()}`
}

function stopPoll() {
  if (pollTimer) { clearInterval(pollTimer); pollTimer = null }
}

function onLoad() {
  if (loading.value) loading.value = false
  error.value = ''
  frameCount.value++
}

function onError() {
  // 连续 6 次失败 (~3秒) 才显示错误，容忍偶尔丢帧
  if (frameCount.value === 0 && !error.value) {
    loading.value = false
    error.value = '视频流连接失败，请确认机器人已开机且后端可达'
  }
}

onBeforeUnmount(() => stopPoll())
</script>

<style scoped>
.camera-panel { text-align: center; }
h3 { margin-bottom: 14px; text-align: left; }

.placeholder { padding: 60px 20px; color: #B09080; font-size: 14px; }
.placeholder.err  { color: #D32F2F; }
.placeholder.warn { color: #F57C00; }

.video-stream {
  width: 100%; max-width: 640px; border-radius: 12px;
  border: 2px solid rgba(255,160,120,0.2);
  box-shadow: 0 4px 16px rgba(200,100,60,0.1);
}
</style>
