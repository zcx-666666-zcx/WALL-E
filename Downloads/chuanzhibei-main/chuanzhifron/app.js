// app.js
App({
  /**
   * 小程序初始化完成时触发
   */
  onLaunch() {
    // 展示本地存储能力
    const logs = wx.getStorageSync('logs') || []
    logs.unshift(Date.now())
    wx.setStorageSync('logs', logs)

    // 检查用户是否已登录
    const token = wx.getStorageSync('token');
    if (!token) {
      // 如果未登录，跳转到登录页面
      wx.redirectTo({
        url: '/pages/login/login'
      });
    }
  },
  
  /**
   * 全局数据
   */
  globalData: {
    userInfo: null
  }
})

// {
//   "pages": [
//     "pages/login/login",
//     "pages/register/register",
//     "pages/index/index",
//     "pages/Heritage/Heritage",
//     "pages/ARExperience/ARExperience",
//     "pages/InheritorCommunity/InheritorCommunity",
//     "pages/PersonalCenter/PersonalCenter",
//     "pages/logs/logs",
//     "pages/learning/learning"
//   ],