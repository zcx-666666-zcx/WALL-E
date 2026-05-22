// pages/commandList/commandList.ts
Page({
  data: {
    commands: [] as { id: number; time: string; content: string; status: string; reply: string }[],
  },

  onLoad() {
    this.loadCommands();
  },

  onShow() {
    this.loadCommands();
  },

  loadCommands() {
    const stored = wx.getStorageSync('command_history') || [];
    this.setData({ commands: stored.slice(0, 50) });
  },
});
