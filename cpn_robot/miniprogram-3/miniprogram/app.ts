// app.ts
App({
  globalData: {
    USERNAME:"人",
    usreId:"",
    can_speak_control: '开启',
    can_element_call: '开启',
    is_AI: '开启',
    open_robot_camera: '开启',
    can_content: '开启',
    user_phoneNumber:''
  },












  onLaunch() {
    // 展示本地存储能力
    const logs = wx.getStorageSync('logs') || []
    logs.unshift(Date.now())
    wx.setStorageSync('logs', logs)

    // 登录
    wx.login({
      success: res => {
        console.log(res.code)
        // 发送 res.code 到后台换取 openId, sessionKey, unionId
      },
    })
  },
})