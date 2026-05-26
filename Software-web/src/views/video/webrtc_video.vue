<template>
  <div class="video-root">

    <!-- 顶栏 -->
    <div class="page-header">
      <div class="page-header-left">
        <div class="page-title-icon">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <path d="M1 4a1 1 0 011-1h8a1 1 0 011 1v8a1 1 0 01-1 1H2a1 1 0 01-1-1V4z" stroke="white" stroke-width="1.4"/>
            <path d="M11 6l4-2v8l-4-2V6z" stroke="white" stroke-width="1.4" stroke-linejoin="round"/>
          </svg>
        </div>
        <div>
          <div class="page-title">星闪安全监护</div>
          <div class="page-sub">WebRTC 实时视频连接</div>
        </div>
      </div>
      <div class="status-capsule" :class="checkingFace ? 'state-checking' : statusClass">
        <span class="status-dot-cap"></span>
        {{ checkingFace ? '活体检测中…' : statusText }}
      </div>
    </div>

    <!-- 主内容 -->
    <div class="main-layout">

      <!-- 左侧：视频区 -->
      <div class="video-section">
        <div class="video-grid">
          <div class="video-card">
            <video id="localVideo" autoplay playsinline muted></video>
            <!-- 活体检测倒计时浮层 -->
            <div class="liveness-overlay" v-if="countdownPhase !== 'idle'">
              <div class="liveness-ring">
                <div class="liveness-text" v-if="countdownPhase === 'countdown'">
                  <div class="liveness-title">即将进行安全验证</div>
                  <div class="liveness-sub">请直视屏幕...</div>
                  <div class="liveness-count">{{ countdownNum }}</div>
                </div>
                <div class="liveness-text" v-else>
                  <div class="liveness-detect-icon">
                    <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
                      <circle cx="16" cy="16" r="14" stroke="rgba(255,255,255,0.6)" stroke-width="2" stroke-dasharray="66" stroke-dashoffset="0">
                        <animateTransform attributeName="transform" type="rotate" from="0 16 16" to="360 16 16" dur="1s" repeatCount="indefinite"/>
                      </circle>
                    </svg>
                  </div>
                  <div class="liveness-title">检测中...</div>
                </div>
              </div>
            </div>
            <div class="video-overlay">
              <div class="video-label">
                <svg width="8" height="8" viewBox="0 0 8 8" fill="none" style="flex-shrink:0">
                  <circle cx="4" cy="4" r="3.5" fill="rgba(255,255,255,0.9)"/>
                </svg>
                本地预览
              </div>
              <div class="video-badge" v-if="isJoined">
                <span class="live-dot-sm"></span> LIVE
              </div>
            </div>
            <div class="video-placeholder" id="localPlaceholder">
              <svg width="40" height="40" viewBox="0 0 40 40" fill="none">
                <circle cx="20" cy="16" r="7" stroke="rgba(255,160,120,0.5)" stroke-width="2"/>
                <path d="M6 34c0-7.7 6.3-14 14-14s14 6.3 14 14" stroke="rgba(255,160,120,0.5)" stroke-width="2" stroke-linecap="round"/>
              </svg>
              <span>摄像头未开启</span>
            </div>
          </div>

          <div class="video-card">
            <video id="remoteVideo" autoplay playsinline></video>
            <div class="video-overlay">
              <div class="video-label">
                <svg width="8" height="8" viewBox="0 0 8 8" fill="none" style="flex-shrink:0">
                  <circle cx="4" cy="4" r="3.5" fill="rgba(255,255,255,0.9)"/>
                </svg>
                远端视频
              </div>
            </div>
            <div class="video-placeholder" id="remotePlaceholder">
              <svg width="40" height="40" viewBox="0 0 40 40" fill="none">
                <rect x="4" y="10" width="22" height="16" rx="3" stroke="rgba(255,160,120,0.5)" stroke-width="2"/>
                <path d="M26 17l10-5v16l-10-5V17z" stroke="rgba(255,160,120,0.5)" stroke-width="2" stroke-linejoin="round"/>
              </svg>
              <span>等待远端接入</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧面板 -->
      <div class="side-panel">

        <!-- 控制卡片 -->
        <div class="ctrl-card">
          <div class="card-header">
            <div class="card-header-icon">
              <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                <circle cx="7" cy="7" r="5.5" stroke="white" stroke-width="1.4"/>
                <path d="M7 4v3l2 1.5" stroke="white" stroke-width="1.3" stroke-linecap="round"/>
              </svg>
            </div>
            通话控制
          </div>

          <div class="ctrl-body">
            <div class="form-row">
              <label class="form-label">房间号</label>
              <div class="input-wrap">
                <svg width="13" height="13" viewBox="0 0 13 13" fill="none" class="input-icon">
                  <rect x="1" y="3" width="11" height="8.5" rx="1.5" stroke="#C4A898" stroke-width="1.2"/>
                  <path d="M3.5 3V2.5a3 3 0 016 0V3" stroke="#C4A898" stroke-width="1.2"/>
                </svg>
                <input type="text" id="roomId" value="0001" class="room-input" placeholder="输入房间号" />
              </div>
            </div>

            <div class="btn-group">
              <button class="ctrl-btn ctrl-join" @click="joinRoom">
                <svg width="13" height="13" viewBox="0 0 13 13" fill="none">
                  <path d="M8 6.5H1m0 0l2.5-2.5M1 6.5L3.5 9" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/>
                  <path d="M5 3.5V2.5a1 1 0 011-1h5a1 1 0 011 1v9a1 1 0 01-1 1H6a1 1 0 01-1-1v-1" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
                </svg>
                加入房间
              </button>
              <button class="ctrl-btn ctrl-call" @click="startCall" :disabled="!isJoined || checkingFace">
                <svg width="13" height="13" viewBox="0 0 13 13" fill="none">
                  <rect x="1" y="3" width="8" height="7" rx="1.2" stroke="white" stroke-width="1.3"/>
                  <path d="M9 5.5l4-2v6l-4-2V5.5z" stroke="white" stroke-width="1.3" stroke-linejoin="round"/>
                </svg>
                {{ checkingFace ? '人脸检测中…' : '请求监视' }}
              </button>
              <button class="ctrl-btn ctrl-call" @click="hangUpCall" :disabled="!isJoined">
                <svg width="13" height="13" viewBox="0 0 13 13" fill="none">
                  <rect x="1" y="3" width="8" height="7" rx="1.2" stroke="white" stroke-width="1.3"/>
                  <path d="M9 5.5l4-2v6l-4-2V5.5z" stroke="white" stroke-width="1.3" stroke-linejoin="round"/>
                </svg>
                结束通话
              </button>
            </div>

            <div class="conn-info">
              <div class="conn-row">
                <span class="conn-label">服务器</span>
                <span class="conn-val">{{ socketServerUrl }}</span>
              </div>
              <div class="conn-row">
                <span class="conn-label">协议</span>
                <span class="conn-val">WebRTC / WS</span>
              </div>
              <div class="conn-row">
                <span class="conn-label">当前状态</span>
                <span class="conn-status" :class="statusClass">{{ statusText }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 日志卡片 -->
        <div class="log-card">
          <div class="card-header">
            <div class="card-header-icon">
              <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                <path d="M2 3h10M2 7h7M2 11h5" stroke="white" stroke-width="1.4" stroke-linecap="round"/>
              </svg>
            </div>
            通话日志
            <button class="log-clear-btn" @click="clearLog">清空</button>
          </div>
          <div class="log-body" id="logArea"></div>
        </div>

      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue';
import { io } from 'socket.io-client';
import { toast } from '../../utils/toast';
import { getConfigValue, getSocketServerUrl } from '../../utils/systemConfig';

export default {
  name: 'WebrtcVideo',
  setup() {
    const socketServerUrl = ref(getSocketServerUrl());
    const livenessApiUrl = ref(getConfigValue('liveness.api-url', ''));
    let socket = null;
    let localStream = null;
    let peerConnection = null;
    const isJoined = ref(false);
    const connState = ref('idle');

    const statusText = computed(() => ({
      idle: '未连接', joined: '已入房，等待通话',
      calling: '连接中…', connected: '视频通话中'
    }[connState.value]));

    const statusClass = computed(() => ({
      idle: 'state-idle', joined: 'state-joined',
      calling: 'state-calling', connected: 'state-connected'
    }[connState.value]));

    const rtcConfig = {
      iceServers: [
        { urls: "stun:stun.l.google.com:19302" },
        { urls: "stun:stun1.l.google.com:19302" }
      ]
    };

    function hangUpCall() {
    console.log("准备挂断通话...");
    
      if (localStream) {
          localStream.getTracks().forEach(track => track.stop());
      }
    
      // 2. 关闭网页端的 WebRTC 连接
      if (peerConnection) {
          peerConnection.close();
          peerConnection = null;
      }
    
      // 3. 【最关键的一步】：通过 Socket.IO 告诉树莓派“我挂断了”
      // 注意：这里的 room_id 要和树莓派上的 ROOM_ID (默认是 "0001") 保持一致
      socket.emit('message', {
          room: '0001', 
          payload: { type: 'bye' } 
      });

      if (socket) {
        socket.disconnect();
        socket = null;
      }
      // 4. 恢复占位符
      setPlaceholder('localPlaceholder', false);
      setPlaceholder('remotePlaceholder', false);

      // 5. 重置状态（关键！）
      isJoined.value = false;
      connState.value = 'idle';
      log("🔴 通话已结束，连接已断开");
    }

    function log(msg) {
      const logArea = document.getElementById('logArea');
      if (logArea) {
        const line = document.createElement('div');
        line.className = 'log-line';
        line.innerHTML = `<span class="log-time">${new Date().toLocaleTimeString()}</span><span>${msg}</span>`;
        logArea.appendChild(line);
        logArea.scrollTop = logArea.scrollHeight;
      }
    }

    function clearLog() {
      const el = document.getElementById('logArea');
      if (el) el.innerHTML = '';
    }

    function setPlaceholder(id, hide) {
      const el = document.getElementById(id);
      if (el) el.style.display = hide ? 'none' : 'flex';
    }

    function joinRoom() {
      const roomId = '0001';
      if (!roomId) return toast.warning("请输入房间号");

      log(`正在申请加入房间: ${roomId}`);

      const socketUrl = socketServerUrl.value;
      log(`正在通过安全通道连接: ${socketUrl}`);

      // 初始化 Socket.IO
      socket = io(socketUrl, {
        transports: ['websocket'],
        path: '/socket.io/',
        secure: false,
        forceNew: true,
        reconnection: true,
        rejectUnauthorized: false
      });

      // 连接成功
      socket.on('connect', () => {
        log(`✅ 已连接信令服务器 (ID: ${socket.id})`);
        console.log("准备发送 join 事件，房间号:", roomId);
        socket.emit('join', { "room": String(roomId) });
      });

      // 连接错误排查
      socket.on('connect_error', (err) => {
        log(`❌ 连接失败: ${err.message}`);
        console.error("连接详情:", err);
      });

      // 收到加入成功
      socket.on('joined', (data) => {
        log(`✅ 已成功加入房间: ${data.room}`);
        connState.value = 'joined';
        isJoined.value = true;
        startLocalCamera();
      });

      // 信令处理
      socket.on('message', async (data) => {
        console.log("收到信令:", data);
        if (data.type === 'offer') await handleOffer(data);
        else if (data.type === 'answer') await handleAnswer(data);
        else if (data.type === 'candidate') await handleCandidate(data);
        else if (data.type === 'bye') {
           log("对方已挂断");
           hangUpCall();
        }
      });
    }

    async function startLocalCamera() {
      try {
        localStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
        document.getElementById('localVideo').srcObject = localStream;
        setPlaceholder('localPlaceholder', true);
        log("📷 摄像头已开启");
      } catch (e) {
        log("❌ 无法打开摄像头: " + e.message);
        toast.warning("请允许浏览器访问摄像头和麦克风！");
      }
    }

    function createPeerConnection() {
      connState.value = 'calling';
      log("🔗 正在创建 PeerConnection…");
      peerConnection = new RTCPeerConnection(rtcConfig);
      peerConnection.onicecandidate = (e) => {
        if (e.candidate) {
          socket.emit('message', { room: document.getElementById('roomId').value, payload: { type: 'candidate', candidate: e.candidate } });
        }
      };
      peerConnection.ontrack = (e) => {
        log("🎬 收到远端视频流！");
        document.getElementById('remoteVideo').srcObject = e.streams[0];
        setPlaceholder('remotePlaceholder', true);
        connState.value = 'connected';
      };
      localStream.getTracks().forEach(track => peerConnection.addTrack(track, localStream));
    }

    const checkingFace = ref(false);
    const countdownPhase = ref('idle');   // 'idle' | 'countdown' | 'detecting'
    const countdownNum = ref(3);

    // Capture current video frame as a Blob
    function captureFrame(videoEl) {
      return new Promise((resolve, reject) => {
        const canvas = document.createElement('canvas');
        canvas.width = videoEl.videoWidth || 640;
        canvas.height = videoEl.videoHeight || 480;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(videoEl, 0, 0, canvas.width, canvas.height);
        canvas.toBlob(blob => {
          if (blob) resolve(blob);
          else reject(new Error('Canvas toBlob failed'));
        }, 'image/jpeg', 0.85);
      });
    }

    async function checkFace() {
      const localVideo = document.getElementById('localVideo');
      if (!localVideo || !localVideo.srcObject) {
        log('⚠ 摄像头未就绪，无法检测人脸');
        return false;
      }

      try {
        const blob = await captureFrame(localVideo);
        const formData = new FormData();
        formData.append('image', blob, 'frame.jpg');

        if (!livenessApiUrl.value) {
          log('⚠ 未配置活体检测服务，已跳过检测');
          return null;
        }

        const resp = await fetch(`${livenessApiUrl.value.replace(/\/$/, '')}/face/liveness`, {
          method: 'POST',
          body: formData,
        });

        if (!resp.ok) {
          const err = await resp.json();
          log(`⚠ 人脸检测服务异常: ${err.error || resp.status}`);
          return null;  // null = service unavailable, allow to proceed
        }

        const result = await resp.json();
        if (result.status === 'no_model') {
          log(`⚠ 活体检测模型未就绪: ${result.detail}`);
          return null;
        }
        log(`[人脸检测] 置信度: ${result.confidence}, 阈值: ${result.threshold}, 结果: ${result.is_real ? '真人' : '伪人脸'}`);
        return result.is_real;
      } catch (e) {
        log(`⚠ 人脸检测连接失败: ${e.message}`);
        return null;
      }
    }

    async function startCall() {
      // ── 倒计时 3 → 2 → 1 ──────────────────
      countdownPhase.value = 'countdown';
      for (let i = 3; i >= 1; i--) {
        countdownNum.value = i;
        await new Promise(r => setTimeout(r, 1000));
      }

      // ── 活体检测 ──────────────────────────
      countdownPhase.value = 'detecting';
      checkingFace.value = true;
      log('正在进行人脸活体检测...');
      const isReal = await checkFace();
      checkingFace.value = false;
      countdownPhase.value = 'idle';

      if (isReal === false) {
        log('⚠ 检测到伪人脸，为确保安全，已拒绝通话');
        toast.error('检测到伪人脸（照片/屏幕翻拍），或未直视屏幕。请再试一次或使用真人进行通话');
        return;
      }
      if (isReal === true) {
        log('✅ 人脸活体检测通过，正在建立通话');
      }

      createPeerConnection();
      const offer = await peerConnection.createOffer();
      await peerConnection.setLocalDescription(offer);
      log('📤 发送 Offer…');
      socket.emit('message', { room: document.getElementById('roomId').value, payload: offer });
    }

    async function handleOffer(offer) {
      log("📥 收到 Offer，准备接听…");
      createPeerConnection();
      await peerConnection.setRemoteDescription(new RTCSessionDescription(offer));
      const answer = await peerConnection.createAnswer();
      await peerConnection.setLocalDescription(answer);
      log("📤 发送 Answer…");
      socket.emit('message', { room: document.getElementById('roomId').value, payload: answer });
    }

    async function handleAnswer(answer) {
      log("📥 对方已接听，连接建立中…");
      await peerConnection.setRemoteDescription(new RTCSessionDescription(answer));
    }

    async function handleCandidate(c) {
      if (peerConnection) await peerConnection.addIceCandidate(new RTCIceCandidate(c.candidate));
    }

    return { joinRoom, startCall, isJoined, statusText, statusClass, clearLog, hangUpCall, checkingFace, countdownPhase, countdownNum, socketServerUrl };
  }
};
</script>

<style scoped>
.video-root {
  width: 100%; height: 100%;
  padding: 20px 24px; box-sizing: border-box;
  display: flex; flex-direction: column; gap: 16px;
  overflow: hidden;
  font-family: "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
}

/* 顶栏 */
.page-header {
  display: flex; align-items: center; justify-content: space-between; flex-shrink: 0;
}
.page-header-left { display: flex; align-items: center; gap: 12px; }
.page-title-icon {
  width: 40px; height: 40px; border-radius: 12px;
  background: linear-gradient(135deg, #FF9A76, #FF6040);
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 4px 12px rgba(255,96,64,0.28); flex-shrink: 0;
}
.page-title { font-size: 18px; font-weight: 700; color: #3A2010; letter-spacing: 0.01em; }
.page-sub { font-size: 12px; color: #B09080; margin-top: 2px; }

.status-capsule {
  display: flex; align-items: center; gap: 6px;
  border-radius: 100px; padding: 6px 14px;
  font-size: 12px; font-weight: 600;
  border: 1px solid transparent; transition: all 0.3s ease;
}
.status-dot-cap { width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0; }
.state-idle    { background:#F5F0EE; color:#A09080; border-color:rgba(180,150,130,0.2); }
.state-idle .status-dot-cap    { background:#C4B0A8; }
.state-joined  { background:#FFF5E8; color:#B06020; border-color:rgba(200,140,50,0.25); }
.state-joined .status-dot-cap  { background:#E0A040; animation:blink 1.5s ease infinite; }
.state-calling { background:#FFF0E8; color:#D06030; border-color:rgba(220,110,60,0.25); }
.state-calling .status-dot-cap { background:#FF8050; animation:blink 0.8s ease infinite; }
.state-checking { background:#FFF0E0; color:#D08020; border-color:rgba(220,140,40,0.3); }
.state-checking .status-dot-cap { background:#FFA040; animation:blink 0.6s ease infinite; }
.state-connected { background:#F0F8EE; color:#3A7030; border-color:rgba(80,160,60,0.25); }
.state-connected .status-dot-cap { background:#5AB040; animation:blink 2s ease infinite; }
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.3} }

/* 主布局 */
.main-layout {
  flex: 1; display: flex; gap: 16px; overflow: hidden; min-height: 0;
}

/* 视频区 */
.video-section { flex: 1; min-width: 0; }
.video-grid {
  width: 100%; height: 100%;
  display: grid; grid-template-columns: 1fr 1fr; gap: 12px;
}
.video-card {
  position: relative; background: #1A100A;
  border-radius: 16px; overflow: hidden;
  border: 1px solid rgba(255,160,120,0.15);
  box-shadow: 0 4px 20px rgba(40,10,0,0.2);
  transition: transform 0.25s ease, box-shadow 0.25s ease;
}
.video-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 30px rgba(40,10,0,0.3);
}
video { width: 100%; height: 100%; object-fit: cover; display: block; }

.video-overlay {
  position: absolute; bottom: 0; left: 0; right: 0;
  display: flex; align-items: center; justify-content: space-between;
  padding: 10px 14px;
  background: linear-gradient(transparent, rgba(20,8,2,0.65));
  pointer-events: none;
}
.video-label {
  display: flex; align-items: center; gap: 5px;
  font-size: 12px; font-weight: 600; color: rgba(255,255,255,0.9);
}
.video-badge {
  display: flex; align-items: center; gap: 4px;
  background: rgba(210,40,20,0.85); border-radius: 100px;
  padding: 2px 8px; font-size: 10px; font-weight: 700; color: white; letter-spacing: 0.08em;
}
.live-dot-sm { width: 5px; height: 5px; border-radius: 50%; background: white; animation: blink 1s ease infinite; }

.video-placeholder {
  position: absolute; inset: 0;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  gap: 10px; background: #1A100A; font-size: 12px; color: rgba(255,160,120,0.45);
}

/* 活体检测倒计时浮层 */
.liveness-overlay {
  position: absolute; inset: 0; z-index: 10;
  display: flex; align-items: center; justify-content: center;
  background: rgba(10,5,2,0.75);
  backdrop-filter: blur(4px);
}
.liveness-ring {
  display: flex; align-items: center; justify-content: center;
  width: 180px; height: 180px;
  border-radius: 50%;
  border: 2px solid rgba(255,160,120,0.3);
  box-shadow: 0 0 60px rgba(255,96,64,0.2), inset 0 0 60px rgba(255,96,64,0.08);
  animation: liveness-pulse 1.2s ease-in-out infinite;
}
@keyframes liveness-pulse {
  0%, 100% { transform: scale(1); border-color: rgba(255,160,120,0.3); }
  50% { transform: scale(1.05); border-color: rgba(255,160,120,0.6); }
}
.liveness-text {
  display: flex; flex-direction: column; align-items: center; gap: 6px;
  color: #fff; text-align: center;
}
.liveness-title {
  font-size: 15px; font-weight: 600; letter-spacing: 0.06em;
}
.liveness-sub {
  font-size: 12px; color: rgba(255,255,255,0.65);
}
.liveness-count {
  font-size: 52px; font-weight: 800; line-height: 1;
  color: #FF9A76;
  text-shadow: 0 0 30px rgba(255,96,64,0.5);
  animation: count-pop 0.9s ease-out infinite;
}
@keyframes count-pop {
  0% { transform: scale(0.5); opacity: 0.2; }
  40% { transform: scale(1.2); opacity: 1; }
  100% { transform: scale(1); opacity: 0.7; }
}
.liveness-detect-icon {
  animation: spin 1s linear infinite;
}
@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 右侧面板 */
.side-panel { width: 272px; flex-shrink: 0; display: flex; flex-direction: column; gap: 12px; }

.ctrl-card, .log-card {
  background: #FFFFFF; border-radius: 16px;
  border: 1px solid rgba(255,160,120,0.12);
  box-shadow: 0 4px 20px rgba(200,90,50,0.06);
  overflow: hidden;
}
.log-card { flex: 1; display: flex; flex-direction: column; min-height: 0; }

.card-header {
  display: flex; align-items: center; gap: 8px;
  padding: 12px 16px;
  background: linear-gradient(90deg, #FF9A76, #FF6040);
  font-size: 13px; font-weight: 700; color: white; letter-spacing: 0.04em;
  flex-shrink: 0;
}
.card-header-icon {
  width: 26px; height: 26px; border-radius: 7px;
  background: rgba(255,255,255,0.2);
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.log-clear-btn {
  margin-left: auto; background: rgba(255,255,255,0.18);
  border: 1px solid rgba(255,255,255,0.3); border-radius: 6px;
  color: white; font-size: 11px; font-weight: 500; font-family: inherit;
  padding: 3px 10px; cursor: pointer; transition: background 0.18s;
}
.log-clear-btn:hover { background: rgba(255,255,255,0.3); }

.ctrl-body { padding: 16px; display: flex; flex-direction: column; gap: 14px; }

.form-row { display: flex; flex-direction: column; gap: 5px; }
.form-label { font-size: 12px; font-weight: 600; color: #6A4030; }
.input-wrap { position: relative; display: flex; align-items: center; }
.input-icon { position: absolute; left: 10px; pointer-events: none; }
.room-input {
  width: 100%; height: 38px; padding: 0 12px 0 32px;
  border: 1px solid rgba(255,160,120,0.3); border-radius: 10px;
  font-size: 13px; font-family: inherit; color: #3A2010; background: #FFFAF7;
  outline: none; box-sizing: border-box; transition: border-color 0.2s;
}
.room-input:focus { border-color: #FF8A65; background: white; }

.btn-group { display: flex; flex-direction: column; gap: 8px; }
.ctrl-btn {
  display: flex; align-items: center; justify-content: center; gap: 6px;
  height: 40px; width: 100%; border: none; border-radius: 10px;
  font-size: 13px; font-weight: 600; font-family: inherit;
  cursor: pointer; transition: all 0.2s ease;
}
.ctrl-join {
  background: #FFF0E8; color: #D06030;
  border: 1px solid rgba(220,120,80,0.25);
}
.ctrl-join:hover { background: #FFE4D4; }
.ctrl-call {
  background: linear-gradient(90deg, #FF9A76, #FF6040); color: white;
  box-shadow: 0 3px 10px rgba(255,96,64,0.28);
}
.ctrl-call:hover:not(:disabled) { transform: translateY(-1px); box-shadow: 0 5px 14px rgba(255,96,64,0.38); }
.ctrl-call:disabled { background: #E8DDD8; color: #B0A098; box-shadow: none; cursor: not-allowed; }

.conn-info {
  background: #FFF8F5; border: 1px solid rgba(255,160,120,0.15);
  border-radius: 10px; padding: 10px 12px;
  display: flex; flex-direction: column; gap: 7px;
}
.conn-row { display: flex; justify-content: space-between; align-items: center; }
.conn-label { font-size: 11px; color: #B09080; }
.conn-val { font-size: 11px; font-weight: 500; color: #5A3020; font-family: monospace; }
.conn-status { font-size: 11px; font-weight: 600; font-family: inherit; }

.log-body {
  flex: 1; overflow-y: auto; padding: 10px 14px;
  display: flex; flex-direction: column; gap: 3px; min-height: 0;
}
.log-body::-webkit-scrollbar { width: 4px; }
.log-body::-webkit-scrollbar-thumb { background: rgba(255,160,120,0.3); border-radius: 4px; }
.log-line { display: flex; gap: 8px; font-size: 11.5px; line-height: 1.6; color: #5A3820; }
.log-time { color: #C4A898; font-size: 10.5px; flex-shrink: 0; font-family: monospace; }

@media (max-width: 900px) {
  .main-layout { flex-direction: column; overflow-y: auto; }
  .video-grid { grid-template-columns: 1fr; height: auto; }
  .video-card { aspect-ratio: 16/9; }
  .side-panel { width: 100%; }
}
</style>
