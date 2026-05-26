const { getStaticUrl } = require('../../utils/config.js');

// pages/info/info.ts
Page({
  data: {
    image_ip: '',
    sections: [
      {
        id: 1, open: false,
        title: '通话功能', icon: '📹',
        color: 'linear-gradient(135deg, #E8F5FF, #D0E8FF)',
        desc: '支持视频通话与语音通话两种模式。视频通话可实时查看机器人摄像头画面，语音通话可通过机器人与家人对话。进入通话页面后，输入房间号加入房间即可开始通话。'
      },
      {
        id: 2, open: false,
        title: '事件提醒', icon: '📋',
        color: 'linear-gradient(135deg, #EDF8F0, #D0F0DC)',
        desc: '可添加定时事件提醒，设置日期、时间、重复周期和优先级。到达设定时间后，机器人会自动语音播报提醒内容。支持每日/每周等多种重复模式，优先级决定多个提醒同时到达时的播报顺序。'
      },
      {
        id: 3, open: false,
        title: 'AI 陪伴', icon: '🤖',
        color: 'linear-gradient(135deg, #FFF5E8, #FFECD0)',
        desc: '基于 AI 大模型的智能陪伴功能。可在 AI 调试页面自定义 AI 的性格、说话风格和背景设定，打造专属陪伴角色。支持实时对话测试，调整满意后即可在机器人端启用。'
      },
      {
        id: 4, open: false,
        title: '远程遥控', icon: '🕹️',
        color: 'linear-gradient(135deg, #FFF0E8, #FFDECA)',
        desc: '遥控页面提供方向控制和云台控制。方向键控制机器人前后左右移动，云台键控制摄像头抬头低头。长按方向键持续移动，松开即停止。操作前请确认设备已连接。'
      },
      {
        id: 5, open: false,
        title: '自定义命令', icon: '📝',
        color: 'linear-gradient(135deg, #F8F0FF, #E8D8FF)',
        desc: '支持向机器人发送自定义文本命令或语音指令。可在指令记录页面查看历史命令记录，了解命令执行状态和结果。'
      },
      {
        id: 6, open: false,
        title: '数据记录', icon: '📊',
        color: 'linear-gradient(135deg, #FFF0F5, #FFD6E4)',
        desc: '健康监测数据（心率、体温、湿度、呼吸频率）会自动记录并生成趋势图。在健康监测页面可查看实时数据和历史最高/最低值，支持切换不同设备查看。'
      },
      {
        id: 7, open: false,
        title: '星闪连接', icon: '⭐',
        color: 'linear-gradient(135deg, #EDF8FF, #D0ECFF)',
        desc: '通过星闪（NearLink）技术实现设备间低延迟、高可靠的无线连接。在「更多连接」页面可管理星闪设备配对和连接状态，查看设备信息。'
      },
    ]
  },

  onLoad() {
    this.setData({
      image_ip: getStaticUrl('/images/menu_container1.jpg')
    })
  },

  toggleSection(e: any) {
    const id = e.currentTarget.dataset.id;
    const sections = this.data.sections.map((s: any) => {
      if (s.id === id) s.open = !s.open;
      return s;
    });
    this.setData({ sections });
  },
});
