// pages/login/login.js
import { loginToBackend, loginWithUsername } from '../../utils/auth.js'

Page({
  data: {
    currentTab: 0, // 0: 账号登录, 1: 微信登录
    username: '',
    password: '',
    canIUseGetUserProfile: false,
    tempLoginCode: '',
    logoUrl: 'http://localhost:8001/uploads/login-bg.png.png' 
  },

  onLoad: function () {
    this.setData({
      canIUseGetUserProfile: wx.canIUse('getUserProfile')
    })
  },

  switchTab: function(e) {
    const tab = parseInt(e.currentTarget.dataset.tab);
    this.setData({
      currentTab: tab
    });
  },

  goToRegister: function() {
    wx.navigateTo({
      url: '../register/register'
    });
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

  onLogin: function () {
    const { username, password } = this.data;
    
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
    
    // 发送登录请求到后端
    loginWithUsername({
      username: username,
      password: password
    }).then((res) => {
      wx.showToast({
        title: '登录成功',
        icon: 'success'
      });

      // 延迟跳转到首页
      setTimeout(() => {
        wx.switchTab({
          url: '../index/index'
        })
      }, 1000)
    }).catch((err) => {
      wx.showToast({
        title: err.error || '登录失败',
        icon: 'none'
      })
    });
  },

  onWechatLogin: function () {
    wx.login({
      success: (res) => {
        if (res.code) {
          // 使用微信用户信息接口（适用于较新版本）
          if (this.data.canIUseGetUserProfile) {
            // 保存登录code，等待用户点击授权按钮
            this.setData({
              tempLoginCode: res.code
            });
            
            // 显示提示信息，让用户知道需要授权
            wx.showModal({
              title: '需要授权',
              content: '为了更好的体验，需要获取您的头像和昵称信息',
              showCancel: true,
              confirmText: '去授权',
              success: (modalRes) => {
                if (modalRes.confirm) {
                  this.onGetUserProfile();
                }
              }
            });
          } else {
            // 兼容旧版本
            wx.getUserInfo({
              success: (userInfos) => {
                // 将微信登录code和用户信息发送到后端
                this.loginToServer(res.code, userInfos.userInfo)
              },
              fail: (err) => {
                console.error('获取用户信息失败', err)
                wx.showToast({
                  title: '登录失败',
                  icon: 'none'
                })
              }
            })
          }
        } else {
          console.log('登录失败！' + res.errMsg)
          wx.showToast({
            title: '登录失败',
            icon: 'none'
          })
        }
      },
      fail: (err) => {
        console.error('微信登录失败', err)
        wx.showToast({
          title: '微信登录失败',
          icon: 'none'
        })
      }
    })
  },
  
  onGetUserProfile: function () {
    const that = this;
    wx.getUserProfile({
      desc: '用于完善会员资料',
      success: (userProfileRes) => {
        // 将微信登录code和用户信息发送到后端
        that.loginToServer(that.data.tempLoginCode, userProfileRes.userInfo)
      },
      fail: (err) => {
        console.error('获取用户信息失败', err)
        wx.showToast({
          title: '授权失败',
          icon: 'none'
        })
      }
    })
  },

  loginToServer: function (code, userInfo) {
    // 添加openid到用户信息中
    const loginData = {
      ...userInfo,
      openid: code // 在实际应用中，应该将code发送到自己的服务器换取openid
    }

    // 登录到后端系统
    loginToBackend(loginData)
      .then((res) => {
        wx.showToast({
          title: '登录成功',
          icon: 'success'
        })

        // 延迟跳转到首页
        setTimeout(() => {
          wx.switchTab({
            url: '../index/index'
          })
        }, 1000)
      })
      .catch((err) => {
        console.error('后端登录失败', err)
        wx.showToast({
          title: '登录失败',
          icon: 'none'
        })
      })
  }
})