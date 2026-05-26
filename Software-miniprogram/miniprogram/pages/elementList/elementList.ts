import request from "../../utils/request.js";
const { getStaticUrl } = require('../../utils/config.js');

// pages/elementList/elementList.js
Page({
  data: {
    elements: [],
    username: '',
    userId: '',
    loading: true,
    image_ip: getStaticUrl('/images/menu_container1.jpg')
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
    request.get(`/users/getId/${username}`)
      .then((data: any) => {
        wx.hideLoading();
        if (data && data.code === 1) {
          const userId = data.data ? data.data.id : 0;
          app.globalData.userId = userId;
          this.setData({ userId, loading: false });
          this.loadElements();
        } else {
          const msg = data ? (data.message || data.msg || '获取失败') : '服务器无响应';
          wx.showToast({ title: msg, icon: 'none' });
          this.setData({ loading: false });
        }
      })
      .catch((err: any) => {
        wx.hideLoading();
        console.error('请求错误:', err);
        wx.showToast({ title: '请求失败，请检查网络', icon: 'none' });
        this.setData({ loading: false });
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

    request.get(`/events/search/${userId}`)
      .then((data: any) => {
        wx.hideLoading();
        if (data.code === 1) {
          this.setData({ elements: data.data.rows || [] });
        } else {
          wx.showToast({ title: data.msg || '加载失败', icon: 'none' });
        }
      })
      .catch((err: any) => {
        wx.hideLoading();
        console.error('获取事件列表失败:', err);
        wx.showToast({ title: '网络请求失败', icon: 'none' });
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
    request.delete('/events/delete', { eventName, userId: this.data.userId })
      .then((data: any) => {
        wx.hideLoading();
        if (data.code) {
          wx.showToast({ title: '删除成功', icon: 'success' });
          this.loadElements();
        } else {
          wx.showToast({ title: data.msg || '删除失败', icon: 'none' });
        }
      })
      .catch((err: any) => {
        wx.hideLoading();
        console.error('删除失败:', err);
        wx.showToast({ title: '删除失败', icon: 'none' });
      });
  },

  onPullDownRefresh() {
    this.loadElements();
    wx.stopPullDownRefresh();
  }
});
