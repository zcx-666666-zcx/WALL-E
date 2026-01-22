// pages/drive/drive.ts
Page({
  data: {
    is_connect:"未连接",
    vedio_connect:"未连接",
    left_isPressing:false,
    left_timer:null,
    right_isPressing:false,
    right_timer:null,
    go_isPressing:false,
    go_timer:null,
    back_isPressing:false,
    back_timer:null,
    up_isPressing:false,
    up_timer:null,
    down_isPressing:false,
    down_timer:null,
    image_ip: ''

  },
  onLoad(){
    this.call_camera();//唤醒机器人
    this.connect_video();//连接视频
    this.loadImages();//拿图片
  },
  loadImages(){
    this.setData({
      image_ip:'http://localhost:8080/images/menu_container1.jpg'
    })
  },

  call_camera(){},
  connect_video(){},

//↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓遥控操作↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓
  //左转
  onButtonPress_left(){
    this.setData({left_isPressing:true});
    this.start();
  },
  onButtonRelease_left(){
    this.setData({right_isPressing:false})
  },

  //右转
  onButtonPress_right(){
    this.setData({right_isPressing:true});
    this.start();
  },
  onButtonRelease_right(){
    this.setData({right_isPressing:false})
  },

  //前进
  onButtonPress_go(){
    this.setData({go_isPressing:true});
    this.start();
  },
  onButtonRelease_go(){
    this.setData({go_isPressing:false})
  },

  //后退
  onButtonPress_back(){
    this.setData({back_isPressing:true});
    this.start();
  },
  onButtonRelease_back(){
    this.setData({back_isPressing:false})
  },

  //抬头
  onButtonPress_up(){
    this.setData({up_isPressing:true});
    this.start();
  },
  onButtonRelease_up(){
    this.setData({up_isPressing:false})
  },

  //低头
  onButtonPress_down(){
    this.setData({down_isPressing:true});
    this.start();
  },
  onButtonRelease_down(){
    this.setData({down_isPressing:false})
  },

  //行动控制函数
  start(){

  },

})