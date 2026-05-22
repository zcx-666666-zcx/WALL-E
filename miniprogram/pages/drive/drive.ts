// pages/drive/drive.js
Page({
  data: {
    is_connect: "未连接",
    vedio_connect: "未连接",
    left_isPressing:  false,
    right_isPressing: false,
    go_isPressing:    false,
    back_isPressing:  false,
    up_isPressing:    false,
    down_isPressing:  false,
    image_ip: ''
  },

  onLoad() {
    this.call_camera();
    this.connect_video();
    this.loadImages();
  },

  loadImages() {
    this.setData({ image_ip: 'https://fm98469zi591.vicp.fun/images/menu_container1.jpg' });
  },

  call_camera()  {},
  connect_video() {},

  /* ══ 左转 ══ */
  onButtonPress_left()   { this.setData({ left_isPressing: true });  this.start(); },
  onButtonRelease_left() { this.setData({ left_isPressing: false }); },

  /* ══ 右转 ══ */
  onButtonPress_right()   { this.setData({ right_isPressing: true });  this.start(); },
  onButtonRelease_right() { this.setData({ right_isPressing: false }); },

  /* ══ 前进 ══ */
  onButtonPress_go()   { this.setData({ go_isPressing: true });  this.start(); },
  onButtonRelease_go() { this.setData({ go_isPressing: false }); },

  /* ══ 后退 ══ */
  onButtonPress_back()   { this.setData({ back_isPressing: true });  this.start(); },
  onButtonRelease_back() { this.setData({ back_isPressing: false }); },

  /* ══ 抬头 ══ */
  onButtonPress_up()   { this.setData({ up_isPressing: true });  this.start(); },
  onButtonRelease_up() { this.setData({ up_isPressing: false }); },

  /* ══ 低头 ══ */
  onButtonPress_down()   { this.setData({ down_isPressing: true });  this.start(); },
  onButtonRelease_down() { this.setData({ down_isPressing: false }); },

  /* ══ 行动控制 ══ */
  start() {
    // 在此处填写实际控制逻辑
  }
});