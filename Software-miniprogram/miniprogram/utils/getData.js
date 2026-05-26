import request from "./request.js";

async function getRate(deviceId) {
  try {
    const res = await request.get(`/healthy/getRate/${deviceId}`);
    if (res.data?.rows?.length) {
      const list = res.data.rows.sort((a, b) => new Date(a.createdAt) - new Date(b.createdAt));
      return list.at(-1).rate;
    }
  } catch (e) { console.error("心率获取失败", e); }
  return -1;
}

async function getHumidity(deviceId) {
  try {
    const res = await request.get(`/healthy/getHumidity/${deviceId}`);
    if (res.data?.rows?.length) {
      const list = res.data.rows.sort((a, b) => new Date(a.createdAt) - new Date(b.createdAt));
      return list.at(-1).humidity;
    }
  } catch (e) { console.error("湿度获取失败", e); }
  return -1;
}

async function getBreathe(deviceId) {
  try {
    const res = await request.get(`/healthy/getBreathe/${deviceId}`);
    if (res.data?.rows?.length) {
      const list = res.data.rows.sort((a, b) => new Date(a.createdAt) - new Date(b.createdAt));
      return list.at(-1).breathe;
    }
  } catch (e) { console.error("呼吸获取失败", e); }
  return -1;
}

async function getTemperature(deviceId) {
  try {
    const res = await request.get(`/healthy/getTemperature/${deviceId}`);
    if (res.data?.rows?.length) {
      const list = res.data.rows.sort((a, b) => new Date(a.createdAt) - new Date(b.createdAt));
      return list.at(-1).temperature;
    }
  } catch (e) { console.error("体温获取失败", e); }
  return -1;
}

async function getFall(deviceId) {
  try {
    const res = await request.get(`/healthy/getFall/${deviceId}`);
    return res.data.fall === true;
  } catch (e) { console.error("跌倒状态获取失败", e); }
  return false;
}

export { getRate, getHumidity, getBreathe, getTemperature, getFall };
