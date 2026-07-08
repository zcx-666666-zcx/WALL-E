<template>
  <div class="audio-panel">
    <h3>音效与语音</h3>

    <div v-if="!machine" class="no-device">请先在顶部选择一个机器人设备</div>
    <div v-else-if="!machine.robotIp" class="no-device warn">当前设备未配置 IP 地址</div>

    <template v-else>
      <h4>音效列表</h4>
      <div v-for="audio in audioList" :key="audio.name" class="audio-item" @click="play(audio)">
        <span class="audio-icon">♪</span>
        <span class="audio-label">{{ audio.label }}</span>
        <span class="audio-dur">{{ audio.duration }}s</span>
      </div>

      <hr />

      <h4>文字转语音（默认音色优先）</h4>
      <div class="tts-row">
        <input v-model="ttsText" placeholder="输入要让机器人说的话..." @keyup.enter="playTTS" />
        <button :disabled="ttsLoading" @click="playTTS">{{ ttsLoading ? '生成中' : '朗读' }}</button>
      </div>
      <div class="profile-hint">
        {{ defaultProfile ? `当前默认朗读音色：${defaultProfile.name}` : '未设置默认音色时，将使用树莓派普通 TTS。' }}
      </div>

      <hr />

      <h4>克隆音色朗读</h4>
      <div class="clone-block">
        <select v-model="selectedProfileId" class="profile-select">
          <option value="">选择音色</option>
          <option v-for="profile in profiles" :key="profile.id" :value="profile.id">
            {{ profile.name }}{{ profile.defaultProfile ? '（默认）' : '' }}
          </option>
        </select>
        <div class="tts-row">
          <input v-model="cloneText" placeholder="用已训练/已保存的音色朗读..." @keyup.enter="playCloneTTS" />
          <button :disabled="cloneLoading" @click="playCloneTTS">{{ cloneLoading ? '生成中' : '发送' }}</button>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { RobotSettingsApi } from '@/api/users'
import { ListVoiceProfilesApi, SpeakWithVoiceProfileApi } from '@/api/voiceProfiles'
import { toast } from '@/utils/toast'

const props = defineProps({
  machine: { type: Object, default: null }
})

const audioList = ref([
  { name: 'hello', label: '打招呼', duration: 2 },
  { name: 'happy', label: '开心', duration: 3 },
  { name: 'sad', label: '悲伤', duration: 2 },
  { name: 'beep', label: '提示音', duration: 1 }
])
const ttsText = ref('')
const cloneText = ref('')
const profiles = ref([])
const selectedProfileId = ref('')
const cloneLoading = ref(false)
const ttsLoading = ref(false)

const defaultProfile = computed(() => profiles.value.find((item) => item.defaultProfile))

ListVoiceProfilesApi().then((res) => {
  if (res?.code === 1) {
    profiles.value = res.data || []
    selectedProfileId.value = defaultProfile.value?.id || profiles.value[0]?.id || ''
  }
}).catch(() => {})

function play(audio) {
  RobotSettingsApi({
    machineId: props.machine.id,
    type: 'audio',
    value: audio.name
  }).catch(() => {})
}

async function playTTS() {
  const text = ttsText.value.trim()
  if (!text || !props.machine?.id) return

  ttsLoading.value = true
  try {
    if (defaultProfile.value) {
      const res = await SpeakWithVoiceProfileApi({
        machineId: props.machine.id,
        profileId: defaultProfile.value.id,
        text
      })
      if (res?.code !== 1) {
        toast.error(res?.msg || '默认音色朗读失败')
        return
      }
      toast.success(`已用默认音色「${defaultProfile.value.name}」发送朗读`)
    } else {
      await RobotSettingsApi({
        machineId: props.machine.id,
        type: 'tts',
        value: text
      })
    }
    ttsText.value = ''
  } catch (error) {
    toast.error(errorMessage(error, '朗读失败'))
  } finally {
    ttsLoading.value = false
  }
}

async function playCloneTTS() {
  if (!selectedProfileId.value) {
    toast.warning('请先创建或选择一个音色')
    return
  }
  const text = cloneText.value.trim()
  if (!text) return
  cloneLoading.value = true
  try {
    const res = await SpeakWithVoiceProfileApi({
      machineId: props.machine.id,
      profileId: selectedProfileId.value,
      text
    })
    if (res?.code === 1) {
      toast.success('已用克隆音色发送')
      cloneText.value = ''
    } else {
      toast.error(res?.msg || '发送失败')
    }
  } catch (error) {
    toast.error(errorMessage(error, '发送失败'))
  } finally {
    cloneLoading.value = false
  }
}

function errorMessage(error, fallback) {
  const data = error?.response?.data
  if (typeof data === 'string') return data || fallback
  return data?.msg || error?.message || fallback
}
</script>

<style scoped>
h3, h4 { margin-bottom: 10px; }

.no-device {
  padding: 40px 20px; color: #B09080; font-size: 14px; text-align: center;
}
.no-device.warn { color: #EF6C00; }

.audio-item {
  display: flex; align-items: center; gap: 10px;
  padding: 10px 12px; border: 1px solid rgba(255,160,120,0.15);
  border-radius: 8px; margin-bottom: 6px;
  cursor: pointer; transition: all 0.15s;
}
.audio-item:hover { background: #FFF5F0; border-color: rgba(255,140,80,0.3); }
.audio-icon { width: 18px; text-align: center; font-size: 18px; color: #FF7043; }
.audio-label { flex: 1; font-size: 13px; font-weight: 600; color: #5A3020; }
.audio-dur { font-size: 11px; color: #B09080; }

.tts-row { display: flex; gap: 8px; }
.tts-row input,
.profile-select {
  flex: 1; height: 38px; border-radius: 8px;
  border: 1px solid rgba(255,160,120,0.3);
  padding: 0 12px; font-size: 13px; font-family: inherit;
  color: #3A2010; background: #FFFAF7; outline: none;
  box-sizing: border-box;
}
.tts-row input:focus,
.profile-select:focus { border-color: #FF8A65; }
.tts-row button {
  height: 38px; padding: 0 18px; border-radius: 8px;
  border: none; background: linear-gradient(135deg, #FF9A76, #FF6040);
  color: white; font-size: 13px; font-weight: 700; font-family: inherit;
  cursor: pointer; box-shadow: 0 3px 10px rgba(255,96,64,0.25);
}
.tts-row button:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

.clone-block {
  display: grid;
  gap: 8px;
}

.profile-hint {
  margin-top: 6px;
  color: #9B7868;
  font-size: 12px;
  line-height: 1.4;
}

hr { border: none; border-top: 1px solid rgba(255,160,120,0.15); margin: 16px 0; }
</style>
