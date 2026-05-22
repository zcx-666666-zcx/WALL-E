// pages/elementList/elementList.js
Page({
  data: {
    elements: [],
    username: '',
    userId: '',
    loading: true,
    image_ip: 'https://fm98469zi591.vicp.fun/images/menu_container1.jpg'
  },

  onLoad() {
    this.getId();
  },

  onShow() {
    if (!this.data.loading) {
      this.loadElements();
    }
  },

  getId(){
    const app = getApp();
    const username = app.globalData.USERNAME;
    wx.request({
      url: `https://fm98469zi591.vicp.fun/api/users/getId/${username}`,
      method: 'GET',
      header: { 'content-type': 'application/json' },
      success: (res) => {
        wx.hideLoading();
        if (res.data && res.data.code === 1) {
          const userId = res.data.data ? res.data.data.id : 0;
          app.globalData.userId = userId;
          this.setData({ userId, loading: false });
          this.loadElements();
        } else {
          const msg = res.data ? (res.data.message || '获取失败') : '服务器无响应';
          wx.showToast({ title: msg, icon: 'none' });
          this.setData({ loading: false });
        }
      },
      fail: (err) => {
        wx.hideLoading();
        console.error('请求错误:', err);
        wx.showToast({ title: '请求失败，请检查网络', icon: 'none' });
        this.setData({ loading: false });
      }
    });
  },

  loadElements() {
    const userId = this.data.userId;

    if (!userId) {
      wx.showToast({ title: '用户未登录', icon: 'none' });
      return;
    }
    this.setData({ userId });
    wx.showLoading({ title: '加载中...' });

    wx.request({
      url: `https://fm98469zi591.vicp.fun/api/events/search/${userId}`,
      method: 'GET',
      success: (res) => {
        wx.hideLoading();
        if (res.data.code === 1) {
          this.setData({ elements: res.data.data.rows || [] });
        } else {
          wx.showToast({ title: res.data.msg || '加载失败', icon: 'none' });
        }
      },
      fail: (err) => {
        wx.hideLoading();
        console.error('获取事件列表失败:', err);
        wx.showToast({ title: '网络请求失败', icon: 'none' });
      }
    });
  },

  onEventTap(e) {
    console.log('点击事件:', e.currentTarget.dataset.event);
  },

  onEditTap(e) {
    const eventId = e.currentTarget.dataset.id;
    wx.navigateTo({ url: `/pages/elementUse/elementUse?eventId=${eventId}` });
  },

  onDeleteTap(e) {
    const eventId = e.currentTarget.dataset.id;
    const eventItem = this.data.elements.find(item => item.id === eventId);
    if (!eventItem) return;

    wx.showModal({
      title: '确认删除',
      content: `确定要删除「${eventItem.eventName}」吗？`,
      confirmColor: '#FF5A36',
      success: (res) => {
        if (res.confirm) this.deleteEvent(eventItem.eventName);
      }
    });
  },

  deleteEvent(eventName) {
    wx.showLoading({ title: '删除中...' });
    wx.request({
      url: 'https://fm98469zi591.vicp.fun/api/events/delete',
      method: 'DELETE',
      data: { eventName, userId: this.data.userId },
      header: { 'content-type': 'application/json;charset=utf-8' },
      success: (res) => {
        wx.hideLoading();
        if (res.data.code) {
          wx.showToast({ title: '删除成功', icon: 'success' });
          this.loadElements();
        } else {
          wx.showToast({ title: res.data.msg || '删除失败', icon: 'none' });
        }
      },
      fail: (err) => {
        wx.hideLoading();
        console.error('删除失败:', err);
        wx.showToast({ title: '删除失败', icon: 'none' });
      }
    });
  },

  onPullDownRefresh() {
    this.loadElements();
    wx.stopPullDownRefresh();
  }
});