const request = require('../../utils/request.js').default;
const { getStaticUrl } = require('../../utils/config.js');

// pages/login/login.js
Page({
  data: {
    login_username: '',
    login_password: '',
    image_ip1: '',
    image_ip2: ''
  },

  onLoad() {
    this.setData({
      image_ip1: getStaticUrl('/images/index_container1.png'),
      image_ip2: getStaticUrl('/images/index_picture.png')
    })
  },

  login_usernameInput(e) {
    this.setData({ login_username: e.detail.value });
  },

  login_passwordInput(e) {
    this.setData({ login_password: e.detail.value });
  },

  Gologin() {
    const login_username = this.data.login_username.trim();
    const login_password = this.data.login_password.trim();

    if (!login_username || !login_password) {
      wx.showToast({ title: '请输入完整内容', icon: 'none' });
      return;
    }

    wx.showLoading({ title: '登录中...', mask: true });

    request.post('/login', { username: login_username, password: login_password })
      .then((data) => {
        wx.hideLoading();
        console.log('登录响应:', data);

        if (data && data.code) {
          wx.showToast({ title: '登录成功', icon: 'success' });
          wx.setStorageSync('username', login_username);
          wx.setStorageSync('loginUserObject', data.data);
          wx.setStorageSync('Id', data.data.id);

          const app = getApp();
          const userId = data.data.id || null;
          app.globalData.USERNAME = login_username;
          app.globalData.userId = userId;

          setTimeout(() => {
            wx.switchTab({
              url: '/pages/menu/menu',
              fail: () => {
                wx.navigateTo({
                  url: '/pages/menu/menu',
                  fail: (err) => {
                    console.error('跳转失败:', err);
                    wx.showToast({ title: '跳转失败', icon: 'none' });
                  }
                });
              }
            });
          }, 1500);
        } else {
          const msg = data ? (data.message || data.msg || '登录失败') : '服务器无响应';
          wx.showToast({ title: msg, icon: 'none' });
        }
      })
      .catch((err) => {
        wx.hideLoading();
        console.error('请求错误:', err);
        wx.showToast({ title: '请求失败，请检查网络', icon: 'none' });
      });
  }
})
