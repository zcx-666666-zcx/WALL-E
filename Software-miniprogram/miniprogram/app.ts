import { getRate, getHumidity, getBreathe, getTemperature, getFall } from "./utils/getData.js";
import check from "./utils/check.js";
const { loadPublicConfig } = require("./utils/config.js");

const app = getApp ? getApp() : null;

App({
  globalData: {
    USERNAME:"人",
    usreId:"",
    can_speak_control: '开启',
    can_element_call: '开启',
    is_AI: '开启',
    open_robot_camera: '开启',
    can_content: '开启',
    user_phoneNumber:'',
    RATE: -1,
    HUMIDITY: -1,
    BREATHE: -1,
    TEMPERATURE: -1,
    FALL: null,
    DEVICEID: 'kCx33ym0Dt',
    HEALTH_ALERT_TEXT: '',
    HEALTH_ALERT_TYPE: false,
  },

  healthTimer: null as number | null,

  onLaunch() {
    const logs = wx.getStorageSync('logs') || []
    logs.unshift(Date.now())
    wx.setStorageSync('logs', logs)

    wx.login({
      success: res => {
        console.log(res.code)
      },
    })

    loadPublicConfig().then(() => this.startHealthManager());
  },

  startHealthManager() {
    const fetchAndCheck = async () => {
      const deviceId = this.globalData.DEVICEID;
      try {
        const [rate, humidity, breathe, temperature, fall] = await Promise.all([
          getRate(deviceId),
          getHumidity(deviceId),
          getBreathe(deviceId),
          getTemperature(deviceId),
          getFall(deviceId),
        ]);

        this.globalData.RATE = rate;
        this.globalData.HUMIDITY = humidity;
        this.globalData.BREATHE = breathe;
        this.globalData.TEMPERATURE = temperature;
        this.globalData.FALL = fall;

        const { num, type } = check(rate, humidity, breathe, temperature, fall);
        this.globalData.HEALTH_ALERT_TEXT = num;
        this.globalData.HEALTH_ALERT_TYPE = type;

        const eventBus = require('./utils/eventBus.js');
        eventBus.emit('healthDataUpdated', {
          rate, humidity, breathe, temperature, fall,
          alertText: num, alertType: type,
        });
      } catch (e) { console.error('Health manager fetch error:', e); }
    };

    fetchAndCheck();
    this.healthTimer = setInterval(fetchAndCheck, 2000) as any;
  },
});
