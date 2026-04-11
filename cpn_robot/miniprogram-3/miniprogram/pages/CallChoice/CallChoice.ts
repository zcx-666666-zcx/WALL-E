// pages/CallChoice/CallChoice.ts
//韬韬温馨提示：请设置或修改27,31,47*,135行的参数,47非必须修改，其余可以选择性修改的参数我在注释上标注了“自己设置“，如果通话启动失败，不论何种原因导致的，都看不到任何画面，只有启动成功才能看到画面

//定义消息接口,用于规范WebSocket通信的消息格式
interface Message {
  type: 'video' | 'audio' | 'control';  // 消息类型：视频/音频/控制
  data: any;                            // 消息数据内容
  timestamp: number;                    // 时间戳，用于排序和同步
  sender: 'client' | 'device';          // 发送者：客户端/设备端
  targetContact?: string;               // 目标设备ID（可选）
}

Page({
  data: {
    pageStatus: 'ready', //ready（准备状态）inVideoCall（视频通话中）inAudioCall（语音通话中）
    
    selectedContactName: '',  //当前选中的设备名称
    showContactList: false,   //是否显示设备选择列表
    
    cameraErrorCount: 0,      //摄像头错误计数，用于错误处理
    cameraLoaded: false,      //摄像头是否加载完成
    
    isTakingPhoto: false,     //是否正在拍照（防止重复拍照）
    photoTimer: null as any,  //拍照定时器引用
    lastPhotoTime: 0,         //上次拍照时间戳，用于控制拍照频率
    photoInterval: 200,       //拍照间隔（毫秒），200ms=5fps
    
    isRecordingAudio: false,  //是否正在录音
    audioTimer: null as any,  //音频录制定时器
    audioInterval: 100,       //音频录制间隔（100ms=10次/秒）
    recorderManager: null as any,  //微信录音管理器
    
    ws: null as any,          //WebSocket连接实例
    wsConnected: false,       //WebSocket连接状态
    wsReconnectCount: 0,      //重连次数计数
    maxReconnectCount: 5,     //最大重连次数
    
    receivedVideoFrames: [] as string[],  //接收到的视频帧队列（base64字符串）
    currentVideoFrame: '',                //当前显示的帧
    videoFrameTimer: null as any,         //视频帧播放定时器
    videoFrameInterval: 200,              //帧播放间隔
    
    audioContext: null as any,    //音频播放上下文
    isPlayingAudio: false,        //是否正在播放音频
    audioQueue: [] as string[],   //音频数据队列
    contacts: [//设备列表,全是假的
      { name: "ESP32-Device-001", deviceId: "esp32_001", ip: "192.168.1.100" },
      { name: "Raspberry-Pi-001", deviceId: "rpi_001", ip: "192.168.1.101" },
      { name: "AIoT-Camera-001", deviceId: "aiot_001", ip: "192.168.1.102" }
    ],
    buttonTexts: {
      video: '视频通话',
      audio: '语音通话',
      stop: '挂断'
    },
    debugInfo: {
      sentFrames: 0,      //已发送的视频帧数
      receivedFrames: 0,  //已接收的视频帧数
      sentAudio: 0,       //已发送的音频包数
      receivedAudio: 0,   //已接收的音频包数
      wsStatus: '未连接'   //WebSocket连接状态文本
    }
  },
  onLoad() {
    console.log('页面加载');this.initRecorder();/*初始化录音功能*/this.initAudioContext();// 初始化音频播放功能
  },
  onUnload() {
    console.log('页面卸载，清理所有资源');this.stopAll();/*停止所有通话*/this.closeWebSocket();   // 关闭WebSocket连接
  },
  onHide() {
    console.log('页面隐藏');
    // 如果正在通话中，则停止通话
    if (this.data.pageStatus !== 'ready') {
      this.stopAll();
    }
  },

  //初始化录音管理器,设置录音的各种事件监听器
  initRecorder() {
    // 获取微信录音管理器实例
    const recorderManager = wx.getRecorderManager();
    this.setData({ recorderManager });
    //录音开始事件
    recorderManager.onStart(() => {
      console.log('录音开始');
    });
    //录音结束事件（重要：处理录制的音频文件）
    recorderManager.onStop((res: any) => {
      console.log('录音结束', res.tempFilePath);
      this.handleAudioRecorded(res.tempFilePath);//处理录制好的音频文件
    });
    //录音错误事件
    recorderManager.onError((res: any) => {
      console.error('录音错误:', res);
    });
  },

  //初始化音频播放上下文,用于播放接收到的音频数据
  initAudioContext() {
    // 创建微信内部音频上下文
    const audioContext = wx.createInnerAudioContext();
    this.setData({ audioContext });
    // 音频开始播放事件
    audioContext.onPlay(() => {
      console.log('音频开始播放');
    });
    // 音频播放结束事件
    audioContext.onEnded(() => {
      console.log('音频播放结束');
      // 播放下一段音频（如果队列中有）
      this.playNextAudio();
    });
    // 音频播放错误事件
    audioContext.onError((res: any) => {
      console.error('音频播放错误:', res);
    });
  },
  
  /**
   * 连接到指定设备的WebSocket服务器
   * @param deviceIp 设备IP地址
   * @returns Promise，连接成功时解析
   */
  connectWebSocket(deviceIp: string) {
    return new Promise((resolve, reject) => {
      console.log('正在连接WebSocket:' ,`ws://${deviceIp}:8080/ws`);
      //如果已有连接，先关闭
      if (this.data.ws) {
        this.data.ws.close();
      }
      
      //创建WebSocket连接
      const ws = wx.connectSocket({
        url: `ws://${deviceIp}:8080/ws`,  //WebSocket地址,自己设置------------------------------------
        timeout: 5000                     //5秒超时
      });
      
      this.setData({ ws });
      
      // 连接成功事件
      ws.onOpen(() => {
        console.log('✅ WebSocket连接成功');
        this.setData({
          wsConnected: true,
          wsReconnectCount: 0,  //重置重连计数
          debugInfo: { ...this.data.debugInfo, wsStatus: '已连接' }
        });
        resolve(ws);  //Promise解析，表示连接成功
      });
      
      // 连接关闭事件
      ws.onClose(() => {
        console.log('WebSocket连接关闭');
        this.setData({
          wsConnected: false,
          debugInfo: { ...this.data.debugInfo, wsStatus: '已断开' }
        });
        
        // 如果在通话中且未超过最大重连次数，尝试重连
        if (this.data.pageStatus !== 'ready' && this.data.wsReconnectCount < this.data.maxReconnectCount) {
          const newCount = this.data.wsReconnectCount + 1;
          this.setData({ wsReconnectCount: newCount });
          console.log(`第${newCount}次尝试重连...`);
          setTimeout(() => {
            this.connectWebSocket(deviceIp);
          }, 2000);  //2秒后重连
        }
      });
      
      // 连接错误事件
      ws.onError((error: any) => {
        console.error('WebSocket错误:', error);
        this.setData({
          debugInfo: { ...this.data.debugInfo, wsStatus: '连接错误' }
        });
        reject(error);  //Promise拒绝，表示连接失败
      });
      
      /**
       * 接收消息事件（核心处理函数）
       * 处理从设备端发送来的各种消息
       */
      ws.onMessage((res: { data: string | ArrayBuffer }) => {
        try {
          // 消息数据可能是字符串或ArrayBuffer，需要统一处理
          let messageString: string;
          
          if (typeof res.data === 'string') {
            //如果是字符串，直接使用
            messageString = res.data;
          } else if (res.data instanceof ArrayBuffer) {
            //如果是ArrayBuffer，转换为字符串
            //ArrayBuffer -> Uint8Array -> 字符串
            const uint8Array = new Uint8Array(res.data);
            messageString = String.fromCharCode.apply(null, Array.from(uint8Array));
          } else {
            console.error('未知的消息数据类型');
            return;
          }
          
          //解析JSON消息
          const message = JSON.parse(messageString) as Message;
          //根据消息类型分发处理
          this.handleIncomingMessage(message);
        } catch (error) {
          console.error('消息解析错误:', error);
        }
      });
    });
  },

  //关闭WebSocket连接
  closeWebSocket() {
    if (this.data.ws) {
      this.data.ws.close();
      this.setData({ ws: null, wsConnected: false });
    }
  },

  //发送消息到设备端
  sendMessage(message: Message) {
    //检查连接状态
    if (!this.data.wsConnected || !this.data.ws) {
      console.warn('WebSocket未连接，无法发送消息');
      return false;
    }
    
    try {
      const messageString = JSON.stringify(message);//将消息对象转换为JSON字符串
      
      //发送消息
      this.data.ws.send({
        data: messageString,
        success: () => {
          //更新调试信息统计
          if (message.type === 'video') {
            const newCount = this.data.debugInfo.sentFrames + 1;
            this.setData({
              debugInfo: { ...this.data.debugInfo, sentFrames: newCount }
            });
          } else if (message.type === 'audio') {
            const newCount = this.data.debugInfo.sentAudio + 1;
            this.setData({
              debugInfo: { ...this.data.debugInfo, sentAudio: newCount }
            });
          }
        },
        fail: (err: any) => {
          console.error('消息发送失败:', err);
        }
      });
      return true;
    } catch (error) {
      console.error('发送消息异常:', error);
      return false;
    }
  },
  
  //处理接收到的消息,根据消息类型分发到不同的处理函数
  handleIncomingMessage(message: Message) {
    console.log('收到消息:', message.type);
    
    switch (message.type) {
      case 'video':
        // 视频帧消息：处理接收到的图片
        this.handleVideoFrame(message.data);
        break;
        
      case 'audio':
        // 音频消息：处理接收到的音频数据
        this.handleAudioData(message.data);
        break;
        
      case 'control':
        // 控制消息：处理通话控制指令
        this.handleControlMessage(message.data);
        break;
        
      default:
        console.warn('未知消息类型:', message.type);
    }
  },

  //处理接收到的视频帧
  handleVideoFrame(imageData: any) {
    // 提取图片字符串（兼容不同格式）
    const imageString = typeof imageData === 'string' ? imageData : 
                       imageData.imageData || '';
    
    // 添加到帧队列
    const newFrames = [...this.data.receivedVideoFrames, imageString];

    // 限制队列长度，防止内存泄漏
    if (newFrames.length > 20) {
      newFrames.shift();  // 移除最旧的帧
    }
    
    // 更新状态
    this.setData({
      receivedVideoFrames: newFrames,
      debugInfo: { ...this.data.debugInfo, receivedFrames: this.data.debugInfo.receivedFrames + 1 }
    });
    
    // 如果还没有启动帧播放器，则启动
    if (!this.data.videoFrameTimer && this.data.pageStatus === 'inVideoCall') {
      this.startVideoFramePlayback();
    }
  },

  //处理接收到的音频数据
  handleAudioData(audioData: any) {
    // 提取音频字符串
    const audioString = typeof audioData === 'string' ? audioData : 
                       audioData.audioData || '';
    
    // 添加到音频队列
    const newQueue = [...this.data.audioQueue, audioString];
    
    // 限制队列长度
    if (newQueue.length > 20) {
      newQueue.shift();
    }
    
    // 更新状态
    this.setData({
      audioQueue: newQueue,
      debugInfo: { ...this.data.debugInfo, receivedAudio: this.data.debugInfo.receivedAudio + 1 }
    });
    
    // 如果当前没有播放音频，则开始播放
    if (!this.data.isPlayingAudio && this.data.pageStatus === 'inAudioCall') {
      this.playNextAudio();
    }
  },

  //处理控制消息
  handleControlMessage(data: any) {
    console.log('控制消息:', data);
    
    //根据命令类型执行不同操作
    switch (data.command) {
      case 'accept':
        //设备接受了通话请求
        wx.showToast({
          title: '对方已接听',
          icon: 'success',
          duration: 2000
        });
        break;
        
      case 'reject':
        //设备拒绝了通话请求
        wx.showToast({
          title: '对方已拒绝',
          icon: 'none',
          duration: 2000
        });
        this.stopAll();  //停止通话
        break;
        
      case 'hangup':
        //设备主动挂断通话
        wx.showToast({
          title: '对方已挂断',
          icon: 'none',
          duration: 2000
        });
        this.stopAll();
        break;
        
      case 'error':
        //设备报告错误
        wx.showToast({
          title: `设备错误: ${data.reason}`,
          icon: 'none',
          duration: 3000
        });
        break;
    }
  },
  
  //切换设备列表的显示/隐藏
  toggleContactList() {
    this.setData({
      showContactList: !this.data.showContactList
    });
  },

  //选择设备
  selectContact(e: any) {
    const index = e.currentTarget.dataset.index;
    const contact = this.data.contacts[index];
    
    this.setData({
      selectedContactName: contact.name,
      showContactList: false  // 选择后隐藏列表
    });
    
    console.log('选择了设备:', contact.name, 'IP:', contact.ip);
  },
  
  //开始视频通话,权限检查 -> 连接WebSocket -> 发送请求 -> 开始拍照
  async startVideoCall() {
    //检查是否选择了设备
    if (!this.data.selectedContactName) {
      wx.showToast({ 
        title: '请先选择设备', 
        icon: 'none',
        duration: 2000 
      });
      return;
    }
    console.log('开始视频通话');
    try {
      await this.requestCameraPermission();//请求摄像头权限
      
      //查找设备信息并连接WebSocket
      const contact = this.data.contacts.find(c => c.name === this.data.selectedContactName);
      if (!contact) {
        throw new Error('设备信息错误');
      }
      
      await this.connectWebSocket(contact.ip);
      
      //发送通话请求到设备
      this.sendMessage({
        type: 'control',
        data: {
          command: 'call_request',
          callType: 'video',
          timestamp: Date.now()
        },
        timestamp: Date.now(),
        sender: 'client',
        targetContact: contact.deviceId
      });

      this.setData({
        pageStatus: 'inVideoCall',  // 进入视频通话状态
        cameraLoaded: false,        // 摄像头未加载
        cameraErrorCount: 0,        // 重置错误计数
        buttonTexts: {              // 更新按钮文本
          video: '结束视频',         // 视频按钮变为结束功能
          audio: '语音通话',
          stop: '挂断'
        }
      });
      
      wx.showLoading({
        title: '正在连接设备...',
        mask: true  // 阻止用户操作
      });
      
      console.log('等待Camera组件初始化...');
      
      //延迟启动拍照（给摄像头和网络足够时间初始化）
      setTimeout(() => {
        wx.hideLoading();  // 隐藏加载提示
        if (this.data.pageStatus === 'inVideoCall') {
          this.startPhotoCapture();  // 开始拍照
          this.startAudioRecording();   //开始录音
        }
      }, 3000);  // 3秒后开始-------------------------------自己设置
      
    } catch (error: any) {
      console.error('视频通话启动失败:', error);
      wx.hideLoading();
      wx.showToast({ 
        title: error.message || '启动失败', 
        icon: 'none',
        duration: 3000 
      });
      this.stopAll();
    }
  },

  //请求摄像头权限
  requestCameraPermission(): Promise<void> {
    return new Promise((resolve, reject) => {
      wx.authorize({
        scope: 'scope.camera',  //请求摄像头权限
        success: () => resolve(),
        fail: (err: any) => {
          reject(new Error('需要摄像头权限'));
        }
      });
    });
  },

  //开始定期拍照（模拟视频流）,使用定时器定期调用拍照函数
  startPhotoCapture() {
    console.log('开始拍照捕获...');
    
    // 清理可能存在的旧定时器
    if (this.data.photoTimer) {
      clearInterval(this.data.photoTimer);
    }
    
    // 创建摄像头上下文
    const cameraContext = wx.createCameraContext();
    
    // 设置定时器，定期拍照
    const timer = setInterval(() => {
      this.takeSinglePhoto(cameraContext);
    }, this.data.photoInterval);
    
    this.setData({ photoTimer: timer });
    console.log(`✅ 拍照定时器已启动（${this.data.photoInterval}ms/帧）`);
  },

  //单次拍照函数
  takeSinglePhoto(cameraContext: any) {
    // 检查拍照频率，防止过于频繁
    const now = Date.now();
    const timeSinceLastPhoto = now - this.data.lastPhotoTime;
    
    if (timeSinceLastPhoto < this.data.photoInterval - 50) {//自己设置-------------
      return;  // 距离上次拍照时间太短，跳过
    }
    
    const { isTakingPhoto, pageStatus, cameraErrorCount } = this.data;//安全检查
    
    if (isTakingPhoto || pageStatus !== 'inVideoCall' || cameraErrorCount >= 3) {
      return;  //正在拍照/不在视频通话状态/错误次数过多，跳过
    }
    
    this.setData({ isTakingPhoto: true });//设置拍照标志位
    
    // 调用微信拍照API
    cameraContext.takePhoto({
      quality: 'low',  // 低质量，减少数据量------------------------自己设置
      success: (res: any) => {
        this.setData({ lastPhotoTime: Date.now() });//更新最后拍照时间
        
        //如果之前有错误，现在重置
        if (cameraErrorCount > 0) {
          this.setData({ cameraErrorCount: 0 });
        }
        
        this.processAndSendPhoto(res.tempImagePath);//处理并发送图片
        
        this.setData({ isTakingPhoto: false });//重置拍照标志位
      },
      fail: (err: any) => {
        console.error('拍照失败:', err);
        const newCount = cameraErrorCount + 1;
        this.setData({ 
          cameraErrorCount: newCount,
          isTakingPhoto: false 
        });
        
        //如果错误次数过多，停止拍照并通知设备
        if (newCount >= 3) {
          this.sendMessage({
            type: 'control',
            data: { command: 'error', reason: '摄像头故障' },
            timestamp: Date.now(),
            sender: 'client'
          });
          this.stopPhotoCapture();
        }
      }
    });
  },

  //处理并发送照片
  async processAndSendPhoto(tempPath: string) {
    try {
      const fileSystem = wx.getFileSystemManager();//读取图片文件
      
      // 同步读取文件为base64编码字符串
      // readFileSync返回类型是string | ArrayBuffer，但指定'base64'参数时返回string
      const fileData = fileSystem.readFileSync(tempPath, 'base64') as string;
      
      const compressedData = fileData.substring(0, 20000);//压缩数据：截取前20000个字符（约20KB）,控制数据大小，避免传输过大的图片,数字越大可以传的图片就越大
      
      const contact = this.data.contacts.find(c => c.name === this.data.selectedContactName);//查找设备信息
      
      // 4. 发送视频帧消息
      this.sendMessage({
        type: 'video',
        data: {
          imageData: compressedData,          // 图片数据
          timestamp: Date.now(),              // 时间戳
          frameIndex: this.data.debugInfo.sentFrames  // 帧序号
        },
        timestamp: Date.now(),
        sender: 'client',
        targetContact: contact?.deviceId
      });
      
      // 5. 清理临时文件（避免占用存储空间）
      try {
        fileSystem.unlink({
          filePath: tempPath,
          fail: () => {}  // 忽略清理错误
        });
      } catch (e) {
        // 忽略错误
      }
      
    } catch (error) {
      console.error('图片处理失败:', error);
    }
  },

  //停止拍照捕获,清理定时器和状态
  stopPhotoCapture() {
    if (this.data.photoTimer) {
      clearInterval(this.data.photoTimer);
      this.setData({ photoTimer: null });
    }
    this.setData({ isTakingPhoto: false });
  },
  
  //开始播放接收到的视频帧,使用定时器从帧队列中取出帧进行显示
  startVideoFramePlayback() {
    console.log('开始播放接收到的视频帧');
    
    //清理可能存在的旧定时器
    if (this.data.videoFrameTimer) {
      clearInterval(this.data.videoFrameTimer);
    }
    
    //设置帧播放定时器
    const timer = setInterval(() => {
      this.displayNextVideoFrame();
    }, this.data.videoFrameInterval);
    
    this.setData({ videoFrameTimer: timer });
  },

  //显示下一帧,从帧队列中取出最早的帧进行显示
  displayNextVideoFrame() {
    const { receivedVideoFrames } = this.data;
    
    if (receivedVideoFrames.length > 0) {
      const frame = receivedVideoFrames[0];//取出队列中的第一帧
      const newFrames = receivedVideoFrames.slice(1);//移除已显示的帧
      
      // 更新当前显示的帧
      this.setData({
        currentVideoFrame: frame,
        receivedVideoFrames: newFrames
      });
    }
  },

  //停止视频帧播放
  stopVideoFramePlayback() {
    if (this.data.videoFrameTimer) {
      clearInterval(this.data.videoFrameTimer);
      this.setData({ videoFrameTimer: null });
    }
  },

  //开始语音通话,连接WebSocket -> 发送请求 -> 开始录音
  async startAudioCall() {
    if (!this.data.selectedContactName) {
      wx.showToast({ 
        title: '请先选择设备', 
        icon: 'none',
        duration: 2000 
      });
      return;
    }
    console.log('开始语音通话');
    try {
      //查找设备信息并连接WebSocket
      const contact = this.data.contacts.find(c => c.name === this.data.selectedContactName);
      if (!contact) {
        throw new Error('设备信息错误');
      }
      
      await this.connectWebSocket(contact.ip);
      
      //发送语音通话请求
      this.sendMessage({
        type: 'control',
        data: {
          command: 'call_request',
          callType: 'audio',
          timestamp: Date.now()
        },
        timestamp: Date.now(),
        sender: 'client',
        targetContact: contact.deviceId
      });
      this.setData({
        pageStatus: 'inAudioCall',
        buttonTexts: {
          video: '视频通话',
          audio: '结束语音',  // 语音按钮变为结束功能
          stop: '挂断'
        }
      });
      
      //显示加载提示
      wx.showLoading({
        title: '正在连接设备...',
        mask: true
      });
      
      //延迟开始录音（给网络连接足够时间）
      setTimeout(() => {
        wx.hideLoading();
        if (this.data.pageStatus === 'inAudioCall') {
          this.startAudioRecording();  // 开始录音
        }
      }, 2000);//自己设置--------------------------
      
    } catch (error: any) {
      console.error('语音通话启动失败:', error);
      wx.hideLoading();
      wx.showToast({ 
        title: error.message || '启动失败', 
        icon: 'none',
        duration: 3000 
      });
      this.stopAll();
    }
  },

  //开始音频录制,使用定时器定期录制短音频片段
  startAudioRecording() {
    console.log('开始音频录制...');
    
    //清理旧定时器
    if (this.data.audioTimer) {
      clearInterval(this.data.audioTimer);
    }
  
    this.recordAudioChunk();//立即开始第一次录制
    
    //设置定时器，定期录制
    const timer = setInterval(() => {
      if (!this.data.isRecordingAudio) {
        this.recordAudioChunk();
      }
    }, this.data.audioInterval);
    
    this.setData({ audioTimer: timer });
    console.log(`✅ 音频录制定时器已启动（${this.data.audioInterval}ms/次）`);
  },

  //录制音频片段,每次录制100ms的音频
  recordAudioChunk() {
    // 安全检查
    if (this.data.isRecordingAudio || this.data.pageStatus !== 'inAudioCall') {
      return;
    }
    
    // 设置录音标志位
    this.setData({ isRecordingAudio: true });
    
    // 开始录音
    this.data.recorderManager.start({
      duration: 100,           // 录制100ms
      sampleRate: 8000,        // 8kHz采样率（电话音质）
      numberOfChannels: 1,     // 单声道
      encodeBitRate: 16000,    // 16kbps比特率
      format: 'mp3'            // MP3格式
    });
    
    //100ms后自动停止（由duration参数控制，这里设置110ms确保停止）
    setTimeout(() => {
      if (this.data.isRecordingAudio) {
        this.data.recorderManager.stop();
      }
    }, 110);
  },

  //处理录制完成的音频
  async handleAudioRecorded(tempPath: string) {
    this.setData({ isRecordingAudio: false });//重置录音标志位
    
    try {
      const fileSystem = wx.getFileSystemManager();//读取音频文件
      
      const fileData = fileSystem.readFileSync(tempPath, 'base64') as string;//读取为base64字符串
      
      const compressedData = fileData.substring(0, 10000);//压缩数据：截取前10000个字符，自己设置
      
      const contact = this.data.contacts.find(c => c.name === this.data.selectedContactName);//查找设备信息
      
      //发送音频数据
      this.sendMessage({
        type: 'audio',
        data: {
          audioData: compressedData,        // 音频数据
          timestamp: Date.now(),            // 时间戳
          audioIndex: this.data.debugInfo.sentAudio  // 音频包序号
        },
        timestamp: Date.now(),
        sender: 'client',
        targetContact: contact?.deviceId
      });
      
      //清理临时文件
      try {
        fileSystem.unlink({
          filePath: tempPath,
          fail: () => {}
        });
      } catch (e) {
        //忽略错误
      }
      
    } catch (error) {
      console.error('音频处理失败:', error);
    }
  },
  
  //播放下一段音频,从音频队列中取出音频数据进行播放
  playNextAudio() {
    const { audioQueue, audioContext, isPlayingAudio, pageStatus } = this.data;
    
    //安全检查
    if (isPlayingAudio || pageStatus !== 'inAudioCall' || audioQueue.length === 0) {
      return;
    }
    
    //取出队列中的第一个音频数据
    const audioData = audioQueue[0];
    const newQueue = audioQueue.slice(1);
    
    //更新状态
    this.setData({
      audioQueue: newQueue,
      isPlayingAudio: true  //设置播放标志位
    });
    
    console.log('播放音频数据，长度:', audioData.length);
    
    // 注意：这里简化了播放逻辑
    // 实际应该：base64解码 -> 转换为音频Buffer -> 播放
    // 由于小程序限制，这里只做示意
    
    //模拟播放完成（100ms后）
    setTimeout(() => {
      this.setData({ isPlayingAudio: false });
      
      // 如果队列中还有音频，继续播放
      if (newQueue.length > 0) {
        this.playNextAudio();
      }
    }, 100);
  },
  
  //Camera初始化完成事件
  onCameraInitDone(e: any) {
    console.log('✅ Camera组件初始化完成');
    this.setData({ cameraLoaded: true });
  },

  //Camera错误事件
  onCameraError(e: any) {
    console.warn('Camera错误:', e.detail);
    // 增加错误计数
    const newCount = this.data.cameraErrorCount + 1;
    this.setData({ cameraErrorCount: newCount });
  },

  //停止所有通话，清理所有资源,这是通话结束的统一入口
  stopAll() {
    console.log('=== 停止所有通话 ===');
    //停止视频相关
    this.stopPhotoCapture();          // 停止拍照
    this.stopVideoFramePlayback();    // 停止帧播放
    //停止音频相关
    if (this.data.audioTimer) {
      clearInterval(this.data.audioTimer);  // 停止录音定时器
    }
    if (this.data.isRecordingAudio) {
      this.data.recorderManager.stop();     // 停止录音
    }
    if (this.data.audioContext) {
      this.data.audioContext.stop();        // 停止音频播放
    }
    
    //发送挂断消息到设备
    const contact = this.data.contacts.find(c => c.name === this.data.selectedContactName);
    if (contact && this.data.wsConnected) {
      this.sendMessage({
        type: 'control',
        data: { command: 'hangup', timestamp: Date.now() },
        timestamp: Date.now(),
        sender: 'client',
        targetContact: contact.deviceId
      });
    }

    this.setData({
      pageStatus: 'ready',         // 回到准备状态
      cameraLoaded: false,         // 摄像头未加载
      cameraErrorCount: 0,         // 重置错误计数
      isTakingPhoto: false,        // 不在拍照
      isRecordingAudio: false,     // 不在录音
      isPlayingAudio: false,       // 不在播放
      receivedVideoFrames: [],     // 清空视频帧队列
      currentVideoFrame: '',       // 清空当前显示帧
      audioQueue: [],              // 清空音频队列
      buttonTexts: {               // 重置按钮文本
        video: '视频通话',
        audio: '语音通话',
        stop: '挂断'
      }
    });
    wx.showToast({ 
      title: '通话已结束', 
      icon: 'success',
      duration: 2000 
    });
  },

  //视频按钮点击事件,根据当前状态执行不同操作
  onVideoButtonTap() {
    if (this.data.pageStatus === 'inVideoCall') {
      //正在视频通话中，点击则停止
      this.stopAll();
    } else if (this.data.pageStatus === 'inAudioCall') {
      //正在语音通话中，先停止语音再开始视频
      this.stopAll();
      setTimeout(() => {
        this.startVideoCall();
      }, 500);  //500ms延迟，确保状态完全重置,自己设置-----------------
    } else {
      //空闲状态，直接开始视频通话
      this.startVideoCall();
    }
  },

  //语音按钮点击事件
  onAudioButtonTap() {
    if (this.data.pageStatus === 'inAudioCall') {
      // 正在语音通话中，点击则停止
      this.stopAll();
    } else if (this.data.pageStatus === 'inVideoCall') {
      // 正在视频通话中，先停止视频再开始语音
      this.stopAll();
      setTimeout(() => {
        this.startAudioCall();
      }, 500);
    } else {
      // 空闲状态，直接开始语音通话
      this.startAudioCall();
    }
  },

  //挂断按钮点击事件,无论当前是什么状态，都停止通话
  onStopButtonTap() {
    this.stopAll();
  }
});