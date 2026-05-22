const baseURL = 'https://fm98469zi591.vicp.fun/api';

const request = {
  get(url) {
    return new Promise((resolve, reject) => {
      wx.request({
        url: baseURL + url,
        method: 'GET',
        header: {
          'Content-Type': 'application/json'
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