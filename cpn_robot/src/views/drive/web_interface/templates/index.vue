<script setup>
    import { ref, onMounted, onUnmounted } from 'vue'

const cameraActive = ref(1)          // 摄像头状态
const connected = ref(0)             // Arduino连接状态
const joystickX = ref(0)             // 操纵杆X坐标
const joystickY = ref(0)             // 操纵杆Y坐标
const ttsText = ref('')              // 文字转语音输入
const motorOffset = ref(190)         // 电机死区
const steerOffset = ref(0)           // 转向偏移
const selectedPort = ref(0)          // 选中的串口
const portSelect = ref(0)            // 默认选中的串口索引
const ports = ref([])                // 串口列表
const audioGroups = ref([])          // 音频分组数据

//代码块配置参数（对应原config变量）
const codeConfig = {
  CODEBLOCK_MOTORPOWER: 50,
  CODEBLOCK_MOTORSPEED: 100,
  CODEBLOCK_TURNPOWER: 50,
  CODEBLOCK_TURNTIME: 2
}

//媒体路径
const mediaPath = '/static/js/blockly/media/'

//音频选项数组
const audioOptions = ref([])

//组件挂载时初始化
onMounted(() => {
  //初始化外部脚本
  initExternalScripts()
  
  //模拟加载串口列表
  loadPorts()
  
  //模拟加载音频分组数据
  loadAudioGroups()
  
  //初始化工具提示
  initTooltips()
})

//生命周期 - 组件卸载时清理
onUnmounted(() => {
  //清理定时器、事件监听等
  cleanupResources()
})

//事件处理函数
const handleArduinoClick = () => {
  //触发设置标签点击
  document.getElementById('settings-tab').click()
}

const handleRangeFocus = (e) => {
  //保存range输入框的旧值
  e.target.oldvalue = e.target.value
}

const handleFileLoad = (e) => {
  //处理文件加载
  const file = e.target.files[0]
  if (file) {
    //这里添加文件读取逻辑
    console.log('加载文件:', file.name)
  }
}

//核心业务函数
const handleAnimeMode = (mode) => {
  sendSettings('animeMode', mode)
  servoInputs(mode === 0 ? 1 : 0)
}

const sendSettings = (key, value) => {
  //发送设置到后端的逻辑
  console.log(`发送设置: ${key} = ${value}`)
  //这里需要替换为实际的API请求
}

const servoControl = (el, type, value) => {
  //舵机控制逻辑
  console.log(`舵机控制 - 类型: ${type}, 值: ${value}`)
  //这里需要替换为实际的控制逻辑
}

const servoPresets = (el, preset, cmd) => {
  //舵机预设值控制
  console.log(`舵机预设 - ${preset}, 指令: ${cmd}`)
  //这里需要替换为实际的控制逻辑
}

const anime = (fileId, duration) => {
  //动画播放逻辑
  console.log(`播放动画 - ID: ${fileId}, 时长: ${duration}s`)
  updateProgress('anime-progress', duration)
}

const playAudio = (fileName, duration) => {
  //音频播放逻辑
  console.log(`播放音频 - 文件: ${fileName}, 时长: ${duration}s`)
  audioOptions.value.push(fileName)
  updateProgress('audio-progress', duration)
}

const playTTS = (text) => {
  //文字转语音
  console.log(`文字转语音: ${text}`)
  //这里添加TTS逻辑
}

const runCode = () => {
  //运行Blockly代码
  console.log('运行代码')
  //这里添加代码执行逻辑
}

const stopCode = () => {
  //停止代码执行
  console.log('停止代码')
  //这里添加停止逻辑
}

const saveFile = () => {
  //保存文件
  console.log('保存文件')
  //这里添加文件保存逻辑
}

const updateOffsets = () => {
  //更新偏移值
  console.log(`更新偏移 - 电机: ${motorOffset.value}, 转向: ${steerOffset.value}`)
  sendSettings('motorOffset', motorOffset.value)
  sendSettings('steerOffset', steerOffset.value)
}

const updateSerialList = (refresh) => {
  //更新串口列表
  console.log('刷新串口列表:', refresh)
  loadPorts()
}

const arduinoConnect = (el) => {
  //连接/断开Arduino
  connected.value = connected.value === 1 ? 0 : 1
  console.log(`Arduino ${connected.value === 1 ? '已连接' : '已断开'}`)
}

