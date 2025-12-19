/**
 * 用户认证工具函数
 */

/**
 * 微信登录
 */
const wxLogin = () => {
  return new Promise((resolve, reject) => {
    wx.login({
      success: res => {
        if (res.code) {
          // 发送 res.code 到后台换取 openId, sessionKey, unionId
          resolve(res.code);
        } else {
          reject(res);
        }
      },
      fail: err => {
        reject(err);
      }
    });
  });
};

/**
 * 用户名密码登录
 * @param {Object} loginData 登录数据
 */
const loginWithUsername = (loginData) => {
  return new Promise((resolve, reject) => {
    wx.request({
      url: 'http://localhost:8001/api/auth/login',
      method: 'POST',
      data: {
        username: loginData.username,
        password: loginData.password
      },
      header: {
        'content-type': 'application/json'
      },
      success(res) {
        if (res.statusCode === 200 && res.data.success) {
          // 存储token和用户信息
          wx.setStorageSync('token', res.data.token);
          wx.setStorageSync('userInfo', res.data.user);
          resolve(res.data);
        } else {
          reject(res.data);
        }
      },
      fail(err) {
        reject(err);
      }
    });
  });
};

/**
 * 用户登录到后端系统
 * @param {Object} userInfo 用户信息
 */
const loginToBackend = (userInfo) => {
  return new Promise((resolve, reject) => {
    wx.request({
      url: 'http://localhost:8001/api/auth/login',
      method: 'POST',
      data: {
        openid: userInfo.openid || '',
        nickname: userInfo.nickName || '',
        avatarUrl: userInfo.avatarUrl || '',
        gender: userInfo.gender || '',
        country: userInfo.country || '',
        province: userInfo.province || '',
        city: userInfo.city || '',
        language: userInfo.language || ''
      },
      header: {
        'content-type': 'application/json'
      },
      success(res) {
        if (res.statusCode === 200 && res.data.success) {
          // 存储token和用户信息
          wx.setStorageSync('token', res.data.token);
          wx.setStorageSync('userInfo', res.data.user);
          resolve(res.data);
        } else {
          reject(res.data);
        }
      },
      fail(err) {
        reject(err);
      }
    });
  });
};

/**
 * 用户注册
 * @param {Object} registerData 注册数据
 */
const registerUser = (registerData) => {
  return new Promise((resolve, reject) => {
    wx.request({
      url: 'http://localhost:8001/api/auth/register',
      method: 'POST',
      data: {
        username: registerData.username,
        password: registerData.password,
        email: registerData.email
      },
      header: {
        'content-type': 'application/json'
      },
      success(res) {
        if (res.statusCode === 200 && res.data.success) {
          // 存储token和用户信息
          wx.setStorageSync('token', res.data.token);
          wx.setStorageSync('userInfo', res.data.user);
          resolve(res.data);
        } else {
          reject(res.data);
        }
      },
      fail(err) {
        reject(err);
      }
    });
  });
};

/**
 * 用户登出
 */
const logout = () => {
  wx.removeStorageSync('token');
  wx.removeStorageSync('userInfo');
};

/**
 * 检查是否已登录
 */
const isLoggedIn = () => {
  return !!wx.getStorageSync('token');
};

/**
 * 获取当前用户信息
 */
const getCurrentUser = () => {
  return wx.getStorageSync('userInfo');
};

module.exports = {
  wxLogin,
  loginWithUsername,
  loginToBackend,
  registerUser,
  logout,
  isLoggedIn,
  getCurrentUser
};