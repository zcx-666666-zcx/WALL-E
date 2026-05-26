const { getApiBaseUrl } = require('./config.js');

const request = {
  get(url) {
    return this.request('GET', url);
  },
  post(url, data) {
    return this.request('POST', url, data);
  },
  put(url, data) {
    return this.request('PUT', url, data);
  },
  delete(url, data) {
    return this.request('DELETE', url, data);
  },
  request(method, url, data = undefined) {
    return new Promise((resolve, reject) => {
      const loginUser = wx.getStorageSync('loginUserObject') || {};
      wx.request({
        url: getApiBaseUrl() + url,
        method,
        data,
        header: {
          'Content-Type': 'application/json',
          token: loginUser.token || ''
        },
        success: res => {
          if (res.statusCode === 200) {
            resolve(res.data);
          } else {
            reject(res);
          }
        },
        fail: err => {
          reject(err);
        }
      });
    });
  }
};

export default request;
