<template>
  <div class="webrtc-video-container">
    <h1 class="page-title">WebRTC 视频通话</h1>
    
    <div class="main-layout">
      
      <div class="video-container">
        <div class="video-box">
          <video id="localVideo" autoplay playsinline muted></video> 
          <div class="label">本地预览</div>
        </div>
        <div class="video-box">
          <video id="remoteVideo" autoplay playsinline></video>
          <div class="label">远端视频</div>
        </div>
      </div>

      <div class="control-panel">
        <div class="control-header">
          <h3>通话控制</h3>
        </div>
        <div class="control-content">
          <div class="control-item room-selector">
            <label>房间号:</label>
            <input type="text" id="roomId" value="0001" class="room-input">
          </div>
          
          <div class="control-item button-group">
            <button class="action-btn primary" id="btnJoin" @click="joinRoom">
              <i class="icon">🚪</i> 加入房间
            </button>
            <button class="action-btn success" id="btnCall" @click="startCall" :disabled="!isJoined">
              <i class="icon">🎥</i> 发起通话
            </button>
          </div>
          
          <div class="control-item status-wrapper">
            <div id="status" class="status-text">请先加入房间...</div>
          </div>
        </div>
      </div>

      <div class="log-container">
        <h4>通话日志</h4>
        <div class="log" id="logArea"></div>
      </div>

    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import { io } from 'socket.io-client';

export default {
  name: 'WebrtcVideo',
  setup() {
    // === 逻辑代码完全保持不变 ===
    const SERVER_URL = "http://zhangchenxideMacBook-Pro.local:8081";
    let socket = null;
    let localStream = null;
    let peerConnection = null;
    const isJoined = ref(false);
    
    const rtcConfig = {
      iceServers: [
        { urls: "stun:stun.l.google.com:19302" },
        { urls: "stun:stun1.l.google.com:19302" }
      ]
    };

    function log(msg) {
      const logArea = document.getElementById('logArea');
      if(logArea) {
        logArea.innerHTML += `<div>[${new Date().toLocaleTimeString()}] ${msg}</div>`;
        logArea.scrollTop = logArea.scrollHeight;
      }
      console.log(msg);
    }

    function joinRoom() {
      const roomId = document.getElementById('roomId').value;
      socket = io(SERVER_URL, { transports: ['websocket'] });

      socket.on('connect', () => {
        log(`✅ 已连接信令服务器 (ID: ${socket.id})`);
        socket.emit('join', { room: roomId });
      });

      socket.on('joined', (data) => {
        log(`WebRTC 就绪，已加入房间: ${data.room}`);
        document.getElementById('status').innerText = "状态: 在线，等待通话...";
        isJoined.value = true;
        startLocalCamera();
      });

      socket.on('message', async (data) => {
        if (data.type === 'offer') {
          await handleOffer(data);
        } else if (data.type === 'answer') {
          await handleAnswer(data);
        } else if (data.type === 'candidate') {
          await handleCandidate(data);
        }
      });
    }

    async function startLocalCamera() {
      try {
        localStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
        document.getElementById('localVideo').srcObject = localStream;
        log("📷 摄像头已打开");
      } catch (e) {
        log("❌ 无法打开摄像头: " + e.message);
        alert("请允许浏览器访问摄像头和麦克风！");
      }
    }

    function createPeerConnection() {
      log("正在创建 PeerConnection...");
      peerConnection = new RTCPeerConnection(rtcConfig);

      peerConnection.onicecandidate = (event) => {
        if (event.candidate) {
          const roomId = document.getElementById('roomId').value;
          socket.emit('message', {
            room: roomId,
            payload: { type: 'candidate', candidate: event.candidate }
          });
        }
      };

      peerConnection.ontrack = (event) => {
        log("🎬 收到远端视频流！");
        document.getElementById('remoteVideo').srcObject = event.streams[0];
      };

      localStream.getTracks().forEach(track => {
        peerConnection.addTrack(track, localStream);
      });
    }

    async function startCall() {
      const roomId = document.getElementById('roomId').value;
      createPeerConnection();

      const offer = await peerConnection.createOffer();
      await peerConnection.setLocalDescription(offer);

      log("📤 发送 Offer (呼叫请求)...");
      socket.emit('message', { room: roomId, payload: offer });
    }

    async function handleOffer(offer) {
      log("📥 收到 Offer (被呼叫)，准备接听...");
      createPeerConnection();

      await peerConnection.setRemoteDescription(new RTCSessionDescription(offer));
      
      const answer = await peerConnection.createAnswer();
      await peerConnection.setLocalDescription(answer);

      const roomId = document.getElementById('roomId').value;
      log("📤 发送 Answer (同意接听)...");
      socket.emit('message', { room: roomId, payload: answer });
    }

    async function handleAnswer(answer) {
      log("📥 收到 Answer (对方已接听)，连接建立中...");
      await peerConnection.setRemoteDescription(new RTCSessionDescription(answer));
    }

    async function handleCandidate(candidate) {
      if (peerConnection) {
        await peerConnection.addIceCandidate(new RTCIceCandidate(candidate.candidate));
      }
    }

    return {
      joinRoom,
      startCall,
      isJoined
    };
  }
};
</script>

