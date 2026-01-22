// pages/agent/agent.ts
Page({
  data: {
    user_message: '',
    styleConfig: '',
    messages: [] as Array<{ type: 'user' | 'ai', content: any }>,
    isLoading: false,
  },

  onLoad() {
    this.setData({
      styleConfig: ''
    });
  },

  onInputChange(e: any) {
    this.setData({
      user_message: e.detail.value
    });
  },

  onStyleConfigChange(e: any) {
    this.setData({
      styleConfig: e.detail.value
    });
  },

  onSendTap() {
    this.sendMessage();
  },

  onConfirm() {
    this.sendMessage();
  },

  //提交风格
  submitStyle(e: any) {
    const app = getApp();
    const style = this.data.styleConfig;
    const username = app.globalData.USERNAME;
    const content = "";
    const time = this.formatTime()

    if(!style){
      wx.showToast({
        title: '风格不能为空',
        icon: 'none'
      })
      return;
    }

    wx.request({
      url: 'https://api.coze.cn/v1/workflow/run',
      method: 'POST',
      header: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer pat_qjJdH6KguUMKmyhr9uDIr38KxfHVL9eMSfRHVOZKUiKujB4TWcKAvZfzsxbRIQuJ`
      },
      data: {
        workflow_id: '7598072302836482048',
        parameters: {
          username,
          content,
          style,
          time
        },
      },
      success:(res)=>{
        if (res.statusCode === 200){
          wx.showToast({
            title: '设置成功',
            icon: 'none'
          })
          this.setData({
            styleConfig: ''
          })
        }
        else{
          wx.showToast({
            title: '设置失败',
            icon: 'none'
          })
        }
      },
      fail:(err)=>{
        wx.showToast({
          title: '请求错误',
          icon: 'none'
        })
      }
    })
  },

  //获取当前时间
  formatTime(): string {
    const date = new Date();
    const addZero = (num: number) => {
      return num < 10 ? '0' + num : num.toString();
    };

    const year = date.getFullYear();
    const month = addZero(date.getMonth() + 1);
    const day = addZero(date.getDate());
    const hours = addZero(date.getHours());
    const minutes = addZero(date.getMinutes());
    const seconds = addZero(date.getSeconds());
    return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
  },

  //发送信息
  sendMessage() {
    const app = getApp();
    const username = app.globalData.USERNAME || '测试1';
    const content = this.data.user_message.trim();
    const styleConfig = this.data.styleConfig.trim();

    if (!content) {
      wx.showToast({
        title: '消息内容不能为空',
        icon: 'none'
      });
      return;
    }
    if (this.data.isLoading) return;

    //添加用户消息到列表
    const userMsg = {
      type: 'user' as const,
      content
    };
    this.setData({
      messages: [...this.data.messages, userMsg],
      user_message: '',
      isLoading: true
    });
    
    const style = this.data.styleConfig;
    const time = this.formatTime()
    wx.request({
      url: 'https://api.coze.cn/v1/workflow/run',
      method: 'POST',
      header: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer pat_qjJdH6KguUMKmyhr9uDIr38KxfHVL9eMSfRHVOZKUiKujB4TWcKAvZfzsxbRIQuJ`
      },
      data: {
        workflow_id: '7598072302836482048',
        parameters: {
          username,
          content,
          style,
          time
        },
      },
      
      success: (res) => {
        if (res.statusCode === 200 && res.data) {
          const aiContent = res.data.data;
          console.log(aiContent);
          const A = JSON.parse(aiContent);
          const AI = A.contentOutput;
          this.setData({
            messages: [...this.data.messages, { type: 'ai', content: AI }]
          });
        } else {
          wx.showToast({
            title: '请求失败：' + res.statusCode,
            icon: 'none'
          });
          this.setData({
            messages: [...this.data.messages, { type: 'ai', content: '抱歉，请求失败～' }]
          });
        }
      },
      
      fail: (err) => {
        console.error('API调用失败：', err);
        this.setData({
          messages: [...this.data.messages, { type: 'ai', content: '网络异常，请稍后再试～' }]
        });
      },
      
      complete: () => {
        this.setData({
          isLoading: false
        });
      }
    });
  },
});