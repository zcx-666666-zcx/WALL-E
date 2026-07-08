<script setup>
import { computed, onMounted, ref } from 'vue'
import { Delete, Headset, Microphone, Promotion, Refresh, Star, UploadFilled, VideoPlay } from '@element-plus/icons-vue'
import { GetMachineListApi } from '@/api/users'
import {
  CreateVoiceProfileApi,
  DeleteVoiceProfileApi,
  ListVoiceProfilesApi,
  PreviewVoiceProfileApi,
  SetDefaultVoiceProfileApi,
  SpeakWithVoiceProfileApi,
} from '@/api/voiceProfiles'
import { toast, confirm } from '@/utils/toast'

const profiles = ref([])
const machines = ref([])
const selectedProfileId = ref('')
const selectedMachineId = ref('')
const loading = ref(false)
const uploading = ref(false)
const previewingId = ref(null)
const speaking = ref(false)
const FIXED_REFERENCE_TEXT = '你好，我是慧慧。今天我们一起测试音色克隆。'
const FIXED_PREVIEW_TEXT = '你好，我是慧慧，正在使用克隆音色进行试听。'
const FIXED_HARDWARE_TEXT = '你好，我是慧慧，这段声音正在从台式机发送到机器人播放。'

const form = ref({
  name: '',
  engine: 'gpt_sovits',
  audio: null,
})

const selectedProfile = computed(() => profiles.value.find((item) => item.id === selectedProfileId.value))

onMounted(() => {
  loadAll()
})

async function loadAll() {
  loading.value = true
  try {
    await Promise.all([loadProfiles(), loadMachines()])
  } finally {
    loading.value = false
  }
}

async function loadProfiles() {
  const res = await ListVoiceProfilesApi()
  if (res?.code === 1) {
    profiles.value = res.data || []
    const defaultProfile = profiles.value.find((item) => item.defaultProfile)
    selectedProfileId.value = defaultProfile?.id || profiles.value[0]?.id || ''
  }
}

async function loadMachines() {
  const userId = localStorage.getItem('Id')
  if (!userId) return
  const res = await GetMachineListApi(userId)
  if (res?.code === 1) {
    machines.value = res.data?.rows || []
    selectedMachineId.value = machines.value[0]?.id || ''
  }
}

function onFileChange(file) {
  form.value.audio = file.raw
}

function onFileRemove() {
  form.value.audio = null
}

async function createProfile() {
  if (!form.value.audio) {
    toast.warning('请先选择一段参考音频')
    return
  }
  const fd = new FormData()
  fd.append('name', form.value.name || '自定义音色')
  fd.append('engine', 'gpt_sovits')
  fd.append('referenceText', FIXED_REFERENCE_TEXT)
  fd.append('audio', form.value.audio)

  uploading.value = true
  try {
    const res = await CreateVoiceProfileApi(fd)
    if (res?.code === 1) {
      toast.success('音色已创建')
      form.value = { name: '', engine: 'gpt_sovits', audio: null }
      await loadProfiles()
      selectedProfileId.value = res.data?.id || selectedProfileId.value
    } else {
      toast.error(res?.msg || '创建音色失败')
    }
  } finally {
    uploading.value = false
  }
}

async function setDefault(profile) {
  const res = await SetDefaultVoiceProfileApi(profile.id)
  if (res?.code === 1) {
    toast.success('默认机器人朗读音色已更新')
    await loadProfiles()
  } else {
    toast.error(res?.msg || '设置失败')
  }
}

async function removeProfile(profile) {
  const ok = await confirm(`确定删除音色「${profile.name}」吗？`, '删除音色', { type: 'warning' })
  if (!ok) return
  const res = await DeleteVoiceProfileApi(profile.id)
  if (res?.code === 1) {
    toast.success('已删除音色')
    await loadProfiles()
  } else {
    toast.error(res?.msg || '删除失败')
  }
}

async function preview(profile) {
  previewingId.value = profile.id
  try {
    const blob = await PreviewVoiceProfileApi(profile.id, FIXED_PREVIEW_TEXT)
    const url = URL.createObjectURL(blob)
    const audio = new Audio(url)
    audio.onended = () => URL.revokeObjectURL(url)
    await audio.play()
  } catch (error) {
    toast.error(await readErrorMessage(error, '试听失败，请检查参考音频和 voice-service'))
  } finally {
    previewingId.value = null
  }
}

async function speakToRobot() {
  if (!selectedProfileId.value) {
    toast.warning('请选择音色')
    return
  }
  if (!selectedMachineId.value) {
    toast.warning('请选择设备')
    return
  }
  speaking.value = true
  try {
    const res = await SpeakWithVoiceProfileApi({
      profileId: selectedProfileId.value,
      machineId: selectedMachineId.value,
      text: FIXED_HARDWARE_TEXT,
    })
    if (res?.code === 1) {
      toast.success('机器人硬件试听已发送')
    } else {
      toast.error(res?.msg || '发送失败')
    }
  } finally {
    speaking.value = false
  }
}

