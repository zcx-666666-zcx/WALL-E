<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { GetMachineListApi, GetDeviceNetworkStatusApi } from '@/api/users'
import CameraPanel from './components/CameraPanel.vue'
import ControlPanel from './components/ControlPanel.vue'
import ServoPanel from './components/ServoPanel.vue'
import AnimationPanel from './components/AnimationPanel.vue'
import AudioPanel from './components/AudioPanel.vue'
import SettingsPanel from './components/SettingsPanel.vue'
import { getRobotHttpPort } from '@/utils/systemConfig'
import { selectPreferredMachine } from './machineSelection.mjs'
import { refreshDeviceNetworkStatuses } from '@/utils/deviceNetworkStatus.mjs'

const tabs = ['遥控','舵机','动画','音效','设置']
const currentTab = ref('遥控')

const machines = ref([])
const selectedMachine = ref(null)
const loadingMachines = ref(false)
const robotHttpPort = getRobotHttpPort()
const NETWORK_REFRESH_MS = 10000
let networkRefreshTimer = null

async function refreshNetworkStatuses() {
  const selectedId = selectedMachine.value?.id
  machines.value = await refreshDeviceNetworkStatuses(
    machines.value,
    GetDeviceNetworkStatusApi
  )
  selectedMachine.value = machines.value.find(machine => machine.id === selectedId)
    || selectPreferredMachine(machines.value)
}

onMounted(async () => {
  const userId = localStorage.getItem('Id')
  if (!userId) return
  loadingMachines.value = true
  try {
    const res = await GetMachineListApi(userId)
    if (res?.code === 1 && res.data?.rows?.length > 0) {
      machines.value = res.data.rows
      selectedMachine.value = selectPreferredMachine(machines.value)
      await refreshNetworkStatuses()
    }
  } catch (e) {
    // silently fail
  } finally {
    loadingMachines.value = false
  }
  networkRefreshTimer = window.setInterval(refreshNetworkStatuses, NETWORK_REFRESH_MS)
})
onBeforeUnmount(() => window.clearInterval(networkRefreshTimer))
</script>

<template>
  <div class="drive-root">

    <div class="page-header">
      <div class="page-header-left">
        <div class="page-title-icon">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <rect x="5" y="2" width="6" height="12" rx="2" stroke="white" stroke-width="1.4"/>
            <circle cx="8" cy="7.5" r="2" stroke="white" stroke-width="1.3"/>
            <path d="M5.5 13.5h5" stroke="white" stroke-width="1.3" stroke-linecap="round"/>
          </svg>
        </div>
        <div>
          <div class="page-title">WALL·E 控制台</div>
          <div class="page-sub">远程控制与调试面板</div>
        </div>
      </div>

      <div class="device-picker">
        <span class="device-picker-label">当前设备</span>
        <el-select
          v-model="selectedMachine"
          value-key="id"
          placeholder="选择机器人"
          size="small"
          :loading="loadingMachines"
          class="device-select"
        >
          <el-option
            v-for="m in machines"
            :key="m.id"
            :label="m.machines"
            :value="m"
          />
        </el-select>
        <span v-if="selectedMachine?.robotIp" class="device-ip" :class="{ offline: !selectedMachine.networkStatus?.online }">
          <span class="status-dot" :class="{ online: selectedMachine.networkStatus?.online }"></span>
          {{ selectedMachine.robotIp }}:{{ robotHttpPort }}
        </span>
        <span v-else-if="selectedMachine" class="device-ip no-ip">未配置 IP</span>
      </div>
    </div>

    <div class="tabs-bar">
      <button
        v-for="t in tabs" :key="t"
        class="tab-btn"
        :class="{ active: currentTab === t }"
        @click="currentTab = t"
      >{{ t }}</button>
    </div>

    <div class="panel-area">
      <div v-if="currentTab==='遥控'" class="drive-layout">
        <div class="drive-video"><CameraPanel :machine="selectedMachine" /></div>
        <div class="drive-joystick"><ControlPanel :machine="selectedMachine" /></div>
      </div>
      <ServoPanel     v-if="currentTab==='舵机'"   :machine="selectedMachine" />
      <AnimationPanel v-if="currentTab==='动画'"   :machine="selectedMachine" />
      <AudioPanel     v-if="currentTab==='音效'"   :machine="selectedMachine" />
      <SettingsPanel  v-if="currentTab==='设置'"   :machine="selectedMachine" />
    </div>

  </div>
