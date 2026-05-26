const { getStaticUrl } = require('../../utils/config.js');

// pages/menu/menu.js
Page({
  data: {
    username: "null",
    day_time: "",
    image_ip: '',
    currentTime: "",
    deviceId: ''
  },

  onLoad() {
    const app = getApp();
    this.getTime();
    this.getUsername();
    this.loadImages();
    this.startTime();
    this.setData({ deviceId: app.globalData.DEVICEID });
  },

  startTime() {
    this.updateTime();
    setInterval(() => {
      this.updateTime();
    }, 1000);
  },

  updateTime() {
    const now = new Date();
    const h = String(now.getHours()).padStart(2, '0');
    const m = String(now.getMinutes()).padStart(2, '0');
    const s = String(now.getSeconds()).padStart(2, '0');
    this.setData({ currentTime: `${h}:${m}:${s}` });
  },

  loadImages() {
    this.setData({ image_ip: getStaticUrl('/images/menu_container1.jpg') });
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