async function readErrorMessage(error, fallback) {
  const data = error?.response?.data
  if (data instanceof Blob) {
    const text = await data.text()
    return text || fallback
  }
  if (typeof data === 'string') return data || fallback
  return data?.msg || error?.message || fallback
}
</script>

<template>
  <div class="voice-root">
    <header class="page-header">
      <div class="page-title-wrap">
        <div class="page-title-icon"><el-icon :size="20"><Microphone /></el-icon></div>
        <div>
          <div class="page-title">音色克隆</div>
          <div class="page-sub">上传参考音频，在台式机生成语音，树莓派作为播放终端</div>
        </div>
      </div>
      <el-button :icon="Refresh" :loading="loading" @click="loadAll">刷新</el-button>
    </header>

    <div class="voice-layout">
      <section class="panel upload-panel">
        <div class="panel-head">
          <div>
            <h2>创建音色</h2>
            <p>请上传 3-10 秒干净人声，录音内容必须照读下面固定参考句。</p>
          </div>
        </div>

        <el-form label-position="top">
          <el-form-item label="音色名称">
            <el-input v-model="form.name" placeholder="例如：妈妈的声音" maxlength="64" />
          </el-form-item>
          <el-form-item label="模型模式">
            <el-radio-group v-model="form.engine" disabled>
              <el-radio-button label="gpt_sovits">GPT-SoVITS</el-radio-button>
            </el-radio-group>
          </el-form-item>
          <el-form-item label="参考音频文字稿（固定）">
            <div class="fixed-copy">{{ FIXED_REFERENCE_TEXT }}</div>
            <div class="field-note">这段文字就是上传参考音频里要念的内容，用来让 GPT-SoVITS 对齐声音和文本；它不限制音色以后只能说这一句。</div>
          </el-form-item>
          <el-form-item label="参考音频">
            <el-upload
              drag
              action="#"
              :auto-upload="false"
              :limit="1"
              accept="audio/*"
              :on-change="onFileChange"
              :on-remove="onFileRemove"
            >
              <el-icon class="upload-icon"><UploadFilled /></el-icon>
              <div class="upload-text">拖入音频或点击选择</div>
              <template #tip>
                <div class="upload-tip">支持 wav、mp3、m4a、webm、flac 等常见格式；后台会统一转成 GPT-SoVITS 更稳定的 WAV。</div>
              </template>
            </el-upload>
          </el-form-item>
          <el-button type="primary" :loading="uploading" class="create-btn" @click="createProfile">保存音色</el-button>
        </el-form>
      </section>

      <section class="panel list-panel">
        <div class="panel-head">
          <div>
            <h2>音色库</h2>
            <p>设为默认后，“驱动/音频”里的文字朗读会优先用这个克隆音色生成，再推给机器人播放。</p>
          </div>
        </div>
        <div class="fixed-copy preview-copy">{{ FIXED_PREVIEW_TEXT }}</div>
        <div class="field-note">点击音色卡片上的试听按钮时，本地固定朗读这句话，方便每次对比同一段内容的音色效果。</div>

        <div v-if="profiles.length === 0" class="empty-state">
          <el-icon :size="34"><Headset /></el-icon>
          <span>还没有音色，先上传一段参考音频。</span>
        </div>

        <div v-else class="profile-list">
          <article
            v-for="profile in profiles"
            :key="profile.id"
            class="profile-card"
            :class="{ selected: selectedProfileId === profile.id }"
            @click="selectedProfileId = profile.id"
          >
            <div class="profile-main">
              <div class="avatar"><el-icon><Microphone /></el-icon></div>
              <div class="profile-text">
                <div class="profile-name">
                  {{ profile.name }}
                  <span v-if="profile.defaultProfile" class="default-tag">默认</span>
                </div>
                <div class="profile-meta">{{ profile.engine }} · {{ profile.status }}</div>
                <div v-if="profile.lastError" class="profile-warn">{{ profile.lastError }}</div>
              </div>
            </div>
            <div class="profile-actions">
              <el-button :icon="VideoPlay" circle title="试听" :loading="previewingId === profile.id" @click.stop="preview(profile)" />
              <el-button :icon="Star" circle title="设为默认机器人朗读音色" @click.stop="setDefault(profile)" />
              <el-button :icon="Delete" circle title="删除" @click.stop="removeProfile(profile)" />
            </div>
          </article>
        </div>
      </section>

      <section class="panel test-panel">
        <div class="panel-head">
          <div>
            <h2>机器人硬件试听</h2>
            <p>台式机先合成固定试听句，再通过设备 IP 的 6007 端口推给树莓派播放。</p>
          </div>
        </div>

        <div class="test-grid">
          <label>
            <span>音色</span>
            <el-select v-model="selectedProfileId" placeholder="选择音色">
              <el-option v-for="profile in profiles" :key="profile.id" :label="profile.name" :value="profile.id" />
            </el-select>
          </label>
          <label>
            <span>设备</span>
            <el-select v-model="selectedMachineId" placeholder="选择机器人">
              <el-option v-for="machine in machines" :key="machine.id" :label="machine.machines" :value="machine.id" />
            </el-select>
          </label>
        </div>

        <div class="fixed-copy send-copy">{{ FIXED_HARDWARE_TEXT }}</div>
        <div class="field-note">这是在机器人上试听克隆音色：音频仍由台式机合成，树莓派只负责播放。需要树莓派正在运行 tts_stream_player.py，设备 IP 配置正确，并且这台台式机能访问树莓派 6007 端口；如果 6007 不通，后端只能退回普通 TTS，听到的就不是克隆音色。</div>
        <div class="send-row">
          <div class="current-profile">
            当前音色：{{ selectedProfile?.name || '未选择' }}
          </div>
          <el-button type="primary" :icon="Promotion" :loading="speaking" @click="speakToRobot">在机器人上试听固定句</el-button>
        </div>
      </section>
    </div>
  </div>
