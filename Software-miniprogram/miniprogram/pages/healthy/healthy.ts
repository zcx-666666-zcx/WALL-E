// pages/healthy/healthy.js
import request from "../../utils/request.js";

Page({
  data: {
    deviceId: "kCx33ym0Dt",
    isFall: false,
    fall: "未识别到目标",
    userid: "",
    picture_url: "",
    Machines: [],
    showMachine: "暂无",

    rate: -1,
    humidity: -1,
    breath: -1,
    temperature: -1,

    maxRate: 0,        minRate: 240,
    maxHumidity: 0,    minHumidity: 100,
    maxBreath: 0,      minBreath: 100,
    maxTemperature: 0, minTemperature: 42,
  },

  fetchTimer: null,

  onLoad() {
    const userid = wx.getStorageSync("Id") || "";
    this.setData({ userid });
    this.getMachinesList();
    this.startFetchLoop();
  },

  onUnload() {
    if (this.fetchTimer) clearInterval(this.fetchTimer);
  },

  startFetchLoop() {
    this.fetchAllData();
    this.fetchTimer = setInterval(() => {
      this.fetchAllData();
      const app = getApp();
      app.globalData.RATE        = this.data.rate;
      app.globalData.HUMIDITY    = this.data.humidity;
      app.globalData.BREATHE     = this.data.breath;
      app.globalData.TEMPERATURE = this.data.temperature;
      app.globalData.FALL = (this.data.fall === "跌倒");
    }, 2000);
  },

  async fetchAllData() {
    await Promise.all([
      this.getRate(),
      this.getHumidity(),
      this.getBreath(),
      this.getTemperature(),
      this.getFall(),
    ]);
  },

  async getRate() {
    try {
      const res = await request.get(`/healthy/getRate/${this.data.deviceId}`);
      if (res.data?.rows?.length) {
        const val = [...res.data.rows].sort((a, b) => new Date(a.createdAt) - new Date(b.createdAt)).at(-1).rate;
        this.setData({ rate: val });
        this.calcMinMax("rate", val);
      }
    } catch (e) { console.error("心率获取失败", e); }
  },

  async getHumidity() {
    try {
      const res = await request.get(`/healthy/getHumidity/${this.data.deviceId}`);
      if (res.data?.rows?.length) {
        const val = [...res.data.rows].sort((a, b) => new Date(a.createdAt) - new Date(b.createdAt)).at(-1).humidity;
        this.setData({ humidity: val });
        this.calcMinMax("humidity", val);
      }
    } catch (e) { console.error("湿度获取失败", e); }
  },

  async getBreath() {
    try {
      const res = await request.get(`/healthy/getBreathe/${this.data.deviceId}`);
      if (res.data?.rows?.length) {
        const val = [...res.data.rows].sort((a, b) => new Date(a.createdAt) - new Date(b.createdAt)).at(-1).breathe;
        this.setData({ breath: val });
        this.calcMinMax("breath", val);
      }
    } catch (e) { console.error("呼吸获取失败", e); }
  },

  async getTemperature() {
    try {
      const res = await request.get(`/healthy/getTemperature/${this.data.deviceId}`);
      if (res.data?.rows?.length) {
        const val = [...res.data.rows].sort((a, b) => new Date(a.createdAt) - new Date(b.createdAt)).at(-1).temperature;
        this.setData({ temperature: val });
        this.calcMinMax("temperature", val);
      }
    } catch (e) { console.error("体温获取失败", e); }
  },

  async getFall() {
    try {
      const res = await request.get(`/healthy/getFall/${this.data.deviceId}`);
      const s = res.data.fall;
      this.setData({ fall: s === false ? "正常" : s === true ? "跌倒" : "未识别到目标" });
    } catch (e) { console.error("跌倒状态获取失败", e); }
  },

  calcMinMax(type, val) {
    const d = this.data;
    const map = {
      rate:        { max: "maxRate",        min: "minRate"        },
      humidity:    { max: "maxHumidity",    min: "minHumidity"    },
      breath:      { max: "maxBreath",      min: "minBreath"      },
      temperature: { max: "maxTemperature", min: "minTemperature" },
    };
    if (!map[type]) return;
    this.setData({
      [map[type].max]: Math.max(d[map[type].max], val),
      [map[type].min]: Math.min(d[map[type].min], val),
    });
  },

  async getMachinesList() {
    try {
      const res = await request.get(`/contractMachine/search/${this.data.userid}`);
      if (res.code === 1 && res.data?.rows) {
        this.setData({ Machines: res.data.rows });
      }
    } catch (e) { console.error("设备列表获取失败", e); }
  },

  changeDeviceId(e) {
    const deviceId = e.currentTarget.dataset.id;
    this.setData({ deviceId }, () => this.fetchAllData());
  },

  Reloading() {
    this.setData({
      rate: -1, humidity: -1, breath: -1, temperature: -1,
      maxRate: 0, minRate: 240, maxHumidity: 0, minHumidity: 100,
      maxBreath: 0, minBreath: 100, maxTemperature: 0, minTemperature: 42,
    });
    this.fetchAllData();
  },
});