//辅助函数
const initExternalScripts = () => {
  //初始化外部脚本（joystick、blockly等）
  //这里需要根据实际的外部脚本进行初始化
  console.log('初始化外部脚本')
}

const loadPorts = () => {
  //模拟加载串口列表
  ports.value = ['/dev/ttyUSB0', '/dev/ttyACM0', '/dev/ttyAMA0']
  selectedPort.value = portSelect.value
}

const loadAudioGroups = () => {
  //模拟加载音频分组数据
  audioGroups.value = [
    {
      key: 'effects',
      items: [
        { fileName: 'beep.wav', name: 'Beep', duration: 0.5 },
        { fileName: 'boop.wav', name: 'Boop', duration: 0.8 }
      ]
    },
    {
      key: 'voices',
      items: [
        { fileName: 'hello.wav', name: 'Hello', duration: 1.2 },
        { fileName: 'hi.wav', name: 'Hi', duration: 1.0 }
      ]
    }
  ]
  
  //填充音频选项数组
  audioGroups.value.forEach(group => {
    group.items.forEach(item => {
      audioOptions.value.push(item.fileName)
    })
  })
}

const initTooltips = () => {
  //初始化Bootstrap工具提示
  if (window.jQuery && window.jQuery.fn.tooltip) {
    window.jQuery('[data-toggle="tooltip"]').tooltip()
  }
}

const updateProgress = (progressId, duration) => {
  //更新进度条
  const progressBar = document.getElementById(progressId)
  let width = 0
  const interval = setInterval(() => {
    if (width >= 100) {
      clearInterval(interval)
    } else {
      width += 100 / (duration * 10)
      progressBar.style.width = `${width}%`
      progressBar.setAttribute('aria-valuenow', width)
    }
  }, 100)
}

const cleanupResources = () => {
  //清理资源
  console.log('清理组件资源')
  //清除定时器、取消事件监听等
}

//暴露给模板的方法（Vue3 setup语法自动暴露，无需return）
</script>

<template>
    <div>
  <!-- Gamepad Information Overlay -->
  <div class="modal fade" id="gamepad-info" tabindex="-1" role="dialog">
    <div class="modal-dialog" role="document">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title" id="gamepad-title">游戏手柄支持</h5>
          <button type="button" class="close" data-dismiss="modal" aria-label="Close">
            <span aria-hidden="true">&times;</span>
          </button>
        </div>
        <div class="modal-body">
          瓦利机器人网页控制界面支持各类标准游戏手柄输入，例如 Xbox 或 PlayStation 手柄，可在所有主流浏览器中运行。
