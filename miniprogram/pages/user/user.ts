// pages/user/user.ts
Page({
  data: { 
    username:'',
    username_style: '',
    is_exit: false,
    image_ip: ''
  },

  onLoad() {
    this.getName();//拿名字
    this.loadImages();//拿图片
  },

  loadImages(){
    this.setData({
      image_ip:'http://localhost:8080/images/menu_container1.jpg'
    })
  },

  getName(){
    const app = getApp();
    if(app.globalData.USERNAME){
      this.setData({username: app.globalData.USERNAME});
    }
    else{
      wx.showToast({
        title: '数据异常，请检查登陆状态或网络连接',
        icon: 'none'
      })
      this.setData({
        username: "数据异常，请检查登陆状态或网络连接",
        username_style: "color: red"
      });
    }
  },//拿名字

  exit(){
    const app = getApp();
    this.setData({
      username: ''
    })
    wx.navigateTo({
      url: '/pages/index/index'
    })
  },//退出登录
})