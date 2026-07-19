<template>
  <div class="camera-panel">
    <h3>实时画面</h3>

    <div v-if="!machine" class="placeholder">请先在顶部选择一个机器人设备</div>
    <div v-else-if="!machine.id" class="placeholder">设备信息不完整</div>
    <div v-else-if="loading" class="placeholder">正在连接摄像头...</div>
    <div v-else-if="error" class="placeholder err">{{ error }}</div>
    <img
      v-show="streamUrl && !loading && !error"
      :src="streamUrl"
      class="video-stream"
      @load="onLoad"
      @error="onError"
    />
  </div>
</template>

<script setup>
import { onBeforeUnmount, ref, watch } from 'vue'
import { getApiBaseUrl } from '@/utils/systemConfig'
import { fetchCameraFrame } from '../cameraFrame.mjs'

const props = defineProps({
  machine: { type: Object, default: null }
})

const streamUrl = ref('')
const loading = ref(false)
const error = ref('')
let refreshTimer = null
let refreshing = false

function stopRefreshing() {
  if (refreshTimer) {
    clearInterval(refreshTimer)
    refreshTimer = null
  }
}

function refreshFrame(id) {
  const base = getApiBaseUrl().replace(/\/$/, '')
  if (refreshing) return
  refreshing = true
  fetchCameraFrame({ baseUrl: base, machineId: id })
    .then(blob => {
      if (!blob) {
        loading.value = false
        error.value = '等待机器人摄像头推流...'
        return
      }
      const nextUrl = URL.createObjectURL(blob)
      const previousUrl = streamUrl.value
      streamUrl.value = nextUrl
      if (previousUrl) URL.revokeObjectURL(previousUrl)
      loading.value = false
      error.value = ''
    })
    .catch(() => {
      loading.value = false
      error.value = '摄像头请求失败，请重新登录后重试'
    })
    .finally(() => { refreshing = false })
}

watch(() => props.machine?.id, (id) => {
  stopRefreshing()
  error.value = ''
  if (!id) { streamUrl.value = ''; return }
  loading.value = true
  refreshFrame(id)
  refreshTimer = setInterval(() => refreshFrame(id), 500)
}, { immediate: true })

onBeforeUnmount(() => {
  stopRefreshing()
  if (streamUrl.value) URL.revokeObjectURL(streamUrl.value)
})

function onLoad() { loading.value = false; error.value = '' }
function onError() {
  loading.value = false
  error.value = '等待机器人摄像头推流...'
}
</script>

<style scoped>
.camera-panel { text-align: center; }
h3 { margin-bottom: 14px; text-align: left; }

.placeholder { padding: 60px 20px; color: #B09080; font-size: 14px; }
.placeholder.err  { color: #D32F2F; }

.video-stream {
  width: 100%; max-width: 640px; border-radius: 12px;
  border: 2px solid rgba(255,160,120,0.2);
  box-shadow: 0 4px 16px rgba(200,100,60,0.1);
}
</style>