使用方法：先将游戏手柄连接至电脑，然后在网页控制界面打开的状态下，按下手柄任意按键即可完成适配。
          <br>
          <a href="/gamepad-layout.jpg" target="_blank">
            <img id="gamepad-layout" class="modal-image" :src="'gamepad-layout.jpg'">
          </a>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" data-dismiss="modal">关闭</button>
        </div>
      </div>
    </div>
  </div>

  <!-- Main Body Content -->
  <div class="container-fluid">
    <div class="row">
      <div class="col">
        <!-- Tab Buttons -->
        <div class="tabbable" id="tabs-937975">
          <ul class="nav nav-tabs row">
            <li class="nav-item col col-md-6 no-padding">
              <a class="nav-link tab-padding d-block d-md-none" href="#tab0" data-toggle="tab">
                <i class="fa fa-camera"></i>
                <div class="tab-text">摄像头</div>
              </a>
            </li>
            <li class="nav-item col no-padding">
              <a class="nav-link tab-padding active show" href="#tab1" data-toggle="tab">
                <i class="fa fa-gamepad"></i>
                <div class="tab-text">控制</div>
              </a>
            </li>
            <li class="nav-item col no-padding">
              <a class="nav-link tab-padding" href="#tab2" data-toggle="tab">
                <i class="fa fa-sliders-h"></i>
                <div class="tab-text">舵机</div>
              </a>
            </li>
            <li class="nav-item col no-padding">
              <a class="nav-link tab-padding" href="#tab3" data-toggle="tab">
                <i class="fa fa-play-circle"></i>
                <div class="tab-text">动画</div>
              </a>
            </li>
            <li class="nav-item col no-padding">
              <a class="nav-link tab-padding" href="#tab4" data-toggle="tab">
                <i class="fa fa-music"></i>
                <div class="tab-text">声音</div>
              </a>
            </li>
            <li class="nav-item col no-padding">
              <a class="nav-link tab-padding" href="#tab5" data-toggle="tab">
                <i class="fa fa-puzzle-piece"></i>
                <div class="tab-text">编程</div>
              </a>
            </li>
            <li class="nav-item col no-padding">
              <a id="settings-tab" class="nav-link tab-padding" href="#tab6" data-toggle="tab">
                <i class="fa fa-tools"></i>
                <div class="tab-text">设置</div>
              </a>
            </li>
          </ul>

          <!-- Tab Content -->
          <div class="tab-content row">
            <!-- Camera Stream -->
            <div class="tab-pane scroll-pane col-sm-12 col-md-6 d-md-block no-padding" id="tab0">
              <div class="media">
                <img 
                  id="stream" 
                  class="stream" 
                  :class="{ starting: cameraActive === 1 }"
                  :src="'/streamimage.jpg'"
                >
              </div>
              <div class="info-elements">
                <div class="info-area text-white">
                  状态:
                </div>
                <span @click="handleArduinoClick">
                  <a 
                    id="ardu-area" 
                    href="#conn-arduino" 
                    class="info-area text-white cursor-pointer"
                    :class="{ 'bg-success': connected === 1, 'bg-danger': connected !== 1 }"
                    :title="connected === 1 ? '已连接' : '未连接'"
                    data-toggle="tooltip" 
                    data-placement="top"
                  >
                    <i class="fa fa-robot"></i>
                    <div id="ardu-text" class="indicator-text">控制器</div>
                  </a>
                </span>
                <span data-toggle="modal" data-target="#gamepad-info">
                  <a 
                    id="cont-area" 
                    class="info-area bg-danger text-white cursor-pointer" 
                    title="未连接" 
                    data-toggle="tooltip" 
                    data-placement="top"
                  >
                    <i class="fa fa-gamepad"></i>
                    <div id="cont-text" class="indicator-text">游戏手柄</div>
                  </a>
                </span>
                <div 
                  id="batt-area" 
                  class="info-area bg-success text-white d-none" 
                  title="电池电量" 
                  data-toggle="tooltip" 
                  data-placement="top"
                >
                  <i id="batt-icon" class="fa fa-battery-full"></i>
                  <div id="batt-text" class="indicator-text">100%</div>
                </div>
              </div>
            </div>

            <!-- Robot Control -->
            <div class="tab-pane col-sm-12 col-md-6 active tabpane-padding" id="tab1">
              <div id="joytext" class="joystick-text">x: {{ joystickX }}, y: {{ joystickY }}</div>
              <div id="joystick" class="joystick">
                <div id="limit" class="limit border border-secondary rounded-circle">
                  <div id="base" class="base border border-secondary rounded-circle"></div>
                  <div id="stick" class="stick border border-dark rounded-circle" style="display: none;"></div>
                </div>
              </div>
            </div>

            <!-- Manual Servo Control -->
            <div class="tab-pane scroll-pane col-sm-12 col-md-6 tabpane-padding" id="tab2">
              <div class="container-fluid">
                <div class="row set-row">
                  <div class="col-xs-12 col-sm-4 set-text"><b>动画模式</b></div>
                  <div class="col-xs-12 col-sm-8">
                    <div class="btn-group btn-group-toggle" data-toggle="buttons">
                      <label class="btn btn-warning">
                        <input 
                          type="radio" 
                          name="options" 
                          id="auto-anime" 
                          @click="handleAnimeMode(1)"
                        > 自动
                      </label>
                      <label class="btn btn-warning active">
                        <input 
                          type="radio" 
                          name="options" 
                          id="manu-anime" 
                          checked 
                          @click="handleAnimeMode(0)"
                        > 手动
                      </label>
                    </div>
                  </div>
                </div>
                <hr/>
                
                <!-- 头部旋转 -->
                <div class="row set-row">
                  <div class="col-xs-12 col-sm-4 set-text">头部旋转</div>
                  <div class="col-xs-12 col-sm-8">
                    <input 
                      id="head-rotation" 
                      class="set-slide custom-range" 
                      type="range" 
                      min="0" 
                      max="100" 
                      step="1" 
                      value="50"
                      @focus="handleRangeFocus($event)"
                      @change="servoControl($event.target, 'G', $event.target.value)"
                    />
                  </div>
                </div>
                <hr/>
                
                <!-- 颈部控制 -->
                <div class="row set-row">
                  <div class="col-xs-12 col-sm-4 set-text">颈部上侧</div>
                  <div class="col-xs-12 col-sm-8">
                    <input 
                      id="neck-top" 
                      class="set-slide custom-range" 
                      type="range" 
                      min="0" 
                      max="100" 
                      step="1" 
                      value="50"
                      @focus="handleRangeFocus($event)"
                      @change="servoControl($event.target, 'T', $event.target.value)"
                    />
                  </div>
                </div>
                <div class="row set-row">
                  <div class="col-xs-12 col-sm-4 set-text">颈部下侧</div>
                  <div class="col-xs-12 col-sm-8">
                    <input 
                      id="neck-bottom" 
                      class="set-slide custom-range" 
                      type="range" 
                      min="0" 
                      max="100" 
                      step="1" 
                      value="50"
                      @focus="handleRangeFocus($event)"
                      @change="servoControl($event.target, 'B', $event.target.value)"
                    />
                  </div>
                </div>
                <div class="row set-row">
                  <div class="col-xs-12 col-sm-4 set-text">颈部预设</div>
                  <div class="col-xs-12 col-sm-8">
                    <div class="btn-group" role="group">
                      <button 
                        type="button" 
                        id="head-up" 
                        class="btn btn-primary"
                        @click="servoPresets($event.target, 'head-up', 'f')"
                      >
                        头部向上
                      </button>
                      <button 
                        type="button" 
                        id="head-neutral" 
                        class="btn btn-primary"
                        @click="servoPresets($event.target, 'head-neutral', 'g')"
                      >
                        中立位
                      </button>
                      <button 
                        type="button" 
                        id="head-down" 
                        class="btn btn-primary"
                        @click="servoPresets($event.target, 'head-down', 'h')"
                      >
                        向下
                      </button>
                    </div>
                  </div>
                </div>
                <hr/>
                
                <!-- 手臂控制 -->
                <div class="row set-row">
                  <div class="col-xs-12 col-sm-4 set-text">左臂</div>
                  <div class="col-xs-12 col-sm-8">
                    <input 
                      id="arm-left" 
                      class="set-slide custom-range" 
                      type="range" 
                      min="0" 
                      max="100" 
                      step="1" 
                      value="50"
                      @focus="handleRangeFocus($event)"
                      @change="servoControl($event.target, 'L', $event.target.value)"
                    />
                  </div>
                </div>
                <div class="row set-row">
                  <div class="col-xs-12 col-sm-4 set-text">右臂</div>
                  <div class="col-xs-12 col-sm-8">
                    <input 
                      id="arm-right" 
                      class="set-slide custom-range" 
                      type="range" 
                      min="0" 
                      max="100" 
                      step="1" 
                      value="50"
                      @focus="handleRangeFocus($event)"
                      @change="servoControl($event.target, 'R', $event.target.value)"
                    />
                  </div>
                </div>
                <div class="row set-row">
                  <div class="col-xs-12 col-sm-4 set-text">手臂预设</div>
                  <div class="col-xs-12 col-sm-8">
                    <div class="btn-group" role="group">
                      <button 
                        type="button" 
                        id="arms-left" 
                        class="btn btn-primary"
                        @click="servoPresets($event.target, 'arms-left', 'm')"
                      >
                        向左
                      </button>
                      <button 
                        type="button" 
                        id="arms-neutral" 
                        class="btn btn-primary"
                        @click="servoPresets($event.target, 'arms-neutral', 'n')"
                      >
                        中立位
                      </button>
                      <button 
                        type="button" 
                        id="arms-right" 
                        class="btn btn-primary"
                        @click="servoPresets($event.target, 'arms-right', 'b')"
                      >
                        向右
                      </button>
                    </div>
                  </div>
                </div>
                <hr/>
                
                <!-- 眼睛控制 -->
                <div class="row set-row">
                  <div class="col-xs-12 col-sm-4 set-text">左眼</div>
                  <div class="col-xs-12 col-sm-8">
                    <input 
                      id="eye-left" 
                      class="set-slide custom-range" 
                      type="range" 
                      min="0" 
                      max="100" 
                      step="1" 
                      value="50"
                      @focus="handleRangeFocus($event)"
                      @change="servoControl($event.target, 'E', $event.target.value)"
                    />
                  </div>
                </div>
                <div class="row set-row">
                  <div class="col-xs-12 col-sm-4 set-text">右眼</div>
                  <div class="col-xs-12 col-sm-8">
                    <input 
                      id="eye-right" 
                      class="set-slide custom-range" 
                      type="range" 
                      min="0" 
                      max="100" 
                      step="1" 
                      value="50"
                      @focus="handleRangeFocus($event)"
                      @change="servoControl($event.target, 'U', $event.target.value)"
                    />
                  </div>
                </div>
                <div class="row set-row">
                  <div class="col-xs-12 col-sm-4 set-text">眼睛预设</div>
                  <div class="col-xs-12 col-sm-8">
                    <div class="btn-group" role="group">
                      <button 
                        type="button" 
                        id="eyes-left" 
                        class="btn btn-primary"
                        @click="servoPresets($event.target, 'eyes-left', 'j')"
                      >
                        向左看
                      </button>
                      <button 
                        type="button" 
                        id="eyes-neutral" 
                        class="btn btn-primary"
                        @click="servoPresets($event.target, 'eyes-neutral', 'k')"
                      >
                        正视
                      </button>
                      <button 
                        type="button" 
                        id="eyes-sad" 
                        class="btn btn-primary"
                        @click="servoPresets($event.target, 'eyes-sad', 'i')"
                      >
                        悲伤
                      </button>
                      <button 
                        type="button"  
                        id="eyes-right" 
                        class="btn btn-primary"
                        @click="servoPresets($event.target, 'eyes-right', 'l')"
                      >
                        向右看
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Animation Selection -->
            <div class="tab-pane scroll-pane col-sm-12 col-md-6 tabpane-padding" id="tab3">
              <div class="container-fluid">
                <!-- Progress Bar Template -->
                <div class="progress">
                  <div 
                    id="anime-progress" 
                    class="progress-bar progress-bar-striped notransition" 
                    style="width:0%" 
                    role="progressbar" 
                    aria-valuenow="0" 
                    aria-valuemin="0" 
                    aria-valuemax="100"
                  ></div>
                </div>
                <br>
                <!-- List Group Template -->
                <div class="list-group" id="anime-accordion">
                  <div class="card">
                    <a href="#all-animations" data-toggle="collapse" class="card-header justify-content-between text-muted">
                      所有动画 
                      <span class="badge badge-info badge-pill">3</span>
                    </a>
                    <div class="collapse show" id="all-animations" data-parent="#anime-accordion">
                      <a 
                        href="#" 
                        class="list-group-item list-group-item-action" 
                        file-name="0" 
                        file-length="1.4"
                        @click="anime(0, 1.4)"
                      >
                        重置舵机位置 <i class="entry-time">&nbsp; | &nbsp; 1.4秒</i>
                      </a>
                      <a 
                        href="#" 
                        class="list-group-item list-group-item-action" 
                        file-name="1" 
                        file-length="8.6"
                        @click="anime(1, 8.6)"
                      >
                        启动序列 <i class="entry-time">&nbsp; | &nbsp; 8.6秒</i>
                      </a>
                      <a 
                        href="#" 
                        class="list-group-item list-group-item-action" 
                        file-name="2" 
                        file-length="18"
                        @click="anime(2, 18)"
                      >
                        好奇动作序列 <i class="entry-time">&nbsp; | &nbsp; 18秒</i>
                      </a>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Sound Selection -->
            <div class="tab-pane scroll-pane col-sm-12 col-md-6 tabpane-padding" id="tab4">
              <div class="container-fluid">
                <!-- Progress Bar Template -->
                <div class="progress">
                  <div 
                    id="audio-progress" 
                    class="progress-bar progress-bar-striped notransition" 
                    style="width:0%" 
                    role="progressbar" 
                    aria-valuenow="0" 
                    aria-valuemin="0" 
                    aria-valuemax="100"
                  ></div>
                </div>
                <br>
                <!-- List Group Template -->
                <div class="list-group" id="audio-accordion">
                  <!-- 音频分组会通过JS动态渲染 -->
                  <div v-for="(group, index) in audioGroups" :key="index" class="card">
                    <a :href="`#${group.key.toLowerCase()}-audio`" data-toggle="collapse" class="card-header justify-content-between text-muted">
                      {{ group.key === 'effects' ? '音效' : '语音' }} 
                      <span class="badge badge-info badge-pill">{{ group.items.length }}</span>
                    </a>
                    <div :id="`${group.key.toLowerCase()}-audio`" class="collapse" data-parent="#audio-accordion">	
                      <a 
                        href="#" 
                        v-for="(item, idx) in group.items" 
                        :key="idx"
                        class="list-group-item list-group-item-action" 
                        :file-name="item.fileName" 
                        :file-length="item.duration"
                        @click="playAudio(item.fileName, item.duration)"
                      >
                        {{ item.name }} <i class="entry-time">&nbsp; | &nbsp;{{ item.duration }}秒</i>
                      </a>
                    </div>
                  </div>
                </div>
                <!-- Text to Speech -->
                <hr/>
                <div class="row set-row ">
                  <div class="col-xs-12 set-text">&nbsp;文字转语音</div>
                </div>
                <div class="row set-row">
                  <div class="input-group col-xs-12 col-sm-10">
                    <input type="text" class="form-control" v-model="ttsText" id="tts_text">
                    <div class="input-group-append">
                      <button class="btn btn-outline-info" type="button" @click="playTTS(ttsText)">朗读</button>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Automation -->
            <div class="tab-pane scroll-pane col-sm-12 col-md-6 tabpane-padding" data-toggle="tab" id="tab5">
              <div class="container-fluid">
                <div class="row set-row ">
                  <div class="btn-group" role="group" aria-label="Blockly Bar">
                    <button id="run" type="button" class="btn btn-success" @click="runCode()">
                      <i class="far fa-play-circle"></i>
                      <div class="indicator-text">运行!</div>
                    </button>
                    <button id="stop" type="button" class="btn btn-danger" @click="stopCode()">
                      <i class="far fa-stop-circle"></i>
                      <div class="indicator-text">停止</div>
                    </button>
                    <button id="save" type="button" class="btn btn-primary" @click="saveFile()">
                      <i class="far fa-save"></i>
                      <div class="indicator-text">保存</div>
                    </button>
                    <button id="load" type="button" class="btn btn-info" @click="document.getElementById('customFile').click()">
                      <i class="fas fa-file-upload"></i>
                      <div class="indicator-text">加载</div>
                    </button>
                  </div>
                </div>
                <div class="row set-row ">
                  <div id="blocklyDiv" style="height: 600px; width: 1200px;"></div>
                </div>
              </div>
            </div>

            <!-- Settings -->
            <div class="tab-pane scroll-pane col-sm-12 col-md-6 tabpane-padding" data-toggle="tab" id="tab6">
              <div class="container-fluid">
                <div class="row set-row d-none">
                  <div class="col-xs-12 col-sm-4 set-text">声音模式</div>
                  <div class="col-xs-12 col-sm-8">
                    <div class="btn-group btn-group-toggle" data-toggle="buttons">
                      <label class="btn btn-primary">
                        <input 
                          type="radio" 
                          name="options" 
                          id="auto-sound" 
                          @click="sendSettings('soundMode', 1)"
                        > 自动
                      </label>
                      <label class="btn btn-primary active">
                        <input 
                          type="radio" 
                          name="options" 
                          id="manu-sound" 
                          autocomplete="off" 
                          checked 
                          @click="sendSettings('soundMode', 0)"
                        > 手动
                      </label>
                    </div>
                  </div>
                </div>
                <div class="row set-row">
                  <div class="col-xs-12 col-sm-4 set-text">声音大小</div>
                  <div class="col-xs-12 col-sm-8">
                    <input 
                      id="volume" 
                      class="set-slide custom-range" 
                      type="range" 
                      min="0" 
                      max="10" 
                      step="1" 
                      value="8"
                      @change="sendSettings('volume', $event.target.value)"
                    />
                  </div>
                </div>
                <hr/>
                <div class="row set-row">
                  <div class="col-xs-12 col-sm-4 set-text">电机死区（Deadzone）</div>
                  <div class="col-xs-12 col-sm-8">
                    <input 
                      type="number" 
                      min="0" 
                      max="250" 
                      value="190" 
                      class="form-control set-num is-valid" 
                      id="motor-offset"
                      v-model="motorOffset"
                    >
                  </div>
                </div>
                <div class="row set-row">
                  <div class="col-xs-12 col-sm-4 set-text">转向微调（Steering）</div>
                  <div class="col-xs-12 col-sm-8">
                    <input 
                      type="number" 
                      min="-100" 
                      max="100" 
                      value="0" 
                      class="form-control set-num is-valid" 
                      id="steer-offset"
                      v-model="steerOffset"
                    >
                  </div>
                </div>
                <div class="row set-row">
                  <div class="col-xs-12 col-sm-4 set-text"></div>
                  <div class="col-xs-12 col-sm-8">
                    <button id="num-update" type="button" class="btn btn-outline-info" @click="updateOffsets()">立即更新参数</button>
                  </div>
                </div>
                <hr/>
                <div class="row set-row">
                  <div class="col-xs-12 col-sm-4 set-text">选择端口</div>
                  <div class="input-group col-xs-12 col-sm-8">
                    <select 
                      class="custom-select set-num" 
                      id="port-select"
                      v-model="selectedPort"
                    >
                      <option v-if="!ports.length" disabled selected>未找到设备!</option>
                      <option 
                        v-for="(port, idx) in ports" 
                        :key="idx"
                        :value="idx"
                        :selected="idx === portSelect"
                      >
                        {{ port }}
                      </option>
                    </select>
                    <div class="input-group-append">
                      <button 
                        class="btn btn-outline-info" 
                        type="button" 
                        @click="updateSerialList(true)"
                      >
                        刷新
                      </button>
                    </div>
                  </div>
                </div>
                <div class="row set-row">
                  <div class="col-xs-12 col-sm-4 set-text">Arduino连接</div>
                  <div class="col-xs-12 col-sm-8">
                    <button 
                      id="conn-arduino" 
                      type="button" 
                      class="btn"
                      :class="{
                        'btn-outline-danger': ports.length && connected === 1,
                        'btn-outline-info': ports.length && connected !== 1,
                        'btn-outline-secondary disabled': !ports.length
                      }"
                      @click="arduinoConnect($event.target)"
                      :disabled="!ports.length"
                    >
                      {{ connected === 1 ? '断开连接' : '重新连接' }}
                    </button>
                  </div>
                </div>
                <hr/>
                <div class="row set-row">
                  <div class="col-xs-12 col-sm-4 set-text">摄像头推流服务</div>
                  <div class="col-xs-12 col-sm-8">
                    <button 
                      id="conn-streamer" 
                      type="button" 
                      class="btn btn-outline-info"
                      @click="sendSettings('streamer', 1)"
                    >
                      重启服务
                    </button>
                  </div>
                </div>
                <div class="row set-row">
                  <div class="col-xs-12 col-sm-4 set-text">界面管理</div>
                  <div class="col-xs-12 col-sm-8">
                    <button 
                      id="restart" 
                      type="button" 
                      class="btn btn-outline-danger"
                      @click="sendSettings('restart', 1)"
                    >
                      重启网页界面
                    </button>
                  </div>
                </div>
                <div class="row set-row">
                  <div class="col-xs-12 col-sm-4 set-text">电源管理</div>
                  <div class="col-xs-12 col-sm-8">
                    <button 
                      id="shutdown" 
                      type="button" 
                      class="btn btn-outline-danger"
                      @click="sendSettings('shutdown', 1)"
                    >
                      关闭树莓派!
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div class="row">
      <div class="d-sm-none d-md-block col-md-6"></div>
      <div class="col-sm-12 col-md-6 alert-col">
        <div id="alert-space" class="alert-area"></div>
      </div>
    </div>
  </div>

  <!-- load file element from the code tab -->
  <input type="file" class="custom-file-input" id="customFile" hidden @change="handleFileLoad">
</div>
</template>

<style>
    .modal-title{
	    color: #000 !important; 
	    font-weight: 700;
	    font-size: 18px;
    }
    .modal-body{
        color: #000 !important; 
	    font-weight: 700;
	    font-size: 18px;
    }
    .info-area{
        color: rgb(46, 25, 25) !important; 
	    font-weight: 700;
	    font-size: 18px;
    }
    .joystick-text{
        color: rgb(160, 16, 16);
        font-weight: 700;
	    font-size: 22px;
    }
    .row{
        color: rgb(6, 110, 32);
    }
    #run,#stop,#save,#load{
        height: 40px
    }
    #num-update,#restart,#shutdown,#conn-streamer,#conn-arduino{
        width: 125px;
    }
</style>