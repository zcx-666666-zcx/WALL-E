// pages/machine/machine.ts
Page({
  data: {
    devices: [] as { id: number; name: string; model: string; icon: string; color: string; signal: number; connected: boolean }[],
  },

  onLoad() {
    this.loadDevices();
  },

  onShow() {
    this.loadDevices();
  },

  loadDevices() {
    const stored = wx.getStorageSync('connected_devices') || [];
    this.setData({ devices: stored });
  },
});
