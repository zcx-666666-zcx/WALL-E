import request from "../../utils/request.js";
const { getCozeConfig, getStaticUrl } = require('../../utils/config.js');

// pages/agent/agent.js
Page({
  data: {
    user_message: '',
    styleConfig: '',
    messages: [],
    isLoading: false,
    image_ip: ''
  },

  onLoad() {
    this.setData({ styleConfig: '', image_ip: getStaticUrl('/images/menu_container1.jpg') });
  },

  onInputChange(e) {
    this.setData({ user_message: e.detail.value });
  },
  onStyleConfigChange(e) {
    this.setData({ styleConfig: e.detail.value });
  },
  onSendTap() { this.sendMessage(); },
  onConfirm()  { this.sendMessage(); },

  // ══ 提交人设 ══
  submitStyle() {
    const app = getApp();
    const style = this.data.styleConfig;
    if (!style) { wx.showToast({ title: '人设不能为空', icon: 'none' }); return; }
    const coze = getCozeConfig();
    if (!coze.workflowId) {
      wx.showToast({ title: '请先在后台配置 Coze', icon: 'none' });
      return;
    }

    request.post('/coze/workflow/run', {
        workflow_id: coze.workflowId,
        parameters: { username: app.globalData.USERNAME, content: '', style, time: this.formatTime(), set: true, gets: false, del: false }
      })
      .then((res) => {
        if (res.code === 1) { wx.showToast({ title: '设置成功', icon: 'success' }); this.setData({ styleConfig: '' }); }
        else wx.showToast({ title: res.msg || '设置失败', icon: 'none' });
      })
      .catch(() => wx.showToast({ title: '请求失败', icon: 'none' }));
  },

  // ══ 获取当前人设 ══
  getCurrentStyle() {
    const app = getApp();
    const coze = getCozeConfig();
    if (!coze.workflowId) {
      wx.showToast({ title: '请先在后台配置 Coze', icon: 'none' });
      return;
    }
    wx.showToast({ title: '获取中...', icon: 'loading' });
    request.post('/coze/workflow/run', {
        workflow_id: coze.workflowId,
        parameters: { username: app.globalData.USERNAME, content: '', style: '', time: this.formatTime(), set: true, gets: true, del: false }
      })
      .then((res) => {
        if (res.code === 1 && res.data) {
          try {
            const proxyData = JSON.parse(res.data);
            const data = JSON.parse(proxyData.data || '{}');
            this.setData({ styleConfig: data.style || '未获取到人设' });
            wx.showToast({ title: '获取成功', icon: 'success' });
          } catch (e) { wx.showToast({ title: '解析失败', icon: 'none' }); }
        } else wx.showToast({ title: '获取失败', icon: 'none' });
      })
      .catch(() => wx.showToast({ title: '请求失败', icon: 'none' }));
  },

  // ══ 清屏 ══
  clearChat() {
    wx.showModal({
      title: '提示', content: '确定清空聊天记录？',
      success: (res) => { if (res.confirm) this.setData({ messages: [] }); }
    });
  },

  // ══ 删除测试数据 ══
  deleteAllMessages() {
    wx.showModal({
      title: '警告', content: '确定删除全部测试数据？此操作不可撤销',
      confirmColor: '#FF5A36',
      success: (res) => { if (res.confirm) this.setData({ messages: [] }); }
    });
  },

  // ══ 发送消息 ══
  sendMessage() {
    const app = getApp();
    const content = this.data.user_message.trim();
    if (!content) { wx.showToast({ title: '消息不能为空', icon: 'none' }); return; }
    if (this.data.isLoading) return;
    const coze = getCozeConfig();
    if (!coze.workflowId) {
      wx.showToast({ title: '请先在后台配置 Coze', icon: 'none' });
      return;
    }

    this.setData({
      messages: [...this.data.messages, { type: 'user', content }],
      user_message: '',
      isLoading: true
    });

    request.post('/coze/workflow/run', {
        workflow_id: coze.workflowId,
        parameters: { username: app.globalData.USERNAME || '测试', content, style: this.data.styleConfig, time: this.formatTime(), set: true, gets: false, del: false }
      })
      .then((res) => {
        const proxyData = res.code === 1 && res.data ? JSON.parse(res.data) : null;
        const aiContent = (proxyData && proxyData.data)
          ? (JSON.parse(proxyData.data).contentOutput || '暂无回答')
          : '请求失败';
        this.setData({ messages: [...this.data.messages, { type: 'ai', content: aiContent }] });
      })
      .catch(() => {
        this.setData({ messages: [...this.data.messages, { type: 'ai', content: '网络异常，请重试' }] });
      })
      .then(() => { this.setData({ isLoading: false }); }, () => { this.setData({ isLoading: false }); });
  },

  formatTime() {
    const d = new Date();
    const p = n => n < 10 ? '0' + n : '' + n;
    return `${d.getFullYear()}-${p(d.getMonth()+1)}-${p(d.getDate())} ${p(d.getHours())}:${p(d.getMinutes())}`;
  }
});
