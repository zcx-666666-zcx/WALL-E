const { getConfig } = require('../../utils/config.js');

Page({
  data: {
    url: '' // 你的网页URL
  },
  
  onLoad(options) {
    // 设置要加载的网页URL
    this.setData({
      url: getConfig().webBaseUrl || ''
    });
  }
})
