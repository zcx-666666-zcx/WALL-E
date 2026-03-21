// utils/getData.js
// 1. 修复路径：和request.js同级，直接写 ./
import request from "./request.js";


async function getRate(deviceId) {
  let rate = -1;

  try {
    const res = await request.get(`/healthy/getRate/${deviceId}`);
    if (res.data?.rows?.length) {
      const list = res.data.rows.sort((a, b) => new Date(a.createdAt) - new Date(b.createdAt));
      const val = list.at(-1).rate;
      rate = val;
    }
  } catch (e) { console.error("心率获取失败", e); }

  const app = getApp();
  app.globalData.RATE = rate;
  //console.log('心率:' + rate);
}

async function getHumidity(deviceId) {
  let humidity = -1;

  try {
    const res = await request.get(`/healthy/getHumidity/${deviceId}`);
    if (res.data?.rows?.length) {
      const list = res.data.rows.sort((a, b) => new Date(a.createdAt) - new Date(b.createdAt));
      const val = list.at(-1).humidity;
      humidity = val;
    }
  } catch (e) { console.error("湿度获取失败", e); }

  const app = getApp();
  app.globalData.HUMIDITY = humidity;
  //console.log('湿度:' + humidity);
}

async function getBreathe(deviceId) {
  let breathe = -1;

  try {
    const res = await request.get(`/healthy/getBreathe/${deviceId}`);
    if (res.data?.rows?.length) {
      const list = res.data.rows.sort((a, b) => new Date(a.createdAt) - new Date(b.createdAt));
      const val = list.at(-1).breathe;
      breathe = val;
    }
  } catch (e) { console.error("呼吸获取失败", e); }

  const app = getApp();
  app.globalData.BREATHE = breathe;
  //console.log('呼吸:' + breathe);
}

async function getTemperature(deviceId) {
  let temperature = -1;

  try {
    const res = await request.get(`/healthy/getTemperature/${deviceId}`);
    if (res.data?.rows?.length) {
      const list = res.data.rows.sort((a, b) => new Date(a.createdAt) - new Date(b.createdAt));
      const val = list.at(-1).temperature;
      temperature = val;
    }
  } catch (e) { console.error("体温获取失败", e); }

  const app = getApp();
  app.globalData.TEMPERATURE = temperature;
  //console.log('温度:' + temperature);
}

async function getFall(deviceId) {
  let fall = false;

  try {
    const res = await request.get(`/healthy/getFall/${deviceId}`);
    const fallStatus = res.data.fall;
    let fallText = "未识别到目标";
    if (fallStatus === false) fallText = "正常";
    if (fallStatus === true) fallText = "跌倒";
    fall = fallText === "跌倒";
  } catch (e) { console.error("跌倒状态获取失败", e); }

  const app = getApp();
  app.globalData.FALL = fall;
  //console.log('跌倒:' + fall);
}

export {
  getRate,
  getHumidity,
  getBreathe,
  getTemperature,
  getFall
};