// pages/register/register.js
Page({
  data: {
    username: '',
    password: '',
    confirmPassword: '',
    email: '',
    logoUrl: 'http://localhost:8001/uploads/login-bg.png.png'
  },

  onUsernameInput: function(e) {
    this.setData({
      username: e.detail.value
    });
  },

  onPasswordInput: function(e) {
    this.setData({
      password: e.detail.value
    });
  },

  onConfirmPasswordInput: function(e) {
    this.setData({
      confirmPassword: e.detail.value
    });
  },

  onEmailInput: function(e) {
    this.setData({
      email: e.detail.value
    });
  },

  goToLogin: function() {
    wx.navigateBack();
  },

  onRegister: function() {
    const { username, password, confirmPassword, email } = this.data;
    
    // 基本验证
    if (!username) {
      wx.showToast({
        title: '请输入用户名',
        icon: 'none'
      });
      return;
    }
    
    if (!password) {
      wx.showToast({
        title: '请输入密码',
        icon: 'none'
      });
      return;
    }
    
    if (password !== confirmPassword) {
      wx.showToast({
        title: '两次输入的密码不一致',
        icon: 'none'
      });
      return;
    }
    
    // 发送注册请求到后端
    wx.request({
      url: 'http://localhost:8080/api/auth/register',
      method: 'POST',
      data: {
        username: username,
        password: password,
        email: email
      },
      header: {
        'content-type': 'application/json'
      },
      success: (res) => {
        if (res.statusCode === 200 && res.data.success) {
          wx.showToast({
            title: '注册成功',
            icon: 'success'
          });
          
          // 延迟跳转到登录页
          setTimeout(() => {
            wx.redirectTo({
              url: '../login/login'
            });
          }, 1500);
        } else {
          wx.showToast({
            title: res.data.error || '注册失败',
            icon: 'none'
          });
        }
      },
      fail: (err) => {
        console.error('注册请求失败', err);
        wx.showToast({
          title: '注册失败，请检查网络',
          icon: 'none'
        });
      }
    });
  }
});