<script setup>
import { ref } from 'vue'

const notiSwitch = ref(true)
const autoSwitch = ref(false)
const darkMode = ref(false)
const voiceNotify = ref(true)

const volume = ref(80)
const voiceType = ref('温馨女声')

//模拟方法
function handleLogout() {
  if (confirm('确定要退出登录吗？')) {
    alert('已退出登录')
  }
}

function saveSetting() {
  alert('设置已保存！')
}

function clearCache() {
  alert('缓存已清除')
}

function about() {
  alert('智能陪伴机器人 v1.0\n❤️ 感谢使用')
}

function feedback() {
  alert('反馈功能即将上线～')
}
</script>

<template>
  <div class="setting-container">
    <div class="header">
      <h1>系统设置</h1>
      <p>个性化配置你的智能陪伴机器人</p>
    </div>

    <!-- 基础设置 -->
    <div class="setting-card">
      <div class="card-title">基础设置</div>
      <div class="item">
        <div>
          <label>音量调节</label>
          <div class="tip">调节机器人提示音大小</div>
        </div>
        <input type="range" v-model="volume" min="0" max="100" class="slider" />
      </div>
      <div class="item">
        <div>
          <label>语音类型</label>
          <div class="tip">选择机器人播报音色</div>
        </div>
        <select v-model="voiceType" class="select">
          <option>温馨女声</option>
          <option>沉稳男声</option>
          <option>可爱童声</option>
          <option>变形金刚</option>
          <option>猫meme</option>
          <option>曼波</option>
        </select>
      </div>
    </div>

    <!-- 提醒设置 -->
    <div class="setting-card">
      <div class="card-title">消息与提醒</div>
      <div class="item">
        <div>
          <label>事件提醒</label>
          <div class="tip">开启后机器人会按时语音提醒</div>
        </div>
        <div class="switch" :class="{ on: notiSwitch }" @click="notiSwitch = !notiSwitch">
          <div class="circle"></div>
        </div>
      </div>
      <div class="item">
        <div>
          <label>开机自动播报</label>
          <div class="tip">开机后自动播报时间与天气</div>
        </div>
        <div class="switch" :class="{ on: autoSwitch }" @click="autoSwitch = !autoSwitch">
          <div class="circle"></div>
        </div>
      </div>
      <div class="item">
        <div>
          <label>操作语音反馈</label>
          <div class="tip">按钮/操作成功时语音提示</div>
        </div>
        <div class="switch" :class="{ on: voiceNotify }" @click="voiceNotify = !voiceNotify">
          <div class="circle"></div>
        </div>
      </div>
    </div>

    <!-- 高级设置 -->
    <div class="setting-card">
      <div class="card-title">高级设置</div>
      <div class="item" @click="clearCache">
        <div>
          <label>清除缓存</label>
          <div class="tip">释放存储空间</div>
        </div>
        <span>→</span>
      </div>
      <div class="item" @click="feedback">
        <div>
          <label>意见反馈</label>
          <div class="tip">帮助我们优化产品</div>
        </div>
        <span>→</span>
      </div>
      <div class="item" @click="about">
        <div>
          <label>关于产品</label>
          <div class="tip">查看版本与信息</div>
        </div>
        <span>→</span>
      </div>
    </div>

    <!-- 账号设置 -->
    <div class="setting-card">
      <div class="card-title">账号管理</div>
      <div class="item" style="color: #e57373; font-weight: 600" @click="handleLogout">
        <div>
          <label>退出登录</label>
          <div class="tip">退出当前账号，返回登录页</div>
        </div>
        <span>→</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.setting-container {
  width: 100%;
  height: 100vh;
  background: #fdf6f0;
  padding: 4vh 4vw;
  box-sizing: border-box;
  overflow-y: auto; /* 允许滚动 */
  overflow-x: hidden;
  display: flex;
  flex-direction: column;
  gap: 2vh;
  padding-bottom: 12vh; /* 最底部留出空间，确保能看到退出登录 */
}

/* 隐藏滚动条但保留滚动功能 */
.setting-container::-webkit-scrollbar {
  width: 0;
  height: 0;
}

.header {
  margin-bottom: 1vh;
}

.header h1 {
  font-size: clamp(24px, 4vw, 36px);
  color: #855ce5;
  margin: 0;
}

.header p {
  font-size: clamp(14px, 2vw, 18px);
  color: #795548;
  margin: 6px 0 0 0;
}

.setting-card {
  background: white;
  border-radius: 16px;
  padding: 3vh 4vw;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.card-title {
  font-size: clamp(16px, 2.5vw, 20px);
  font-weight: 600;
  color: #5d4037;
  margin-bottom: 2vh;
}

.item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 2vh 0;
  border-bottom: 1px solid #f0e9e4;
  cursor: pointer;
}

.item:last-child {
  border-bottom: none;
}

.item label {
  font-size: clamp(15px, 2.2vw, 18px);
  color: #333;
  font-weight: 500;
}

.item .tip {
  font-size: 12px;
  color: #999;
  margin-top: 4px;
}

.slider {
  width: 120px;
  height: 6px;
  appearance: none;
  background: #e0d5d0;
  border-radius: 100px;
  outline: none;
}

.slider::-webkit-slider-thumb {
  appearance: none;
  width: 16px;
  height: 16px;
  background: #a888e6;
  border-radius: 50%;
}

.select {
  padding: 8px 12px;
  border: 1px solid #d1c7c2;
  border-radius: 8px;
  outline: none;
  font-size: 14px;
}

.switch {
  width: 50px;
  height: 28px;
  background: #ccc;
  border-radius: 100px;
  position: relative;
  transition: 0.3s;
}

.switch.on {
  background: #a888e6;
}

.circle {
  width: 22px;
  height: 22px;
  background: white;
  border-radius: 50%;
  position: absolute;
  top: 3px;
  left: 3px;
  transition: 0.3s;
}

.switch.on .circle {
  left: 25px;
}
.save-btn:hover {
  background: #724bd1;
}
</style>