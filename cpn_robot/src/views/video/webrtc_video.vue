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
  .webrtc-video-container {
    font-family: 'Helvetica Neue', Arial, sans-serif;
    background: #f0f2f5;
    padding: 20px 10px; 
    min-height: 100vh;
    box-sizing: border-box;
  }
  
  .page-title {
    text-align: center;
    color: #333;
    margin-bottom: 20px;
    font-weight: 700;
    font-size: 28px;
  }

  .main-layout {
    max-width: 1600px;
    width: 96%; 
    margin: 0 auto;
    display: flex;
    flex-direction: column;
    gap: 20px;
  }
  
  .video-container {
    display: flex;
    gap: 20px;
    width: 100%;
    justify-content: center;
  }
  
  .video-box {
    flex: 1; 
    position: relative;
    aspect-ratio: 16 / 9; 
    background: #000;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 4px 20px rgba(0,0,0,0.15);
    transition: transform 0.3s ease;
  }
  
  .video-box:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(0,0,0,0.2);
  }
  
  video {
    width: 100%;
    height: 100%;
    object-fit: cover; 
  }
  
  .label {
    position: absolute;
    bottom: 15px;
    left: 15px;
    color: white;
    background: rgba(0, 0, 0, 0.5);
    backdrop-filter: blur(4px);
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 14px;
    font-weight: 500;
    pointer-events: none;
  }
  
  .control-panel {
    width: 100%;
    background: #ffffff;
    border-radius: 12px;
    padding: 20px 30px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    box-sizing: border-box;
  }
  
  .control-header {
    border-bottom: 1px solid #eee;
    padding-bottom: 15px;
    margin-bottom: 20px;
  }
  
  .control-header h3 {
    margin: 0;
    color: #444;
    font-size: 18px;
  }
  
  .control-content {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 20px;
    flex-wrap: wrap; 
  }

  .control-item {
    display: flex;
    align-items: center;
  }

  .room-selector {
    gap: 10px;
  }
  
  .room-selector label {
    font-weight: 600;
    color: #555;
  }
  
  .room-input {
    padding: 10px 15px;
    border: 1px solid #ddd;
    border-radius: 6px;
    font-size: 16px;
    width: 120px;
    text-align: center;
    outline: none;
    transition: border-color 0.2s;
  }

  .room-input:focus {
    border-color: #007bff;
  }
  
  .button-group {
    display: flex; /* 显式声明 flex */
    gap: 20px;    /* 增加按钮之间的间距 */
  }
  
  /* --- 关键修改：按钮样式 --- */
  .action-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    
    /* 1. 增大尺寸 */
    padding: 14px 32px; 
    font-size: 16px;
    font-weight: 600;
    
    /* 2. 强制横向不换行 */
    white-space: nowrap; 
    flex-shrink: 0;      /* 防止被挤压 */
    
    /* 3. 其他样式 */
    cursor: pointer;
    border: none;
    border-radius: 8px; /* 稍微圆润一点 */
    transition: all 0.2s ease;
    min-width: 140px;   /* 设置最小宽度，保证看起来够大气 */
  }
  
  .action-btn.primary {
    background: #007bff;
    color: white;
  }
  
  .action-btn.success {
    background: #28a745;
    color: white;
  }
  
  .action-btn:hover:not(:disabled) {
    opacity: 0.9;
    transform: translateY(-2px); /* 悬浮效果更明显 */
    box-shadow: 0 4px 12px rgba(0,0,0,0.15); /* 增加投影 */
  }
  
  .action-btn:disabled {
    background: #e9ecef;
    color: #adb5bd;
    cursor: not-allowed;
    transform: none;
    box-shadow: none;
  }

  .status-wrapper {
    flex: 1; 
    justify-content: flex-end; 
  }
  
  .status-text {
    padding: 10px 20px; /* 状态栏也稍微大一点 */
    background: #f8f9fa;
    border: 1px solid #e9ecef;
    border-radius: 6px;
    color: #666;
    font-size: 14px;
    white-space: nowrap;
  }
  
  .log-container {
    width: 100%;
    background: #2d2d2d;
    border-radius: 12px;
    padding: 20px;
    box-sizing: border-box;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  }
  
  .log-container h4 {
    margin-top: 0;
    margin-bottom: 10px;
    color: #ccc;
    font-weight: 500;
    font-size: 14px;
    border-bottom: 1px solid #444;
    padding-bottom: 10px;
  }
  
  .log {
    width: 100%;
    height: 150px; 
    background: transparent;
    color: #0f0;
    padding: 5px;
    overflow-y: auto;
    font-family: 'Consolas', 'Monaco', monospace;
    font-size: 12px;
    line-height: 1.5;
    border: none;
  }
  
  .log::-webkit-scrollbar {
    width: 8px;
  }
  .log::-webkit-scrollbar-thumb {
    background: #555;
    border-radius: 4px;
  }

  @media (max-width: 900px) { 
    .video-container {
      flex-direction: column; 
    }

    .control-content {
      flex-direction: column; 
      align-items: stretch;
      gap: 15px;
    }

    .status-wrapper {
      justify-content: center;
    }
    
    .status-text {
      text-align: center;
      width: 100%;
    }

    .button-group {
        display: grid;
        grid-template-columns: 1fr 1fr;
    }
    
    .action-btn {
        width: 100%; /* 手机上按钮撑满宽度 */
    }
  }
</style>