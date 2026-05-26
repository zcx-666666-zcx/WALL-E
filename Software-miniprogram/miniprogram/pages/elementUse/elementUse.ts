import request from "../../utils/request.js";

Page({
  data: {
    eventName: '',
    eventDate: '',
    eventTime: '',
    description: '',
    machines: '',
    repeatOptions: [] as string[],
    repeatIndex: 0,
    priorityIndex: 1, //默认选中优先级
    userId: '' // 添加用户ID
  },

  onLoad(options: any) {
    this.creatChoice(); //生成选项
    // 从全局数据或本地存储获取用户ID
    const app = getApp();
    this.setData({
      userId: app.globalData.userId || wx.getStorageSync('userId')
    });
  },

  creatChoice() {
    const repeatOptions = [];
    for (let i = 1; i <= 365; i++) {
      repeatOptions.push(`每${i}天提醒一次`);
    }
    this.setData({
      repeatOptions: repeatOptions
    });
  }, //选项生成器

  machines_input(e: any){
    this.setData({
      machines: e.detail.value
    })
  },

  event_name_input(e: any) {
    this.setData({
      eventName: e.detail.value
    });
  },//事件名称输入
  event_info_input(e: any) {
    this.setData({
      description: e.detail.value
    });
  },//事件描述输入
  onRepeatChange(e: any) {
    this.setData({
      repeatIndex: parseInt(e.detail.value)
    });
  },//重复提醒选择变化
  eventDateInput(e: any) {
    this.setData({
      eventDate: e.detail.value
    });
  },//事件日期选择变化
  eventTimeInput(e: any) {
    this.setData({
      eventTime: e.detail.value
    });
  },//事件时间选择变化
  onPriorityChange(e: any) {
    const index = parseInt(e.currentTarget.dataset.index);
    this.setData({
      priorityIndex: index
    });
  },//优先级选择变化

  //保存事件
  save_event() {
    const { 
      eventName, 
      eventDate, 
      eventTime, 
      repeatIndex, 
      priorityIndex,
      machines,
      description, 
      userId
    } = this.data;

    //验证
    if (!eventName.trim()) {
      wx.showToast({
        title: '请输入事件名称',
        icon: 'none'
      });
      return;
    }
    if (!eventDate) {
      wx.showToast({
        title: '请选择日期',
        icon: 'none'
      });
      return;
    }
    if (!eventTime) {
      wx.showToast({
        title: '请选择时间',
        icon: 'none'
      });
      return;
    }
    if (!userId) {
      wx.showToast({
        title: '用户未登录',
        icon: 'none'
      });
      return;
    }

    // 优先级映射
    const priorityMap = ['LOW', 'MEDIUM', 'HIGH'];
    
    //构造事件对象
    const eventData = {
      eventName: eventName,
      eventDate: eventDate,
      eventTime: eventTime,
      repeatDays: repeatIndex + 1, // 0表示不重复，其他表示重复天数
      priority: priorityMap[priorityIndex], // 转换为后端枚举值
      machines: machines,
      description: description,
      userId: userId
    };

    console.log('保存的事件数据:', eventData);
    
    wx.showLoading({
      title: '保存中...'
    });

    request.post('/events/add', eventData)
      .then((data: any) => {
        wx.hideLoading();
        console.log('保存响应:', data);

        if (data.code) {
          wx.showToast({
            title: '保存成功',
            icon: 'success',
            duration: 2000,
            success: () => {
              // 延迟返回上一页
              setTimeout(() => {
                wx.navigateBack();
              }, 2000);
            }
          });
        } else {
          wx.showToast({
            title: data.message || data.msg || '保存失败',
            icon: 'none',
            duration: 3000
          });
        }
      })
      .catch((error: any) => {
        wx.hideLoading();
        console.error('请求失败:', error);
        wx.showToast({
          title: '网络请求失败',
          icon: 'none',
          duration: 3000
        });
      });
  }
});