</template>

<style scoped>
.drive-root {
  width: 100%; height: 100%;
  padding: 20px 24px; box-sizing: border-box;
  display: flex; flex-direction: column; gap: 16px;
  overflow: hidden;
  font-family: "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
}

.page-header { display: flex; align-items: center; justify-content: space-between; flex-shrink: 0; }
.page-header-left { display: flex; align-items: center; gap: 12px; }
.page-title-icon {
  width: 40px; height: 40px; border-radius: 12px;
  background: linear-gradient(135deg, #FF9A76, #FF6040);
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 4px 12px rgba(255,96,64,0.28); flex-shrink: 0;
}
.page-title { font-size: 18px; font-weight: 700; color: #3A2010; letter-spacing: 0.01em; }
.page-sub { font-size: 12px; color: #B09080; margin-top: 2px; }

.device-picker { display: flex; align-items: center; gap: 10px; }
.device-picker-label { font-size: 12.5px; font-weight: 600; color: #8A5040; }
.device-select { width: 180px; }
.device-ip {
  font-size: 11.5px; color: #5AB060; font-family: monospace;
  background: #F0FFF2; border: 1px solid #C8E6C9;
  border-radius: 6px; padding: 4px 10px;
}
.device-ip.no-ip {
  color: #EF6C00; background: #FFF3E0; border-color: #FFCC80;
}
.device-ip.offline { color: #8A6F62; background: #F6F2F0; border-color: #DDD2CC; }
.status-dot {
  display: inline-block; width: 7px; height: 7px; margin-right: 5px;
  border-radius: 50%; background: #B8AAA2;
}
.status-dot.online { background: #2FA66A; }

/* Tabs */
.tabs-bar {
  display: flex; gap: 6px; flex-shrink: 0;
}
.tab-btn {
  height: 38px; padding: 0 20px;
  background: #FFFFFF; color: #7A5040;
  border: 1px solid rgba(255,160,120,0.2);
  border-radius: 10px; font-size: 13px; font-weight: 600;
  font-family: inherit; cursor: pointer;
  transition: all 0.2s cubic-bezier(0.34, 1.4, 0.64, 1);
}
.tab-btn:hover { background: #FFF0E8; color: #D06030; border-color: rgba(255,140,80,0.3); transform: translateY(-1px); }
.tab-btn.active {
  background: linear-gradient(135deg, #FF9A76, #FF6040);
  color: white; border-color: transparent;
  box-shadow: 0 3px 10px rgba(255,96,64,0.28);
}

.panel-area {
  flex: 1; min-height: 0; overflow-y: auto;
  background: #FFFFFF; border-radius: 16px;
  border: 1px solid rgba(255,160,120,0.12);
  box-shadow: 0 2px 12px rgba(200,90,50,0.05);
  padding: 20px;
}

.drive-layout {
  display: flex; gap: 16px; height: 100%;
}
.drive-video {
  flex: 1; min-width: 0; display: flex; align-items: center; justify-content: center;
  background: #1A1A1A; border-radius: 12px; overflow: hidden;
}
.drive-video :deep(.camera-panel) {
  width: 100%; height: 100%; display: flex; flex-direction: column; align-items: center; justify-content: center;
}
.drive-video :deep(.video-stream) {
  width: 100%; max-width: 100%; border-radius: 0; border: none; box-shadow: none;
}
.drive-video :deep(h3) { display: none; }
.drive-joystick {
  width: 260px; flex-shrink: 0;
  display: flex; align-items: center; justify-content: center;
  border-left: 1px solid rgba(255,160,120,0.08); padding-left: 16px;
}
</style>
