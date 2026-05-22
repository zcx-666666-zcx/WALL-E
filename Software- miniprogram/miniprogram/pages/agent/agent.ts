// pages/agent/agent.js
Page({
  data: {
    user_message: '',
    styleConfig: '',
    messages: [],
    isLoading: false,
    image_ip: 'https://fm98469zi591.vicp.fun/images/menu_container1.jpg'
  },

  onLoad() {
    this.setData({ styleConfig: '' });
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

    wx.request({
      url: 'https://api.coze.cn/v1/workflow/run',
      method: 'POST',
      header: { 'Content-Type': 'application/json', 'Authorization': `Bearer pat_hGQLZyKcpFQxn88rubPnaAodHjXbLmznqvdNvQtY5IqOMGYl9xi2eoXAKKkjtlVo` },
      data: {
        workflow_id: '7598072302836482048',
        parameters: { username: app.globalData.USERNAME, content: '', style, time: this.formatTime(), set: true, gets: false, del: false }
      },
      success: (res) => {
        if (res.statusCode === 200) { wx.showToast({ title: '设置成功', icon: 'success' }); this.setData({ styleConfig: '' }); }
        else wx.showToast({ title: '设置失败', icon: 'none' });
      },
      fail: () => wx.showToast({ title: '请求失败', icon: 'none' })
    });
  },

  // ══ 获取当前人设 ══
  getCurrentStyle() {
    const app = getApp();
    wx.showToast({ title: '获取中...', icon: 'loading' });
    wx.request({
      url: 'https://api.coze.cn/v1/workflow/run',
      method: 'POST',
      header: { 'Content-Type': 'application/json', 'Authorization': `Bearer pat_hGQLZyKcpFQxn88rubPnaAodHjXbLmznqvdNvQtY5IqOMGYl9xi2eoXAKKkjtlVo` },
      data: {
        workflow_id: '7598072302836482048',
        parameters: { username: app.globalData.USERNAME, content: '', style: '', time: this.formatTime(), set: true, gets: true, del: false }
      },
      success: (res) => {
        if (res.statusCode === 200 && res.data.data) {
          try {
            const data = JSON.parse(res.data.data);
            this.setData({ styleConfig: data.style || '未获取到人设' });
            wx.showToast({ title: '获取成功', icon: 'success' });
          } catch (e) { wx.showToast({ title: '解析失败', icon: 'none' }); }
        } else wx.showToast({ title: '获取失败', icon: 'none' });
      },
      fail: () => wx.showToast({ title: '请求失败', icon: 'none' })
    });
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

    this.setData({
      messages: [...this.data.messages, { type: 'user', content }],
      user_message: '',
      isLoading: true
    });

    wx.request({
      url: 'https://api.coze.cn/v1/workflow/run',
      method: 'POST',
      header: { 'Content-Type': 'application/json', 'Authorization': `Bearer pat_hGQLZyKcpFQxn88rubPnaAodHjXbLmznqvdNvQtY5IqOMGYl9xi2eoXAKKkjtlVo` },
      data: {
        workflow_id: '7598072302836482048',
        parameters: { username: app.globalData.USERNAME || '测试', content, style: this.data.styleConfig, time: this.formatTime(), set: true, gets: false, del: false }
      },
      success: (res) => {
        const aiContent = (res.statusCode === 200 && res.data.data)
          ? (JSON.parse(res.data.data).contentOutput || '暂无回答')
          : '请求失败';
        this.setData({ messages: [...this.data.messages, { type: 'ai', content: aiContent }] });
      },
      fail: () => {
        this.setData({ messages: [...this.data.messages, { type: 'ai', content: '网络异常，请重试' }] });
      },
      complete: () => { this.setData({ isLoading: false }); }
    });
  },

  formatTime() {
    const d = new Date();
    const p = n => n < 10 ? '0' + n : '' + n;
    return `${d.getFullYear()}-${p(d.getMonth()+1)}-${p(d.getDate())} ${p(d.getHours())}:${p(d.getMinutes())}`;
  }
});