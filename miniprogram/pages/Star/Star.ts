// pages/Star/Star.ts
Page({
  data: {
    devices: [] as { id: number; name: string; deviceId: string; connected: boolean }[],
  },

  onLoad() {
    this.loadDevices();
  },

  onShow() {
    this.loadDevices();
  },

  loadDevices() {
    const stored = wx.getStorageSync('star_devices') || [];
    this.setData({ devices: stored });
  },

  scanDevice() {
    wx.showToast({ title: '搜索中...', icon: 'loading', duration: 2000 });
    setTimeout(() => {
      wx.showToast({ title: '暂未发现新设备', icon: 'none' });
    }, 2000);
  },
});
