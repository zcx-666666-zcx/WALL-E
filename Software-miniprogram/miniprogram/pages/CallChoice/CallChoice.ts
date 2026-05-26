const { getSocketServerUrl } = require('../../utils/config.js');

// pages/call/call.js
Page({
  data: {
    roomId: "0001",
    isJoined: false,
    statusText: "请先加入房间...",
    logs: [],
    SERVER_URL: "",
  },

  socket: null,
  localStream: null,
  peerConnection: null,

  onLoad() {
    this.setData({ SERVER_URL: getSocketServerUrl() });
    this.log("页面加载完成，等待连接...");
  },

  // 日志：改为 {time, msg} 对象，配合模板分列显示
  log(msg) {
    const time = new Date().toLocaleTimeString();
    this.setData({
      logs: [...this.data.logs, { time, msg }]
    });
  },

  onRoomInput(e) {
    this.setData({ roomId: e.detail.value });
  },

  joinRoom() {
    const { roomId } = this.data;
    this.log("连接信令服务器...");

    this.socket = io(this.data.SERVER_URL, { transports: ['websocket'] });

    this.socket.on('connect', () => {
      this.log(`已连接 (ID: ${this.socket.id})`);
      this.socket.emit('join', { room: roomId });
    });

    this.socket.on('joined', (data) => {
      this.log(`已加入房间: ${data.room}`);
      this.setData({
        isJoined: true,
        statusText: "已就绪，等待通话"
      });
      this.startLocalCamera();
    });

    this.socket.on('message', async (data) => {
      if (data.type === 'offer')     await this.handleOffer(data);
      if (data.type === 'answer')    await this.handleAnswer(data);
      if (data.type === 'candidate') await this.handleCandidate(data);
    });
  },

  async startLocalCamera() {
    try {
      const stream = await wx.createCameraContext().getVideoTrack();
      this.localStream = stream;
      this.log("摄像头已开启");
    } catch (e) {
      this.log("摄像头开启失败：" + e.message);
    }
  },

  createPeerConnection() {
    this.log("正在创建通话连接...");
    this.peerConnection = new RTCPeerConnection({
      iceServers: [{ urls: "stun:stun.l.google.com:19302" }]
    });

    this.peerConnection.onicecandidate = (e) => {
      if (e.candidate) {
        this.socket.emit('message', {
          room: this.data.roomId,
          payload: { type: 'candidate', candidate: e.candidate }
        });
      }
    };

    this.peerConnection.ontrack = (e) => {
      this.log("🎬 收到远端视频流");
      this.setData({ statusText: "视频通话中" });
      wx.createVideoContext('remoteVideo').setSrcObject(e.streams[0]);
    };

    this.localStream.getTracks().forEach(track => {
      this.peerConnection.addTrack(track, this.localStream);
    });
  },

  async startCall() {
    this.createPeerConnection();
    const offer = await this.peerConnection.createOffer();
    await this.peerConnection.setLocalDescription(offer);
    this.log("📤 发送呼叫请求...");
    this.socket.emit('message', { room: this.data.roomId, payload: offer });
  },

  async handleOffer(offer) {
    this.log("📥 收到呼叫，准备接听...");
    this.createPeerConnection();
    await this.peerConnection.setRemoteDescription(offer);
    const answer = await this.peerConnection.createAnswer();
    await this.peerConnection.setLocalDescription(answer);
    this.socket.emit('message', { room: this.data.roomId, payload: answer });
    this.log("📤 已发送应答");
  },

  async handleAnswer(answer) {
    this.log("📥 对方已接听，连接建立中...");
    await this.peerConnection.setRemoteDescription(answer);
  },

  async handleCandidate(data) {
    if (this.peerConnection) {
      await this.peerConnection.addIceCandidate(data.candidate);
    }
  },
});
