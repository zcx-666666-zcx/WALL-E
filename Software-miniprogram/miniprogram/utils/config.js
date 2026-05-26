const STORAGE_KEY = 'walleSystemConfig';

const DEFAULT_CONFIG = {
  apiBaseUrl: 'http://localhost:8080/api',
  staticBaseUrl: 'http://localhost:8080',
  webBaseUrl: '',
  socketServerUrl: 'http://localhost:8081',
  cozeApiUrl: 'https://api.coze.cn',
  cozeWorkflowId: ''
};

function normalize(config = {}) {
  return Object.assign({}, DEFAULT_CONFIG, config);
}

function getConfig() {
  const cached = wx.getStorageSync(STORAGE_KEY);
  return normalize(cached || {});
}

function saveConfig(config) {
  const merged = normalize(config);
  wx.setStorageSync(STORAGE_KEY, merged);
  return merged;
}

function getApiBaseUrl() {
  return (getConfig().apiBaseUrl || DEFAULT_CONFIG.apiBaseUrl).replace(/\/$/, '');
}

function getStaticUrl(path) {
  if (!path) return '';
  if (/^https?:\/\//i.test(path)) return path;
  const base = (getConfig().staticBaseUrl || DEFAULT_CONFIG.staticBaseUrl).replace(/\/$/, '');
  return `${base}/${String(path).replace(/^\//, '')}`;
}

function getSocketServerUrl() {
  return getConfig().socketServerUrl || DEFAULT_CONFIG.socketServerUrl;
}

function getCozeConfig() {
  const config = getConfig();
  return {
    apiUrl: config.cozeApiUrl || DEFAULT_CONFIG.cozeApiUrl,
    workflowId: config.cozeWorkflowId || ''
  };
}

function loadPublicConfig() {
  return new Promise((resolve) => {
    wx.request({
      url: `${getApiBaseUrl()}/system-config/public`,
      method: 'GET',
      success: (res) => {
        const data = res.data && res.data.data ? res.data.data : null;
        if (!data) {
          resolve(getConfig());
          return;
        }
        resolve(saveConfig({
          apiBaseUrl: data.apiBaseUrl,
          staticBaseUrl: data.staticBaseUrl,
          webBaseUrl: data.webBaseUrl,
          socketServerUrl: data.socketServerUrl,
          cozeApiUrl: data.cozeApiUrl,
          cozeWorkflowId: data.cozeWorkflowId
        }));
      },
      fail: () => resolve(getConfig())
    });
  });
}

module.exports = {
  DEFAULT_CONFIG,
  getConfig,
  saveConfig,
  getApiBaseUrl,
  getStaticUrl,
  getSocketServerUrl,
  getCozeConfig,
  loadPublicConfig
};
