import axios from 'axios'

const STORAGE_KEY = 'walleSystemConfig'
const ENV_API_BASE_URL = (import.meta.env?.VITE_API_BASE_URL || '').trim()

const BASE_PUBLIC_CONFIG = {
  apiBaseUrl: '/api',
  webBaseUrl: '',
  staticBaseUrl: '',
  robotDefaultIp: '127.0.0.1',
  robotHttpPort: 5000,
  socketServerUrl: 'http://localhost:8081',
  cozeApiUrl: 'https://api.coze.cn',
  cozeWorkflowId: '',
  publicConfig: {}
}

function mergeConfig(config) {
  return { ...BASE_PUBLIC_CONFIG, ...(config || {}) }
}

function applyEnvOverrides(config) {
  if (!ENV_API_BASE_URL) return config
  return { ...config, apiBaseUrl: ENV_API_BASE_URL }
}

export const DEFAULT_PUBLIC_CONFIG = applyEnvOverrides(mergeConfig())

export function getCachedConfig() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (raw) return applyEnvOverrides(mergeConfig(JSON.parse(raw)))
  } catch {
    localStorage.removeItem(STORAGE_KEY)
  }
  return applyEnvOverrides(mergeConfig())
}

export function saveCachedConfig(config) {
  const merged = mergeConfig(config)
  localStorage.setItem(STORAGE_KEY, JSON.stringify(merged))
  return applyEnvOverrides(merged)
}

export function getApiBaseUrl() {
  return getCachedConfig().apiBaseUrl || '/api'
}

export function getSocketServerUrl() {
  return getCachedConfig().socketServerUrl || DEFAULT_PUBLIC_CONFIG.socketServerUrl
}

export function getRobotHttpPort() {
  return Number(getCachedConfig().robotHttpPort) || DEFAULT_PUBLIC_CONFIG.robotHttpPort
}

export function getConfigValue(key, fallback = '') {
  const config = getCachedConfig()
  return config.publicConfig?.[key] ?? fallback
}

export function resolveStaticUrl(path) {
  if (!path) return ''
  if (/^https?:\/\//i.test(path)) return path
  const base = getCachedConfig().staticBaseUrl || ''
  if (!base) return path
  return `${base.replace(/\/$/, '')}/${String(path).replace(/^\//, '')}`
}

export async function loadPublicConfig() {
  const baseURL = getApiBaseUrl()
  const response = await axios.get(`${baseURL}/system-config/public`, { timeout: 8000 })
  const payload = response.data?.data || response.data
  return saveCachedConfig(payload)
}