<style scoped>
/* ===== 页面整体 ===== */
.webrtc-video-container {
  background: linear-gradient(135deg, #FFF8F3, #FFEFE6);
  padding: 20px;
  height: 100%;
  box-sizing: border-box;
}

/* 标题 */
.page-title {
  text-align: center;
  color: #E64A19;
  margin-bottom: 20px;
  font-weight: 700;
  font-size: 28px;
}

/* 主布局 */
.main-layout {
  width: 100%;
  height: calc(100% - 60px);
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* ===== 视频区域 ===== */
.video-container {
  display: flex;
  gap: 20px;
  width: 100%;
}

.video-box {
  flex: 1;
  position: relative;
  aspect-ratio: 16 / 9;
  background: #000;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 10px 30px rgba(0,0,0,0.2);
  transition: 0.3s;
}

.video-box:hover {
  transform: translateY(-4px);
  box-shadow: 0 20px 40px rgba(0,0,0,0.3);
}

video {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* 标签 */
.label {
  position: absolute;
  bottom: 12px;
  left: 12px;
  background: rgba(0,0,0,0.5);
  backdrop-filter: blur(6px);
  color: #fff;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 13px;
}

/* ===== 控制面板 ===== */
.control-panel {
  background: #FFFFFF;
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 8px 24px rgba(255, 138, 101, 0.08);
}

/* 标题 */
.control-header {
  border-bottom: 1px solid #FFE0D6;
  padding-bottom: 10px;
  margin-bottom: 15px;
}

.control-header h3 {
  margin: 0;
  color: #E64A19;
}

/* 内容布局 */
.control-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
}

/* 房间输入 */
.room-input {
  padding: 10px 14px;
  border: 1px solid #FFD6C8;
  border-radius: 10px;
  text-align: center;
  outline-color: #FF8A65;
}

/* 按钮组 */
.button-group {
  display: flex;
  gap: 14px;
}

/* 按钮统一 */
.action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 150px;
  height: 44px;
  padding: 0 20px;

  font-size: 15px;
  font-weight: 600;

  border-radius: 12px;
  cursor: pointer;
  border: none;

  transition: all 0.25s ease;
}

/* 👉 次按钮（加入房间） */
.action-btn.primary {
  background: #FFF3EE;
  color: #E64A19;
  border: 1px solid #FFCCBC;
}

/* 👉 主按钮（发起通话） */
.action-btn.success {
  background: linear-gradient(90deg, #FF8A65, #FF7043);
  color: #fff;
  box-shadow: 0 6px 16px rgba(255, 138, 101, 0.35);
}

/* hover效果 */
.action-btn.primary:hover {
  background: #FFE0D6;
}

.action-btn.success:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 24px rgba(255, 138, 101, 0.5);
}

/* 禁用状态 */
.action-btn:disabled {
  background: #eee !important;
  color: #aaa !important;
  box-shadow: none;
  cursor: not-allowed;
}

/* 状态 */
.status-text {
  padding: 8px 16px;
  background: #FFF3EE;
  border-radius: 10px;
  color: #E64A19;
}

/* ===== 日志区 ===== */
.log-container {
  background: #FFFFFF;
  border-radius: 16px;
  padding: 16px;
  box-shadow: 0 8px 24px rgba(255, 138, 101, 0.08);
}

/* 标题 */
.log-container h4 {
  margin-bottom: 10px;
  color: #E64A19;
}

/* 日志框 */
.log {
  height: 140px;
  background: #FFF7F3;
  border-radius: 10px;
  padding: 10px;
  overflow-y: auto;
  font-size: 12px;
  border: 1px solid #FFE0D6;
}

/* 滚动条 */
.log::-webkit-scrollbar {
  width: 6px;
}

.log::-webkit-scrollbar-thumb {
  background: #FFB199;
  border-radius: 3px;
}

/* ===== 响应式 ===== */
@media (max-width: 900px) {
  .video-container {
    flex-direction: column;
  }

  .control-content {
    flex-direction: column;
    gap: 15px;
    align-items: stretch;
  }

  .button-group {
    width: 100%;
    display: grid;
    grid-template-columns: 1fr 1fr;
  }
}
</style>