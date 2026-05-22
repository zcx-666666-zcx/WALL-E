<template>
  <div class="settings-panel">
    <h3>机器人设置</h3>

    <div v-if="!machine" class="no-device">请先在顶部选择一个机器人设备</div>
    <div v-else-if="!machine.robotIp" class="no-device warn">当前设备未配置 IP 地址</div>

    <template v-else>
      <div class="setting-group">
        <h4>运行模式</h4>
        <div class="mode-btns">
          <button :class="{ active: currentMode === 'patrol' }" @click="setMode('streamer', 'Active')">
            <span class="mode-icon">👁️</span>
            <span>巡线模式</span>
          </button>
          <button :class="{ active: currentMode === 'control' }" @click="setMode('streamer', 'Offline')">
            <span class="mode-icon">🎮</span>
            <span>遥控模式</span>
          </button>
        </div>
      </div>

      <div class="setting-group">
        <h4>系统操作</h4>
        <div class="sys-btns">
          <button class="btn-restart" @click="sendCmd('restart')">🔄 重启服务</button>
          <button class="btn-shutdown" @click="sendCmd('shutdown')">⏻ 关机</button>
        </div>
        <p class="hint">关机后需手动重新上电机器人</p>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { RobotSettingsApi } from '@/api/users'

const props = defineProps({
  machine: { type: Object, default: null }
})

const currentMode = ref('control')

function setMode(type, value) {
  currentMode.value = value === 'Active' ? 'patrol' : 'control'
  RobotSettingsApi({
    machineId: props.machine.id,
    type,
    value
  }).catch(() => {})
}

function sendCmd(cmd) {
  if (cmd === 'shutdown' && !confirm('确定要关闭机器人吗？关机后需手动重新上电。')) return
  RobotSettingsApi({
    machineId: props.machine.id,
    type: cmd,
    value: ''
  }).catch(() => {})
}
</script>

<style scoped>
h3 { margin-bottom: 14px; }
h4 { font-size: 13px; color: #6A4030; margin-bottom: 10px; }

.no-device { padding: 40px 20px; color: #B09080; font-size: 14px; text-align: center; }
.no-device.warn { color: #EF6C00; }

.setting-group {
  margin-bottom: 24px; padding: 16px;
  background: #FFFAF7; border: 1px solid rgba(255,160,120,0.12);
  border-radius: 14px;
}

.mode-btns { display: flex; gap: 10px; }
.mode-btns button {
  flex: 1; height: 60px; border-radius: 12px;
  border: 2px solid rgba(255,160,120,0.2);
  background: #FFFFFF;
  display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 2px;
  cursor: pointer; font-family: inherit; font-size: 13px; font-weight: 600; color: #7A5040;
  transition: all 0.2s;
}
.mode-btns button:hover { border-color: rgba(255,140,80,0.4); }
.mode-btns button.active { border-color: #FF6040; background: #FFF5F0; color: #D06030; }
.mode-icon { font-size: 20px; }

.sys-btns { display: flex; gap: 10px; }
.btn-restart {
  flex: 1; height: 40px; border-radius: 10px;
  border: 1px solid rgba(255,160,120,0.25);
  background: #FFF5F0; color: #D06030;
  font-size: 13px; font-weight: 600; font-family: inherit;
  cursor: pointer; transition: all 0.15s;
}
.btn-restart:hover { background: #FFE8DC; }
.btn-shutdown {
  flex: 1; height: 40px; border-radius: 10px;
  border: none; background: #FF6040; color: white;
  font-size: 13px; font-weight: 600; font-family: inherit;
  cursor: pointer; transition: all 0.15s;
}
.btn-shutdown:hover { background: #E8451A; }

.hint { font-size: 11px; color: #B09080; margin-top: 10px; }
</style>
