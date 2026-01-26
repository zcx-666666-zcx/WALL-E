// pages/menu/menu.ts
Page({
  data: {
    username:"null",
    day_time:"",
    energy:80,
    image_ip:''

  },
  onLoad(){
    this.getTime();//拿时间
    this.getUsername();//拿名字
    this.loadImages();//拿图片
    //尝试与机器人取得连接，获取电量
  },
  loadImages(){
    this.setData({
      image_ip:'http://localhost:8080/images/menu_container1.jpg'
    })
  },

  getTime(){
    const now = new Date();
    const hours = now.getHours().toString().padStart(2,'0');
//    const minutes = now.getMinutes().toString().padStart(2,'0');获取分钟
//    const seconds = now.getSeconds().toString().padStart(2,'0');获取秒
//    const time_string = `${hours}:${minutes}:${seconds}`;转换成00:00:00形式
    if(hours<=7){
      this.setData({day_time:"早上"})
    }else if(hours<=11){
      this.setData({day_time:"上午"})
    }else if(hours<=13){
      this.setData({day_time:"中午"})
    }else if(hours<=17){
      this.setData({day_time:"下午"})
    }else{
      this.setData({day_time:"晚上"})
    }
  },//拿时间
  getUsername(){
    const app = getApp();
    if(app.globalData.USERNAME){
      this.setData({
        username:app.globalData.USERNAME
      })
    }
    else{
      wx.showToast({
        title: '信息异常',
        icon: 'none'
      })
    }
  }//拿名字
  
})