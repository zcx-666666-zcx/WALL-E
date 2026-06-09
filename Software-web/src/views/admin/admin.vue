<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { GetSystemConfigApi, UpdateSystemConfigApi } from '@/api/systemConfig'
import { ChangePasswordApi } from '@/api/users'
import { saveCachedConfig } from '@/utils/systemConfig'
import { clearAuthSession, logoutLocally } from '@/utils/authSession'

const router = useRouter()
const configs = ref([])
const loading = ref(false)
const saving = ref(false)
const changingPassword = ref(false)
const loadError = ref('')
const passwordForm = ref({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const groupLabels = {
  network: '网络地址',
  robot: '机器人控制',
  third_party: '第三方服务',
  secret: '密钥配置',
  custom: '自定义'
}

const groupedConfigs = computed(() => {
  const groups = []
  const index = new Map()
  configs.value.forEach((item) => {
    const key = item.configGroup || 'custom'
    if (!index.has(key)) {
      const group = { key, label: groupLabels[key] || key, items: [] }
      index.set(key, group)
      groups.push(group)
    }
    index.get(key).items.push(item)
  })
  return groups
})

onMounted(loadConfigs)

async function loadConfigs() {
  loading.value = true
  loadError.value = ''
  try {
    const result = await GetSystemConfigApi()
    if (result?.code === 1) {
      configs.value = (result.data || []).map(normalizeConfig)
    } else {
      handleLoadError(result?.msg || '读取系统配置失败')
    }
  } catch (error) {
    handleLoadError(error?.response?.data?.msg || error?.message || '读取系统配置失败')
  } finally {
    loading.value = false
  }
}

async function saveConfigs() {
  saving.value = true
  try {
    const payload = configs.value.map((item) => ({
      ...item,
      configValue: item.configValue == null ? '' : String(item.configValue).trim()
    }))
    const result = await UpdateSystemConfigApi(payload)
    if (result?.code === 1) {
      configs.value = (result.data || []).map(normalizeConfig)
      syncPublicCache(configs.value)
      ElMessage.success('系统配置已保存')
    } else {
      ElMessage.error(result?.msg || '保存失败')
    }
  } catch (error) {
    ElMessage.error(error?.response?.data?.msg || error?.message || '保存失败')
  } finally {
    saving.value = false
  }
}

async function changePassword() {
  const form = passwordForm.value
  if (!form.oldPassword || !form.newPassword || !form.confirmPassword) {
    ElMessage.warning('请填写完整密码信息')
    return
  }
  if (form.newPassword.length < 6) {
    ElMessage.warning('新密码至少 6 位')
    return
  }
  if (form.newPassword !== form.confirmPassword) {
    ElMessage.warning('两次输入的新密码不一致')
    return
  }
  changingPassword.value = true
  try {
    const result = await ChangePasswordApi({
      oldPassword: form.oldPassword,
      newPassword: form.newPassword
    })
    if (result?.code === 1) {
      passwordForm.value = { oldPassword: '', newPassword: '', confirmPassword: '' }
      ElMessage.success('密码已修改，请使用新密码重新登录')
      logoutLocally()
      router.replace('/login')
    } else {
      ElMessage.error(result?.msg || '修改密码失败')
    }
  } catch (error) {
    ElMessage.error(error?.response?.data?.msg || error?.message || '修改密码失败')
  } finally {
    changingPassword.value = false
  }
}

function handleLoadError(message) {
  loadError.value = message
  if (message === '无权限') {
      clearAuthSession()
    ElMessage.error('管理员登录状态已失效，请重新登录')
    router.replace('/login')
    return
  }
  ElMessage.error(message)
}

function addConfig() {
  configs.value.push({
    configKey: '',
    configValue: '',
    label: '',
    configGroup: 'custom',
    secret: false,
    remark: ''
  })
}

function normalizeConfig(item) {
  return {
    ...item,
    configValue: item.configValue == null ? '' : item.configValue,
    configGroup: item.configGroup || 'custom',
    label: item.label || item.configKey,
    secret: Boolean(item.secret)
  }
}

function syncPublicCache(items) {
  const map = {}
  items.forEach((item) => { map[item.configKey] = item.configValue })
  saveCachedConfig({
    apiBaseUrl: map['api.base-url'],
    webBaseUrl: map['web.base-url'],
    staticBaseUrl: map['static.base-url'],
    robotDefaultIp: map['robot.default-ip'],
    robotHttpPort: Number(map['robot.http-port']) || 5000,
    socketServerUrl: map['socket.server-url'],
    cozeApiUrl: map['coze.api-url'],
    cozeWorkflowId: map['coze.workflow-id'],
    publicConfig: Object.fromEntries(items.filter((item) => !item.secret).map((item) => [item.configKey, item.configValue]))
  })
}
</script>

<template>
  <div class="admin-root">
    <div class="page-header">
      <div class="page-title-block">
        <div class="page-title-icon">
          <el-icon :size="20"><Setting /></el-icon>
        </div>
        <div>
          <div class="page-title">系统配置</div>
          <div class="page-sub">统一维护 IP、URL、端口和密钥</div>
        </div>
      </div>
      <div class="page-actions">
        <el-button :loading="loading" @click="loadConfigs">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
        <el-button @click="addConfig">
          <el-icon><Plus /></el-icon>
          新增
        </el-button>
        <el-button type="primary" :loading="saving" @click="saveConfigs">
          <el-icon><Check /></el-icon>
          保存
        </el-button>
      </div>
    </div>

    <div v-loading="loading" class="config-scroll">
      <section class="config-section">
        <div class="section-head">
          <span>管理员账号</span>
          <span class="section-count">安全</span>
        </div>
        <div class="password-panel">
          <el-input
            v-model="passwordForm.oldPassword"
            type="password"
            show-password
            placeholder="当前密码"
          />
          <el-input
            v-model="passwordForm.newPassword"
            type="password"
            show-password
            placeholder="新密码，至少 6 位"
          />
          <el-input
            v-model="passwordForm.confirmPassword"
            type="password"
            show-password
            placeholder="再次输入新密码"
          />
          <el-button type="primary" :loading="changingPassword" @click="changePassword">
            修改密码
          </el-button>
        </div>
      </section>

      <el-empty v-if="!loading && loadError" :description="loadError">
        <el-button type="primary" @click="loadConfigs">重新加载</el-button>
      </el-empty>

      <el-empty v-else-if="!loading && groupedConfigs.length === 0" description="暂无系统配置">
        <el-button type="primary" @click="addConfig">新增配置</el-button>
      </el-empty>

      <section v-for="group in groupedConfigs" v-else :key="group.key" class="config-section">
        <div class="section-head">
          <span>{{ group.label }}</span>
          <span class="section-count">{{ group.items.length }}</span>
        </div>

        <div class="config-grid">
          <div v-for="item in group.items" :key="item.id || item.configKey" class="config-row">
            <div class="config-meta">
              <input v-model="item.label" class="label-input" placeholder="配置名称" />
              <input v-model="item.configKey" class="key-input" placeholder="config.key" :disabled="Boolean(item.id)" />
              <textarea v-model="item.remark" class="remark-input" placeholder="说明"></textarea>
            </div>
            <div class="config-value">
              <el-input
                v-model="item.configValue"
                :type="item.secret ? 'password' : 'text'"
                :show-password="item.secret"
                placeholder="配置值"
              />
              <div class="config-options">
                <el-select v-model="item.configGroup" size="small">
                  <el-option label="网络地址" value="network" />
                  <el-option label="机器人控制" value="robot" />
                  <el-option label="第三方服务" value="third_party" />
                  <el-option label="密钥配置" value="secret" />
                  <el-option label="自定义" value="custom" />
                </el-select>
                <el-switch
                  v-model="item.secret"
                  size="small"
                  active-text="敏感"
                  inactive-text="公开"
                  inline-prompt
                />
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<style scoped>
.admin-root {
  width: 100%;
  height: 100%;
  min-height: 0;
  padding: 20px 24px;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  gap: 16px;
  overflow-y: auto;
  overflow-x: hidden;
  font-family: var(--font);
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  flex-shrink: 0;
}

.page-title-block {
  display: flex;
  align-items: center;
  gap: 12px;
}

.page-title-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: linear-gradient(135deg, #2563eb, #0f766e);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.22);
}

.page-title {
  font-size: 18px;
  font-weight: 800;
  color: #263238;
}

.page-sub {
  font-size: 12px;
  color: #78909c;
  margin-top: 2px;
}

.page-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.config-scroll {
  flex: 0 0 auto;
  min-height: 0;
  overflow: visible;
  display: flex;
  flex-direction: column;
  gap: 14px;
  padding-bottom: 32px;
  padding-right: 2px;
}

.config-section {
  background: #ffffff;
  border: 1px solid rgba(80, 120, 140, 0.14);
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(35, 70, 90, 0.05);
  overflow: hidden;
}

.section-head {
  height: 44px;
  padding: 0 18px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid rgba(80, 120, 140, 0.1);
  font-weight: 700;
  color: #263238;
  background: #f8fbfc;
}

.section-count {
  min-width: 24px;
  height: 22px;
  border-radius: 999px;
  padding: 0 8px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: #e0f2fe;
  color: #0369a1;
  font-size: 12px;
}

.config-grid {
  display: flex;
  flex-direction: column;
}

.password-panel {
  display: grid;
  grid-template-columns: repeat(3, minmax(160px, 1fr)) auto;
  gap: 12px;
  padding: 16px 18px;
  align-items: center;
}

.config-row {
  display: grid;
  grid-template-columns: minmax(260px, 0.9fr) minmax(320px, 1.2fr);
  gap: 18px;
  padding: 16px 18px;
  border-bottom: 1px solid rgba(80, 120, 140, 0.08);
}

.config-row:last-child {
  border-bottom: 0;
}

.config-meta {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.label-input,
.key-input,
.remark-input {
  width: 100%;
  border: 1px solid rgba(80, 120, 140, 0.18);
  border-radius: 6px;
  outline: none;
  color: #263238;
  background: #fff;
  box-sizing: border-box;
  font-family: inherit;
}

.label-input,
.key-input {
  height: 34px;
  padding: 0 10px;
}

.key-input {
  font-family: var(--font-mono);
  color: #455a64;
}

.key-input:disabled {
  background: #f5f7f8;
  color: #78909c;
}

.remark-input {
  grid-column: 1 / -1;
  min-height: 52px;
  resize: vertical;
  padding: 9px 10px;
  line-height: 1.5;
}

.config-value {
  display: flex;
  flex-direction: column;
  gap: 10px;
  min-width: 0;
}

.config-options {
  display: flex;
  align-items: center;
  gap: 10px;
  justify-content: flex-end;
}

.config-options .el-select {
  width: 128px;
}

@media (max-width: 900px) {
  .admin-root {
    padding: 12px;
  }

  .page-header {
    align-items: flex-start;
    flex-direction: column;
  }

  .page-actions {
    width: 100%;
    justify-content: flex-start;
  }

  .config-row {
    grid-template-columns: 1fr;
  }

  .password-panel {
    grid-template-columns: 1fr;
  }
}
</style>
