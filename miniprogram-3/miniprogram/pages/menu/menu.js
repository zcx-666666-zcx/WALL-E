// pages/menu/menu.js
import check from "../../utils/check.js";
import { getRate, getHumidity, getBreathe, getTemperature, getFall } from "../../utils/getData.js";

Page({
  data: {
    username: "null",
    day_time: "",
    image_ip: '',
    currentTime: "",
    text: "",
    Show: false,
    deviceId: ''
  },

  onLoad() {
    const app = getApp();
    this.getTime();
    this.getUsername();
    this.loadImages();
    this.startTime();
    this.setData({ deviceId: app.globalData.DEVICEID });
    console.log(this.data.deviceId);
  },

  startTime() {
    this.updateTime();
    setInterval(() => {
      this.updateTime();
      this.getData();
      this.Gocheck();
    }, 1000);
  },

  getData() {
    const deviceId = this.data.deviceId;
    getRate(deviceId);
    getHumidity(deviceId);
    getBreathe(deviceId);
    getTemperature(deviceId);
    getFall(deviceId);
  },

  Gocheck() {
    const app = getApp();
    const rate        = app.globalData.RATE        || 0;
    const humidity    = app.globalData.HUMIDITY    || 0;
    const breathe     = app.globalData.BREATHE     || 0;
    const temperature = app.globalData.TEMPERATURE || 0;
    const fall        = app.globalData.FALL        || false;

    const { num, type } = check(rate, humidity, breathe, temperature, fall);
    this.setData({ text: num, Show: type });
  },

  updateTime() {
    const now = new Date();
    const h = String(now.getHours()).padStart(2, '0');
    const m = String(now.getMinutes()).padStart(2, '0');
    const s = String(now.getSeconds()).padStart(2, '0');
    this.setData({ currentTime: `${h}:${m}:${s}` });
  },

  loadImages() {
    this.setData({ image_ip: 'http://localhost:8080/images/menu_container1.jpg' });
  },

  getTime() {
    const hours = new Date().getHours();
    let day_time = "晚上";
    if      (hours <= 7)  day_time = "早上";
    else if (hours <= 11) day_time = "上午";
    else if (hours <= 13) day_time = "中午";
    else if (hours <= 17) day_time = "下午";
    this.setData({ day_time });
  },

  getUsername() {
    const app = getApp();
    if (app.globalData.USERNAME) {
      this.setData({ username: app.globalData.USERNAME });
    } else {
      wx.showToast({ title: '信息异常', icon: 'none' });
    }
  }
})