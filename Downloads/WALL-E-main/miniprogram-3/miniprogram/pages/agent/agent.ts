Page({
  data: {
    messages: [
      {
        type: 'ai',
        content: '你好呀'
      }
    ],
    user_message: '',
    styleConfig: ''
  },

  onLoad() {
    //页面加载时的初始化
  },

  onInputChange(e: any) {
    this.setData({
      user_message: e.detail.value
    });
  },//监听用户输入

  onStyleConfigChange(e: any) {
    this.setData({
      styleConfig: e.detail.value
    });
  },//监听风格设置输入

  //发送消息
  sendMessage() {
    const message = this.data.user_message.trim();
    if (!message) {
      wx.showToast({
        title: '消息不能为空',
        icon: 'none'
      });
      return;
    }
    //添加用户消息到列表
    const userMsg = {
      type: 'user',
      content: message
    };

    this.setData({
      messages: [...this.data.messages, userMsg],
      user_message: '' //清空输入框
    });

    // 模拟AI回复（实际开发中这里应该是调用API）
    setTimeout(() => {
      const aiMsg = {
        type: 'ai',
        content: this.getAIResponse(message)
      };
      
      this.setData({
        messages: [...this.data.messages, aiMsg]
      });

      //滚动到底部
      this.scrollToBottom();
    }, 500);
  },

  // 模拟AI回复,应替换为真实的API调用
  getAIResponse(userMessage: string): string {
    // 可以根据styleConfig来调整回复风格
    const style = this.data.styleConfig;
    
    if (style.includes('幽默')) {
      return `用户说："${userMessage}"\n哈哈，这个问题真有趣！让我用幽默的方式回答你~`;
    } else if (style.includes('专业') || style.includes('学术')) {
      return `关于"${userMessage}"的问题，从专业角度分析，我认为...`;
    } else {
      return `收到你的消息："${userMessage}"。这是我根据当前设置的回复风格给出的回答。`;
    }
  },

  //提交风格设置
  submitStyle(e: any) {
    const styleConfig = e.detail.value.styleConfig.trim();
    if (!styleConfig) {
      wx.showToast({
        title: '请输入风格设置',
        icon: 'none'
      });
      return;
    }

    this.setData({
      styleConfig: styleConfig
    });

    wx.showToast({
      title: '风格设置成功',
      icon: 'success'
    });

    //添加系统提示消息
    const systemMsg = {
      type: 'ai',
      content: `聊天风格已更新为：${styleConfig}`
    };

    this.setData({
      messages: [...this.data.messages, systemMsg]
    });

    this.scrollToBottom();
  },
  //滚动到底部
  scrollToBottom() {
    setTimeout(() => {
      wx.createSelectorQuery()
        .select('.talk')
        .boundingClientRect()
        .exec((res) => {
          if (res[0]) {
            wx.pageScrollTo({
              scrollTop: res[0].height,
              duration: 300
            });
          }
        });
    }, 100);
  },

  // 点击发送按钮
  onSendTap() {
    this.sendMessage();
  },

  // 文本框确认发送（点击键盘发送按钮）
  onConfirm() {
    this.sendMessage();
  }
});