// ARExperience.js
import { request } from '../../utils/util.js'

Page({
  data: {
    arProjects: [],
    experienceRecords: [
      {
        id: 1,
        name: '青铜器复原体验',
        image: 'https://s.coze.cn/image/Z91yggWpudY/',
        time: '2024-05-20 14:30',
        duration: '15分钟'
      },
      {
        id: 2,
        name: '古画复活体验',
        image: 'https://s.coze.cn/image/CZFB5AEC6zc/',
        time: '2024-05-18 10:15',
        duration: '12分钟'
      }
    ],
    loading: true
  },

  onLoad: function() {
    // 加载AR项目数据
    this.loadArProjects();
    // 检查AR功能支持
    this.checkARSupport();
  },
  
  // 加载AR项目数据
  loadArProjects: function() {
    request({
      url: '/ar-experience'
    }).then(data => {
      this.setData({
        arProjects: data,
        loading: false
      });
    }).catch(err => {
      console.error('获取AR项目失败:', err);
      this.setData({
        loading: false
      });
      wx.showToast({
        title: '加载AR项目失败',
        icon: 'none'
      });
    });
  },

  // 检查AR功能支持
  checkARSupport: function() {
    wx.getSystemInfo({
      success: (res) => {
        console.log('设备信息:', res);
        // 这里可以添加AR功能检测逻辑
      }
    });
  },

  // AR项目点击
  onARProjectTap: function(e) {
    const item = e.currentTarget.dataset.item;
    wx.showModal({
      title: item.name,
      content: item.description,
      showCancel: true,
      cancelText: '取消',
      confirmText: '开始体验',
      success: (res) => {
        if (res.confirm) {
          this.startARExperience(item);
        }
      }
    });
  },

  // 开始AR体验
  startARExperience: function(item) {
    // 检查相机权限
    wx.getSetting({
      success: (res) => {
        if (res.authSetting['scope.camera'] === false) {
          wx.showModal({
            title: '需要相机权限',
            content: 'AR体验需要访问您的相机，请在设置中开启相机权限',
            showCancel: false,
            confirmText: '知道了'
          });
          return;
        }
        
        // 模拟AR体验启动
        wx.showLoading({
          title: '正在启动AR体验...'
        });
        
        setTimeout(() => {
          wx.hideLoading();
          wx.showToast({
            title: `开始体验：${item.name}`,
            icon: 'none',
            duration: 2000
          });
          
          // 这里应该调用实际的AR功能
          // 例如：wx.navigateTo({ url: '/pages/AR/AR?projectId=' + item.id })
        }, 1500);
      }
    });
  },

  // 重新体验
  replayExperience: function(e) {
    const item = e.currentTarget.dataset.item;
    wx.showModal({
      title: '重新体验',
      content: `确定要重新体验"${item.name}"吗？`,
      showCancel: true,
      cancelText: '取消',
      confirmText: '确定',
      success: (res) => {
        if (res.confirm) {
          this.startARExperience(item);
        }
      }
    });
  },

  // 下拉刷新
  onPullDownRefresh: function() {
    setTimeout(() => {
      wx.stopPullDownRefresh();
      wx.showToast({
        title: '刷新成功',
        icon: 'success'
      });
    }, 1000);
  }
})