// pages/set/set.ts
Page({
  data: {
    can_speak_control: '开启',
    can_element_call: '开启',
    is_AI: '开启',
    open_robot_camera: '开启',
    can_content: '开启',
  },

  onLoad() {
    const app = getApp();
    this.setData({
      can_speak_control: app.globalData.can_speak_control || '开启',
      can_element_call: app.globalData.can_element_call || '开启',
      is_AI: app.globalData.is_AI || '开启',
      open_robot_camera: app.globalData.open_robot_camera || '开启',
      can_content: app.globalData.can_content || '开启',
    });
  },

  toggleSetting(e: any) {
    const key = e.currentTarget.dataset.key;
    const app = getApp();
    const current = this.data[key] || '开启';
    const next = current === '开启' ? '关闭' : '开始';

    app.globalData[key] = next;
    this.setData({ [key]: next });

    wx.showToast({
      title: `${next === '开启' ? '已开启' : '已关闭'}`,
      icon: 'none',
      duration: 1200,
    });
  },
});
