// InheritorCommunity.js
import { request } from '../../utils/util.js'

Page({
  data: {
    masterList: [],
    skillVideos: [
      {
        id: 1,
        title: '苏绣技艺展示',
        description: '国家级传承人展示苏绣的精湛技艺和独特魅力',
        thumbnail: 'https://s.coze.cn/image/SbUcnCt-Iqc/',
        duration: '15:30',
        date: '2024-05-15',
        views: '3.2万'
      },
      {
        id: 2,
        title: '书法创作演示',
        description: '著名书法家现场演示书法创作过程和技巧',
        thumbnail: 'https://s.coze.cn/image/PBlzmW2nGZc/',
        duration: '12:45',
        date: '2024-05-10',
        views: '2.8万'
      }
    ],
    activities: [
      {
        id: 1,
        title: '非遗技艺体验日',
        time: '2024-06-15 10:00-16:00',
        location: '北京市东城区非遗展示中心',
        day: '15',
        month: '六月',
        buttonText: '报名参加'
      },
      {
        id: 2,
        title: '传承人讲座系列',
        time: '2024-06-18 14:00-16:00',
        location: '线上直播',
        day: '18',
        month: '六月',
        buttonText: '预约观看'
      }
    ],
    communityPosts: [
      {
        id: 1,
        userName: '剪纸达人',
        avatar: 'https://s.coze.cn/image/-iCInm6Nsno/',
        time: '2小时前',
        content: '今天完成了新的剪纸作品《龙凤呈祥》，融合了传统纹样和现代设计元素，希望大家喜欢！',
        images: ['https://s.coze.cn/image/FZSjJ9b6B20/'],
        likes: 128,
        comments: 23,
        isLiked: false
      },
      {
        id: 2,
        userName: '陶瓷工艺师',
        avatar: 'https://s.coze.cn/image/FiE0xG-tX8Q/',
        time: '5小时前',
        content: '分享一个青花瓷的制作过程，从选料到烧制，每一步都凝聚着匠人的心血。',
        images: ['https://s.coze.cn/image/soDA5vwwUNI/', 'https://s.coze.cn/image/s2urUFbD2t4/'],
        likes: 256,
        comments: 45,
        isLiked: true
      }
    ],
    loading: true
  },

  onLoad: function() {
    // 页面加载时的初始化
    this.loadMasterList();
  },
  
  // 加载传承人列表
  loadMasterList: function() {
    request({
      url: '/inheritor'
    }).then(data => {
      this.setData({
        masterList: data,
        loading: false
      });
    }).catch(err => {
      console.error('获取传承人列表失败:', err);
      this.setData({
        loading: false
      });
      wx.showToast({
        title: '加载传承人失败',
        icon: 'none'
      });
    });
  },

  // 传承人点击
  onMasterTap: function(e) {
    const item = e.currentTarget.dataset.item;
    wx.showModal({
      title: item.name,
      content: `${item.skill} - ${item.description}`,
      showCancel: false,
      confirmText: '知道了'
    });
  },

  // 预约体验
  bookExperience: function(e) {
    const item = e.currentTarget.dataset.item;
    wx.showModal({
      title: '预约体验',
      content: `确定要预约${item.name}的${item.skill}体验吗？`,
      showCancel: true,
      cancelText: '取消',
      confirmText: '确定预约',
      success: (res) => {
        if (res.confirm) {
          wx.showToast({
            title: '预约成功',
            icon: 'success'
          });
        }
      }
    });
  },

  // 视频点击
  onVideoTap: function(e) {
    const item = e.currentTarget.dataset.item;
    wx.showModal({
      title: item.title,
      content: item.description,
      showCancel: true,
      cancelText: '取消',
      confirmText: '观看视频',
      success: (res) => {
        if (res.confirm) {
          wx.showToast({
            title: '正在播放视频...',
            icon: 'none'
          });
        }
      }
    });
  },

  // 参加活动
  joinActivity: function(e) {
    const item = e.currentTarget.dataset.item;
    wx.showModal({
      title: '参加活动',
      content: `确定要${item.buttonText}"${item.title}"吗？`,
      showCancel: true,
      cancelText: '取消',
      confirmText: '确定',
      success: (res) => {
        if (res.confirm) {
          wx.showToast({
            title: item.buttonText === '报名参加' ? '报名成功' : '预约成功',
            icon: 'success'
          });
        }
      }
    });
  },

  // 点赞
  likePost: function(e) {
    const item = e.currentTarget.dataset.item;
    const communityPosts = this.data.communityPosts;
    const index = communityPosts.findIndex(post => post.id === item.id);
    
    if (index !== -1) {
      communityPosts[index].isLiked = !communityPosts[index].isLiked;
      communityPosts[index].likes += communityPosts[index].isLiked ? 1 : -1;
      
      this.setData({
        communityPosts: communityPosts
      });
      
      wx.showToast({
        title: communityPosts[index].isLiked ? '已点赞' : '已取消点赞',
        icon: 'none'
      });
    }
  },

  // 评论
  commentPost: function(e) {
    const item = e.currentTarget.dataset.item;
    wx.showModal({
      title: '评论',
      content: `对"${item.userName}"的帖子进行评论`,
      showCancel: true,
      cancelText: '取消',
      confirmText: '发表评论',
      success: (res) => {
        if (res.confirm) {
          wx.showToast({
            title: '评论功能开发中',
            icon: 'none'
          });
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