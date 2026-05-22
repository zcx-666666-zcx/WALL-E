// pages/user/user.ts
Page({
  data: {
    username: '',
    image_ip: ''
  },

  onLoad() {
    this.getName();
    this.loadImages();
  },

  loadImages() {
    this.setData({
      image_ip: 'https://fm98469zi591.vicp.fun/images/menu_container1.jpg'
    })
  },

  getName() {
    const app = getApp();
    if (app.globalData.USERNAME) {
      this.setData({ username: app.globalData.USERNAME });
    } else {
      wx.showToast({
        title: '数据异常，请检查登陆状态或网络连接',
        icon: 'none'
      });
    }
  },

  goToContact() {
    wx.navigateTo({ url: '/pages/contact/contact' });
  },
  goToEvents() {
    wx.navigateTo({ url: '/pages/elementList/elementList' });
  },
  goToCommands() {
    wx.navigateTo({ url: '/pages/commandList/commandList' });
  },
  goToStar() {
    wx.navigateTo({ url: '/pages/Star/Star' });
  },

  exit() {
    wx.navigateTo({
      url: '/pages/index/index'
    });
  },
});
