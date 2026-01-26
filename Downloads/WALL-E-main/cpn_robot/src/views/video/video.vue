<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
// 注意：如果未安装socket.io-client，先执行 npm install socket.io-client
import { io } from 'socket.io-client'

// 修复：服务器地址与原生HTML保持一致（8081）
const SERVER_URL = 'http://localhost:8081'
let socket = null
let localStream = null
let peerConnection = null

// RTC 配置（不变）
const rtcConfig = {
  iceServers: [
    { urls: 'stun:stun.l.google.com:19302' },
    { urls: 'stun:stun1.l.google.com:19302' }
  ]
}

// Vue 响应式数据
const roomId = ref('0001') // 与原生默认值保持一致
const isJoined = ref(false)
const statusText = ref('请先加入房间...')
const logContent = ref('')

// 修复1：定义的ref需要在template中绑定
const localVideo = ref(null)
const remoteVideo = ref(null)
const logArea = ref(null)

// 日志函数（修复：使用Vue内置的nextTick）
function log(msg) {
  const timeStr = new Date().toLocaleTimeString()
  logContent.value += `<div>[${timeStr}] ${msg}</div>`
  // 使用Vue内置的nextTick
  nextTick(() => {
    if (logArea.value) {
      logArea.value.scrollTop = logArea.value.scrollHeight
    }
  })
  console.log(`[${timeStr}]`, msg)
}

// 加入房间（逻辑不变，仅确保地址一致）
async function joinRoom() {
  if (!roomId.value) {
    alert('请输入房间号！')
    return
  }

  // 连接信令服务器
  socket = io(SERVER_URL, { transports: ['websocket'] })

  socket.on('connect', () => {
    log(`✅ 已连接信令服务器 (ID: ${socket.id})`)
    socket.emit('join', { room: roomId.value })
  })

  socket.on('joined', (data) => {
    log(`WebRTC 就绪，已加入房间: ${data.room}`)
    statusText.value = '状态: 在线，等待通话...'
    isJoined.value = true // 启用呼叫按钮
    startLocalCamera() // 自动打开摄像头
  })

  // 处理信令消息
  socket.on('message', async (data) => {
    // 修复：注意数据结构，原生中是data.payload，这里要对齐
    const payload = data.payload || data
    if (payload.type === 'offer') {
      await handleOffer(payload)
    } else if (payload.type === 'answer') {
      await handleAnswer(payload)
    } else if (payload.type === 'candidate') {
      await handleCandidate(payload)
    }
  })

  socket.on('disconnect', () => {
    log('❌ 与信令服务器断开连接')
    statusText.value = '已断开连接'
    isJoined.value = false
  })

  socket.on('error', (err) => {
    log(`❌ 连接错误: ${err.message}`)
  })
}

// 打开本地摄像头（修复：检查ref是否存在）
async function startLocalCamera() {
  try {
    localStream = await navigator.mediaDevices.getUserMedia({
      video: true,
      audio: true
    })
    // 确保ref绑定成功后再挂载流
    if (localVideo.value) {
      localVideo.value.srcObject = localStream
      log('📷 摄像头已打开')
    } else {
      log('❌ 本地视频元素未找到')
    }
  } catch (e) {
    log(`❌ 无法打开摄像头: ${e.message}`)
    alert('请允许浏览器访问摄像头和麦克风！')
  }
}

// 创建 PeerConnection（逻辑不变）
function createPeerConnection() {
  log('正在创建 PeerConnection...')
  peerConnection = new RTCPeerConnection(rtcConfig)

  // 处理ICE候选
  peerConnection.onicecandidate = (event) => {
    if (event.candidate) {
      socket.emit('message', {
        room: roomId.value,
        payload: { type: 'candidate', candidate: event.candidate }
      })
    }
  }

  // 接收远端流
  peerConnection.ontrack = (event) => {
    log('🎬 收到远端视频流！')
    if (remoteVideo.value) {
      remoteVideo.value.srcObject = event.streams[0]
    }
  }

  // 添加本地流
  if (localStream) {
    localStream.getTracks().forEach((track) => {
      peerConnection.addTrack(track, localStream)
    })
  }
}