</template>

<style scoped>
.voice-root {
  width: 100%;
  min-height: 100%;
  display: flex;
  flex-direction: column;
  gap: 16px;
  font-family: "PingFang SC", "Microsoft YaHei", sans-serif;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.page-title-wrap {
  display: flex;
  align-items: center;
  gap: 12px;
}

.page-title-icon {
  width: 42px;
  height: 42px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  background: linear-gradient(135deg, #ff8a65, #e64a19);
  box-shadow: 0 4px 12px rgba(230, 74, 25, 0.22);
}

.page-title {
  font-size: 20px;
  font-weight: 800;
  color: #3a2010;
}

.page-sub {
  margin-top: 2px;
  font-size: 12px;
  color: #9b7868;
}

.voice-layout {
  display: grid;
  grid-template-columns: minmax(300px, 380px) minmax(360px, 1fr);
  grid-template-areas:
    "upload list"
    "test test";
  gap: 16px;
}

.panel {
  background: #fff;
  border: 1px solid rgba(255, 160, 120, 0.16);
  border-radius: 8px;
  padding: 18px;
  box-shadow: 0 2px 12px rgba(200, 90, 50, 0.05);
}

.upload-panel { grid-area: upload; }
.list-panel { grid-area: list; }
.test-panel { grid-area: test; }

.panel-head {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 14px;
}

.panel-head h2 {
  margin: 0;
  color: #3a2010;
  font-size: 16px;
}

.panel-head p {
  margin: 4px 0 0;
  color: #9b7868;
  font-size: 12px;
  line-height: 1.5;
}

.upload-icon {
  font-size: 30px;
  color: #ff7043;
}

.upload-text {
  color: #5a3020;
  font-weight: 700;
}

.upload-tip {
  color: #a88979;
  font-size: 12px;
}

.fixed-copy {
  width: 100%;
  min-height: 42px;
  display: flex;
  align-items: center;
  padding: 10px 12px;
  box-sizing: border-box;
  border-radius: 7px;
  color: #3a2010;
  background: #fff7f2;
  line-height: 1.6;
  font-size: 13px;
  font-weight: 700;
}

.send-copy {
  margin-bottom: 8px;
}

.field-note {
  margin-top: 6px;
  color: #9b7868;
  line-height: 1.6;
  font-size: 12px;
}

.create-btn {
  width: 100%;
}

.empty-state {
  min-height: 220px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  gap: 10px;
  color: #a88979;
}

.profile-list {
  display: grid;
  gap: 10px;
  max-height: 390px;
  overflow: auto;
  padding-right: 4px;
}

.profile-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  border: 1px solid rgba(255, 160, 120, 0.16);
  border-radius: 8px;
  padding: 12px;
  cursor: pointer;
  transition: border-color 0.15s, background 0.15s;
}

.profile-card:hover,
.profile-card.selected {
  background: #fff7f2;
  border-color: rgba(255, 112, 67, 0.35);
}

.profile-main {
  min-width: 0;
  display: flex;
  align-items: center;
  gap: 10px;
}

.avatar {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #e64a19;
  background: #fff0e8;
}

.profile-text {
  min-width: 0;
}

.profile-name {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #3a2010;
  font-weight: 800;
}

.default-tag {
  color: #1b7f3a;
  background: #eaf8ee;
  border: 1px solid #c6ebcf;
  border-radius: 999px;
  padding: 1px 7px;
  font-size: 11px;
  font-weight: 700;
}

.profile-meta {
  margin-top: 2px;
  color: #9b7868;
  font-size: 12px;
}

.profile-warn {
  margin-top: 4px;
  color: #d27000;
  font-size: 11px;
  max-width: 520px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.profile-actions {
  display: flex;
  gap: 6px;
  flex-shrink: 0;
}

.test-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
  margin-bottom: 12px;
}

.test-grid label {
  display: grid;
  gap: 6px;
}

.test-grid span {
  color: #8a5040;
  font-size: 12px;
  font-weight: 700;
}

.send-row {
  margin-top: 12px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.current-profile {
  color: #8a5040;
  font-size: 13px;
}

@media (max-width: 900px) {
  .voice-layout {
    grid-template-columns: 1fr;
    grid-template-areas:
      "upload"
      "list"
      "test";
  }

  .test-grid {
    grid-template-columns: 1fr;
  }

  .send-row {
    align-items: stretch;
    flex-direction: column;
  }
}
</style>
