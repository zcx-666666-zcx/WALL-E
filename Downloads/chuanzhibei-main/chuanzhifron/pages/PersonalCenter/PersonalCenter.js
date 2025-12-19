// PersonalCenter.js
import { request } from '../../utils/util.js'
import { getCurrentUser } from '../../utils/auth.js'

Page({
  data: {
    userInfo: {
      name: '访客',
      title: '非遗文化爱好者',
      avatar: 'https://s.coze.cn/image/Ex1Uxeu9hO8/'
    },
    userStats: {
      collections: 12,
      creations: 5,
      bookings: 3
    },
    collections: [],
    creations: [
      {
        id: 1,
        title: '我的剪纸作品',
        image: 'https://s.coze.cn/image/4xVhJpO4Qmk/'
      },
      {
        id: 2,
        title: '非遗展览随拍',
        image: 'https://s.coze.cn/image/i4_GSuT_V3o/'
      }
    ],
    bookings: [
      {
        id: 1,
        masterName: '张明远',
        skill: '剪纸体验',
        time: '2024-06-20 14:00-16:00',
        masterAvatar: 'https://s.coze.cn/image/QWiQen_znu8/',
        status: 'confirmed',
        statusText: '已预约'
      }
    ],
    loading: true
  },

  onLoad: function() {
    // 页面加载时的初始化
    // 检查用户登录状态
    const user = getCurrentUser();
    if (user) {
      this.setData({
        'userInfo.name': user.nickName || user.name,
        'userInfo.avatar': user.avatarUrl || user.avatar
      });
    }
    
    this.loadCollections();
  },
  
  // 加载收藏数据
  loadCollections: function() {
    // 这里应该从服务器加载用户的收藏数据
    // 暂时使用模拟数据
    const collections = [
      {
        id: 1,
        name: '昆曲',
        level: '国家级非物质文化遗产',
        description: '昆曲是中国最古老的戏曲声腔、剧种，被称为"百戏之祖"，列入联合国教科文组织非物质文化遗产名录...',
        image: 'https://s.coze.cn/image/v8I8iXe9kEs/'
      },
      {
        id: 2,
        name: '苏绣',
        level: '国家级非物质文化遗产',
        description: '苏绣是中国传统刺绣工艺之一，以精细、雅致著称，被誉为"东方艺术明珠"，具有极高的艺术价值...',
        image: 'https://s.coze.cn/image/-Wnxd47nx_g/'
      }
    ];
    
    this.setData({
      collections: collections,
      loading: false,
      'userStats.collections': collections.length
    });
  },

  // 设置按钮
  onSettings: function() {
    wx.showActionSheet({
      itemList: ['编辑资料', '隐私设置', '通知设置'],
      success: (res) => {
        const actions = ['编辑资料', '隐私设置', '通知设置'];
        wx.showToast({
          title: `选择了：${actions[res.tapIndex]}`,
          icon: 'none'
        });
      }
    });
  },

  // 收藏点击
  onCollectionTap: function(e) {
    const item = e.currentTarget.dataset.item;
    wx.showModal({
      title: item.name,
      content: item.description,
      showCancel: false,
      confirmText: '知道了'
    });
  },

  // 移除收藏
  removeCollection: function(e) {
    const item = e.currentTarget.dataset.item;
    wx.showModal({
      title: '移除收藏',
      content: `确定要移除"${item.name}"的收藏吗？`,
      showCancel: true,
      cancelText: '取消',
      confirmText: '确定',
      success: (res) => {
        if (res.confirm) {
          const collections = this.data.collections.filter(collection => collection.id !== item.id);
          this.setData({
            collections: collections,
            'userStats.collections': this.data.userStats.collections - 1
          });
          wx.showToast({
            title: '已移除收藏',
            icon: 'success'
          });
        }
      }
    });
  },

  // 创作点击
  onCreationTap: function(e) {
    const item = e.currentTarget.dataset.item;
    wx.showModal({
      title: item.title,
      content: '查看创作详情',
      showCancel: false,
      confirmText: '知道了'
    });
  },

  // 添加创作
  addCreation: function() {
    wx.showActionSheet({
      itemList: ['拍照', '从相册选择', '录制视频'],
      success: (res) => {
        const actions = ['拍照', '从相册选择', '录制视频'];
        wx.showToast({
          title: `选择了：${actions[res.tapIndex]}`,
          icon: 'none'
        });
      }
    });
  },

  // 取消预约
  cancelBooking: function(e) {
    const item = e.currentTarget.dataset.item;
    wx.showModal({
      title: '取消预约',
      content: `确定要取消"${item.masterName} - ${item.skill}"的预约吗？`,
      showCancel: true,
      cancelText: '不取消',
      confirmText: '确定取消',
      success: (res) => {
        if (res.confirm) {
          const bookings = this.data.bookings.filter(booking => booking.id !== item.id);
          this.setData({
            bookings: bookings,
            'userStats.bookings': this.data.userStats.bookings - 1
          });
          wx.showToast({
            title: '已取消预约',
            icon: 'success'
          });
        }
      }
    });
  },

  // 查看全部收藏
  viewAllCollections: function() {
    wx.showToast({
      title: '查看全部收藏',
      icon: 'none'
    });
  },

  // 查看全部创作
  viewAllCreations: function() {
    wx.showToast({
      title: '查看全部创作',
      icon: 'none'
    });
  },

  // 查看全部预约
  viewAllBookings: function() {
    wx.showToast({
      title: '查看全部预约',
      icon: 'none'
    });
  },

  // 菜单点击
  onMenuTap: function(e) {
    const type = e.currentTarget.dataset.type;
    const menuMap = {
      profile: '个人资料',
      settings: '设置',
      help: '帮助与反馈',
      about: '关于我们'
    };
    
    if (type === 'settings') {
      wx.showActionSheet({
        itemList: ['编辑资料', '隐私设置', '通知设置', '退出登录'],
        success: (res) => {
          if (res.tapIndex === 3) {
            // 退出登录
            wx.showModal({
              title: '退出登录',
              content: '确定要退出登录吗？',
              success: (res) => {
                if (res.confirm) {
                  // 清除用户信息
                  wx.removeStorageSync('token');
                  wx.removeStorageSync('userInfo');
                  
                  // 跳转到登录页面
                  wx.redirectTo({
                    url: '/pages/login/login'
                  });
                }
              }
            });
          } else {
            wx.showModal({
              title: menuMap[type],
              content: `${['编辑资料', '隐私设置', '通知设置'][res.tapIndex]}功能开发中`,
              showCancel: false,
              confirmText: '知道了'
            });
          }
        }
      });
    } else {
      wx.showModal({
        title: menuMap[type],
        content: `${menuMap[type]}功能开发中`,
        showCancel: false,
        confirmText: '知道了'
      });
    }
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
