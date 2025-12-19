// logs.js
const util = require('../../utils/util.js')

/**
 * 日志页面逻辑处理
 */
Page({
  /**
   * 页面初始数据
   */
  data: {
    logs: []
  },

  /**
   * 页面加载时执行
   */
  onLoad() {
    this.setData({
      logs: (wx.getStorageSync('logs') || []).map(log => {
        return {
          date: util.formatTime(new Date(log)),
          timeStamp: log
        }
      })
    })
  }
})
