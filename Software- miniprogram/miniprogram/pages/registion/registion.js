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
      image_ip1: 'https://fm98469zi591.vicp.fun/index_container1.png',
      image_ip2: 'https://fm98469zi591.vicp.fun/index_picture.png'
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
    console.log(username,password);

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

    console.log(username,password);

    wx.request({
      url: 'https://fm98469zi591.vicp.fun/api/users/register',
      method: 'POST',
      data: { username, phoneNumber, password },
      header: { 'content-type': 'application/json;charset=utf-8' },
      success: (res) => {
        wx.hideLoading();
        console.log('注册响应:', res.data);

        if (res.data.code) {
          wx.showToast({ title: '注册成功', icon: 'success', duration: 1500 });
          setTimeout(() => {
            wx.navigateTo({ url: '/pages/login/login' });
          }, 1500);
        } else {
          wx.showToast({
            title: res.data.message || '注册失败',
            icon: 'none', duration: 3000
          });
        }
      },
      fail: (err) => {
        wx.hideLoading();
        console.error('请求失败:', err);
        wx.showToast({ title: '网络请求失败，请检查连接', icon: 'none', duration: 3000 });
      }
    });
  }
})