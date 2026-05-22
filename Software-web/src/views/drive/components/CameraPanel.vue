<template>
  <div class="camera-panel">
    <h3>实时画面</h3>

    <div v-if="!machine" class="placeholder">请先在顶部选择一个机器人设备</div>
    <div v-else-if="!machine.id" class="placeholder">设备信息不完整</div>
    <div v-else-if="loading" class="placeholder">正在连接摄像头...</div>
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
import { ref, watch } from 'vue'

const props = defineProps({
  machine: { type: Object, default: null }
})

const streamUrl = ref('')
const loading = ref(false)
const error = ref('')

watch(() => props.machine?.id, (id) => {
  error.value = ''
  if (!id) { streamUrl.value = ''; return }
  loading.value = true
  // 通过 Java 后端代理，浏览器不需要和机器人在同一局域网
  streamUrl.value = `/api/robot/video-feed/${id}`
}, { immediate: true })

function onLoad() { loading.value = false; error.value = '' }
function onError() {
  loading.value = false
  error.value = '视频流连接失败，请确认机器人已开机且后端可达'
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
