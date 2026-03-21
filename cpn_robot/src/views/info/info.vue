<script setup>
import { ref } from 'vue'

let show = ref(false)
let info = ref('歪比歪比，歪比巴卜。rua哇rou！')

function Element() {
  show.value = true
  info.value =
    '事件提醒：<br><br>应用场景：通过在小程序或网页中添加事件，让机器人在指定时间为用户进行语音提示，避免用户遗忘事件，可起到记事本或闹钟的作用<br><br>使用方法：在网页端“事件管理”或微信小程序“事件”中，查看已设置的事件，并对其进行管理，如新增事件或删除事件等操作<br><br>注意事项：<br>事件名称--在小程序和网页中显示<br>事件优先级--当同一时间有多个事件需要提醒，将按照优先级从高到低依次提醒，因此不建议在同一时间设置大于3个事件<br>事件描述--机器人实际触发语音向用户提醒的内容<br>绑定设备--设备号为?????，需要把事件绑定给一个设备（即机器人）才能生效<br><br>您可在“命令查询”中，查看事件是否被成功触发'
}
function Agent() {
  show.value = true
  info.value = 'AI陪聊：'
}
function Safe() {
  show.value = true
  info.value = '安全监测内容'
}
function Video() {
  show.value = true
  info.value = '远程通话内容'
}
function Drive() {
  show.value = true
  info.value = '远程遥控内容'
}
function no() {
  show.value = true
  info.value = '敬请期待'
}
</script>

<template>
  <div class="help-container">
    <!-- 左侧菜单 -->
    <div class="sidebar">
      <div class="menu-item" @click="Element">事件提醒</div>
      <div class="menu-item" @click="Agent">智能陪聊</div>
      <div class="menu-item" @click="Safe">安全监测</div>
      <div class="menu-item" @click="Video">远程通话</div>
      <div class="menu-item" @click="Drive">远程遥控</div>
      <div class="menu-item" @click="no">暂未添加</div>
    </div>

    <!-- 右侧内容 -->
    <div class="content" v-if="show" v-html="info"></div>
  </div>
</template>

<style scoped>

.help-container {
  width: 100%;
  height: 100%;
  display: flex;
  background: linear-gradient(135deg, #FFF8F3, #FFEFE6);
  overflow: hidden;
}

/* ===== 左侧菜单 ===== */
.sidebar {
  width: 20%;
  background: #FFFFFF;
  padding: 20px 14px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  box-shadow: 4px 0 20px rgba(255, 138, 101, 0.08);
  border-radius: 0 16px 16px 0;
}

/* 菜单按钮（重点改造） */
.menu-item {
  width: 100%;
  height: 10%;

  background: #FFF3EE;
  color: #E64A19;

  font-size: 25px;
  font-weight: 600;

  border-radius: 10px;
  display: flex;
  align-items: center;
  padding-left: 20px;

  cursor: pointer;
  transition: all 0.25s ease;
  border: 1px solid #FFE0D6;
}

/* hover效果 */
.menu-item:hover {
  background: #FFE0D6;
  transform: translateX(6px);
}

/* ===== 内容区 ===== */
.content {
  width: 80%;
  padding: 30px 40px;

  background: #FFFFFF;
  margin: 16px;
  border-radius: 20px;

  font-size: 18px;
  color: #4E342E;
  line-height: 1.8;

  overflow-y: auto;

  box-shadow: 0 10px 30px rgba(255, 138, 101, 0.08);
}

/* ===== 内容优化（让文字更像说明文档） ===== */
.content br {
  margin-bottom: 10px;
}

/* 标题感（自动增强） */
.content::first-line {
  font-size: 23px;
  font-weight: 700;
  color: #E64A19;
}

/* 滚动条优化 */
.content::-webkit-scrollbar {
  width: 6px;
}

.content::-webkit-scrollbar-thumb {
  background: #FFB199;
  border-radius: 3px;
}
</style>