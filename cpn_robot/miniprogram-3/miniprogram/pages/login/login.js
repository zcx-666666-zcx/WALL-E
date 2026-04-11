Page({
  data: {
    login_username: '',
    login_password: '',
    image_ip1: '',
    image_ip2: ''
  },

  onLoad(){
    this.setData({
      image_ip1:'http://localhost:8080/images/index_container1.png',
      image_ip2:'http://localhost:8080/images/index_picture.png'
    })
  },

  // 输入用户名
  login_usernameInput(e) {
    this.setData({ login_username: e.detail.value });
  },

  // 输入密码
  login_passwordInput(e) {
    this.setData({ login_password: e.detail.value });
  },

  
  // 登录方法
  Gologin() {
    const { login_username, login_password } = this.data;

    // 简单校验
    if (!login_username || !login_password) {
      wx.showToast({
        title: '请输入完整内容',
        icon: 'none'
      });
      return;
    }

    wx.showLoading({ title: '登录中...', mask: true });

    wx.request({
      url: 'http://localhost:8080/login',
      method: 'POST',
      data: {
        username: login_username,
        password: login_password
      },
      header: {
        'content-type': 'application/json'
      },
      success: (res) => {
        wx.hideLoading();
        console.log('登录响应:', res); // 添加日志以便调试
        
        if (res.data && res.data.code) {
          wx.showToast({ title: '登录成功', icon: 'success' });
          wx.setStorageSync('username', login_username);
          
          // 设置全局变量
          const app = getApp();
          const userId = res.data.data ? res.data.data.id : null;
          app.globalData.USERNAME = login_username;
          app.globalData.USER_ID = userId;
          
          // 同时将用户ID保存到本地存储
          if (userId) {
            wx.setStorageSync('userId', userId);
          }

          // 检查是否真的获取到了用户ID
          if (!app.globalData.USER_ID) {
            console.warn('警告：登录响应中未包含用户ID');
          }

          // 延迟跳转以确保提示显示
          setTimeout(() => {
            wx.switchTab({
              url: '/pages/menu/menu',
              fail: function() {
                wx.navigateTo({ 
                  url: '/pages/menu/menu',
                  fail: function(err) {
                    console.error('跳转失败:', err);
                    wx.showToast({ title: '跳转失败', icon: 'none' });
                  }
                });
              }
            });
          }, 1500);
        } else {
          const errorMessage = res.data ? (res.data.message || '登录失败') : '服务器无响应';
          wx.showToast({ title: errorMessage, icon: 'none' });
        }
      },
      fail: (err) => {
        wx.hideLoading();
        console.error('请求错误:', err);
        wx.showToast({ title: '请求失败，请检查网络和服务器状态', icon: 'none' });
      }
    });
  }
})