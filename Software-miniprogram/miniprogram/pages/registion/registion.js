const request = require('../../utils/request.js').default;
const { getStaticUrl } = require('../../utils/config.js');

// pages/registion/registion.js
Page({
  data: {
    username: '',
    password: '',
    surePassword: '',
    phoneNumber: '',
    pwdMatch: '',   // '' | 'ok' | 'err'
    image_ip1: '',
    image_ip2: ''
  },

  onLoad() {
    this.setData({
      image_ip1: getStaticUrl('/images/index_container1.png'),
      image_ip2: getStaticUrl('/images/index_picture.png')
    })
  },

  nameHandle(e) {
    this.setData({ username: e.detail.value });
  },

  passwordHandle(e) {
    const val = e.detail.value;
    this.setData({ password: val });
    // 密码变化时同步更新确认框状态
    if (this.data.surePassword) {
      this.setData({ pwdMatch: val === this.data.surePassword ? 'ok' : 'err' });
    }
  },

  sureHandle(e) {
    const val = e.detail.value;
    this.setData({
      surePassword: val,
      pwdMatch: val === '' ? '' : val === this.data.password ? 'ok' : 'err'
    });
  },

  phone_numberHandle(e) {
    this.setData({ phoneNumber: e.detail.value });
  },

  GoRegist() {
    const username = this.data.username.trim();
    const password = this.data.password.trim();
    const surePassword = this.data.surePassword.trim();
    const phoneNumber = this.data.phoneNumber.trim();

    if (!username || !password || !surePassword || !phoneNumber) {
      wx.showToast({ title: '请输入完整内容', icon: 'none' });
      return;
    }

    if (password !== surePassword) {
      wx.showToast({ title: '密码输入不一致', icon: 'none' });
      return;
    }

    const phoneRegex = /^1[3-9]\d{9}$/;
    if (!phoneRegex.test(phoneNumber)) {
      wx.showToast({ title: '请输入正确的手机号', icon: 'none' });
      return;
    }

    wx.showLoading({ title: '注册中...', mask: true });

    request.post('/users/register', { username, phoneNumber, password })
      .then((data) => {
        wx.hideLoading();
        console.log('注册响应:', data);

        if (data.code) {
          wx.showToast({ title: '注册成功', icon: 'success', duration: 1500 });
          setTimeout(() => {
            wx.navigateTo({ url: '/pages/login/login' });
          }, 1500);
        } else {
          wx.showToast({
            title: data.message || data.msg || '注册失败',
            icon: 'none', duration: 3000
          });
        }
      })
      .catch((err) => {
        wx.hideLoading();
        console.error('请求失败:', err);
        wx.showToast({ title: '网络请求失败，请检查连接', icon: 'none', duration: 3000 });
      });
  }
})
