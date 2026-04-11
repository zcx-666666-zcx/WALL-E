Page({
  data: {
    username: '',
    password: '',
    surePassword: '',
    phoneNumber: '',
    showError: false,
    image_ip1: '',
    image_ip2: ''
  },

  onLoad(){
    this.setData({
      image_ip1:'http://localhost:8080/images/index_container1.png',
      image_ip2:'http://localhost:8080/images/index_picture.png'

    })
  },

  nameHandle(e) {
    this.setData({ username: e.detail.value });
  },
  passwordHandle(e) {
    this.setData({ password: e.detail.value });
  },
  sureHandle(e) {
    this.setData({ surePassword: e.detail.value });
  },
  phone_numberHandle(e){
    this.setData({ phoneNumber: e.detail.value });
  },

  GoRegist() {
    const { username, password, surePassword, phoneNumber } = this.data;

    // 验证逻辑保持不变...
    if (!username || !password || !surePassword || !phoneNumber) {
        this.setData({ showError: true });
        wx.showToast({ title: '请输入完整内容', icon: 'none' });
        return;
    }

    if (password !== surePassword) {
        this.setData({ showError: true });
        wx.showToast({ title: '密码输入不一致', icon: 'none' });
        return;
    }

    const phoneRegex = /^1[3-9]\d{9}$/;
    if (!phoneRegex.test(phoneNumber)) {
        this.setData({ showError: true });
        wx.showToast({ title: '请输入正确的手机号', icon: 'none' });
        return;
    }

    wx.showLoading({ title: '注册中...' });
    
    wx.request({
        url: 'http://localhost:8080/users/register', // 你的后端地址
        method: 'POST',
        data: { 
            username: username, 
            phoneNumber: phoneNumber, 
            password: password
        },
        header: {
            'content-type': 'application/json'
        },
        success: (res) => {
            wx.hideLoading();
            console.log('注册响应:', res.data);
            
            if (res.data.code) {
                wx.showToast({ 
                    title: '注册成功', 
                    icon: 'success',
                    duration: 1500 
                });
                
                setTimeout(() => {
                    wx.navigateTo({
                      url: '/pages/login/login',
                    });
                }, 1500);
            } else {
                wx.showToast({ 
                    title: res.data.message || '注册失败', 
                    icon: 'none',
                    duration: 3000 
                });
            }
        },
        fail: (error) => {
            wx.hideLoading();
            console.error('请求失败:', error);
            wx.showToast({ 
                title: '网络请求失败，请检查服务器连接', 
                icon: 'none',
                duration: 3000 
            });
        }
    });
}
});