// 发起呼叫
async function startCall() {
  if (!isJoined.value || !localStream) {
    alert('请先加入房间并打开摄像头！')
    return
  }
  createPeerConnection()

  const offer = await peerConnection.createOffer()
  await peerConnection.setLocalDescription(offer)

  log('📤 发送 Offer (呼叫请求)...')
  socket.emit('message', { room: roomId.value, payload: offer })
}

// 处理Offer
async function handleOffer(offer) {
  log('📥 收到 Offer (被呼叫)，准备接听...')
  createPeerConnection()

  await peerConnection.setRemoteDescription(new RTCSessionDescription(offer))

  const answer = await peerConnection.createAnswer()
  await peerConnection.setLocalDescription(answer)

  log('📤 发送 Answer (同意接听)...')
  socket.emit('message', { room: roomId.value, payload: answer })
}

// 处理Answer
async function handleAnswer(answer) {
  log('📥 收到 Answer (对方已接听)，连接建立中...')
  await peerConnection.setRemoteDescription(new RTCSessionDescription(answer))
}

// 处理ICE Candidate
async function handleCandidate(candidate) {
  if (peerConnection && candidate.candidate) {
    await peerConnection.addIceCandidate(new RTCIceCandidate(candidate.candidate))
  }
}

// 组件卸载清理
onUnmounted(() => {
  // 关闭本地流
  if (localStream) {
    localStream.getTracks().forEach((track) => track.stop())
  }
  // 关闭PeerConnection
  if (peerConnection) {
    peerConnection.close()
  }
  // 断开socket
  if (socket) {
    socket.disconnect()
  }
  log('🔌 已清理所有资源')
})
</script>

<template>
  <h1>WebRTC 视频通话调试台</h1>

  <div class="container">
    <div class="video-box">
      <!-- 修复2：绑定ref属性到video元素 -->
      <video ref="localVideo" autoplay playsinline muted></video>
      <div class="label">本地预览 (我)</div>
    </div>
    <div class="video-box">
      <!-- 修复2：绑定ref属性到video元素 -->
      <video ref="remoteVideo" autoplay playsinline></video>
      <div class="label">远端视频 (对方)</div>
    </div>
  </div>

  <div class="controls">
    <h3>操作面板</h3>
    <div>
      <!-- 修复3：绑定roomId响应式数据 -->
      <label>房间号: 
        <input 
          type="text" 
          v-model="roomId" 
          style="padding: 5px; width: 60px; text-align: center;"
        >
      </label>
    </div>
    <br>
    <!-- 修复4：绑定按钮禁用状态 -->
    <button class="aa" @click="joinRoom" :disabled="isJoined">1. 加入房间</button>
    <button class="aa" @click="startCall" :disabled="!isJoined">2. 发起视频通话</button>
    <!-- 修复5：绑定状态文本 -->
    <div id="status">{{ statusText }}</div>
  </div>

  <!-- 修复6：绑定日志ref和日志内容 -->
  <div class="log" ref="logArea" v-html="logContent"></div>
</template>

<style scoped>
/* 样式保持不变，仅添加scoped避免样式污染 */
#roomId {
  width: 200px;
  height: 40px;
}
h1 {
  color: rgb(0, 0, 0);
}
body {
  font-family: sans-serif;
  background: #f0f2f5;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.container {
  width: 2245px;
  height: 900px;
  display: flex;
  gap: 20px;
  margin-top: 20px;
}
.video-box {
  position: relative;
  width: 800px;
  height: 600px;
  background: #000;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}
video {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.label {
  position: absolute;
  bottom: 10px;
  left: 10px;
  color: white;
  background: rgba(0, 0, 0, 0.5);
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 20px;
}
.controls {
  margin-top: 20px;
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  text-align: center;
  color: black;
}
.aa {
  width: 200px;
  height: 50px;
  padding: 10px 20px;
  font-size: 20px;
  font-weight: 600;
  cursor: pointer;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  margin: 0 10px;
}
button:disabled {
  background: #ccc;
  cursor: not-allowed;
}
#status {
  margin-top: 10px;
  color: #666;
  font-size: 14px;
}
.log {
  width: 800px;
  height: 150px;
  background: #333;
  color: #0f0;
  margin-top: 20px;
  padding: 10px;
  overflow-y: scroll;
  font-family: monospace;
  font-size: 12px;
  border-radius: 4px;
}
</style>