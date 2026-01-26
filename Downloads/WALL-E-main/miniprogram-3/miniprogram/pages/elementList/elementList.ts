// pages/elementList/elementList.ts
Page({
  data: {
    elements: [] as any[],
    userId: '',
    image_ip: ''
  },

  onLoad() {
    this.loadElements(); // 调取已添加的事件
    this.loadImages();//拿图片
  },

  loadImages(){
    this.setData({
      image_ip:'http://localhost:8080/images/menu_container1.jpg'
    })
  },

  onShow() {
    // 页面显示时重新加载数据
    this.loadElements();
  },

  loadElements() {
    // 获取用户ID
    const app = getApp();
    const userId = app.globalData.userId || wx.getStorageSync('userId');
    
    if (!userId) {
      wx.showToast({
        title: '用户未登录',
        icon: 'none'
      });
      return;
    }

    this.setData({ userId });

    wx.showLoading({
      title: '加载中...'
    });

    // 从后端获取事件列表
    wx.request({
      url: `http://localhost:8080/events/search/${userId}`,
      method: 'GET',
      success: (res: any) => {
        wx.hideLoading();
        console.log('获取事件列表响应:', res.data);

        if (res.data.code === 1) {
          this.setData({
            elements: res.data.data.rows || []
          });
        } else {
          wx.showToast({
            title: res.data.msg || '加载失败',
            icon: 'none'
          });
        }
      },
      fail: (error: any) => {
        wx.hideLoading();
        console.error('获取事件列表失败:', error);
        wx.showToast({
          title: '网络请求失败',
          icon: 'none'
        });
      }
    });
  },

  // 事件项点击
  onEventTap(e: any) {
    const event = e.currentTarget.dataset.event;
    console.log('点击事件:', event);
  },

  // 编辑事件
  onEditTap(e: any) {
    const eventId = e.currentTarget.dataset.id;
    console.log('编辑事件:', eventId);
    
    // 跳转到编辑页面，传递事件ID
    wx.navigateTo({
      url: `/pages/elementUse/elementUse?eventId=${eventId}`
    });
  },

  // 删除事件
  onDeleteTap(e: any) {
    const eventId = e.currentTarget.dataset.id;
    const eventItem = this.data.elements.find(item => item.id === eventId);
    
    if (!eventItem) return;
    const eventName = eventItem.eventName
    console.log(eventName)
    wx.showModal({
      title: '确认删除',
      content: `确定要删除事件"${eventItem.eventName}"吗？`,
      confirmColor: '#ff4757',
      success: (res) => {
        if (res.confirm) {
          this.deleteEvent(eventName);
        }
      }
    });
  },

  // 删除事件请求
  deleteEvent(eventName: string) {
    const userId = this.data.userId;
    wx.showLoading({
      title: '删除中...'
    });

    wx.request({
      url: "http://localhost:8080/events/delete",
      method: 'DELETE',
      data: {
        eventName,
        userId: userId
      },
      header: {
        'content-type': 'application/json'
      },
      success: (res: any) => {
        wx.hideLoading();
        console.log('删除响应:', res.data);
        
        if (res.data.code) {
          wx.showToast({
            title: '删除成功',
            icon: 'success'
          });
          // 重新加载列表
          this.loadElements();
        } else {
          wx.showToast({
            title: res.data.msg || '删除失败',
            icon: 'none'
          });
        }
      },
      fail: (error: any) => {
        wx.hideLoading();
        console.error('删除失败:', error);
        wx.showToast({
          title: '删除失败',
          icon: 'none'
        });
      }
    });
  },

  // 下拉刷新
  onPullDownRefresh() {
    this.loadElements();
    wx.stopPullDownRefresh();
  }
});