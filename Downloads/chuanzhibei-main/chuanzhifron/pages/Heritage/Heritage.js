// Heritage.js
import { request } from '../../utils/util.js'

Page({
  data: {
    currentCategory: 'all',
    nationalList: [],
    provincialList: [],
    filteredList: [],
    loading: true
  },

  onLoad: function() {
    this.loadHeritageData();
  },
  
  // 加载非遗数据
  loadHeritageData: function() {
    // 获取所有非遗项目
    request({
      url: '/heritage'
    }).then(data => {
      // 分离国家级和省级项目
      const nationalList = data.filter(item => item.level === 1).map(item => ({
        ...item,
        isBookmarked: false
      }));
      
      const provincialList = data.filter(item => item.level === 2).map(item => ({
        ...item,
        isBookmarked: false
      }));
      
      this.setData({
        nationalList: nationalList,
        provincialList: provincialList,
        loading: false
      }, () => {
        this.filterHeritage();
      });
    }).catch(err => {
      console.error('获取非遗数据失败:', err);
      this.setData({
        loading: false
      });
      wx.showToast({
        title: '加载数据失败',
        icon: 'none'
      });
    });
  },

  // 分类筛选
  onCategoryChange: function(e) {
    const category = e.currentTarget.dataset.category;
    this.setData({
      currentCategory: category
    });
    this.filterHeritage();
  },

  // 筛选非遗项目
  filterHeritage: function() {
    const { currentCategory, nationalList, provincialList } = this.data;
    let filtered = [];
    
    if (currentCategory === 'all') {
      filtered = [...nationalList, ...provincialList];
    } else {
      filtered = [...nationalList, ...provincialList].filter(item => item.category === currentCategory);
    }
    
    this.setData({
      filteredList: filtered
    });
  },

  // 非遗项目点击
  onHeritageTap: function(e) {
    const item = e.currentTarget.dataset.item;
    wx.showModal({
      title: item.name,
      content: item.description,
      showCancel: false,
      confirmText: '知道了'
    });
  },

  // 收藏功能
  onBookmarkTap: function(e) {
    const item = e.currentTarget.dataset.item;
    const { nationalList, provincialList } = this.data;
    
    // 更新国家级列表
    const nationalIndex = nationalList.findIndex(heritage => heritage.id === item.id);
    if (nationalIndex !== -1) {
      nationalList[nationalIndex].isBookmarked = !nationalList[nationalIndex].isBookmarked;
    }
    
    // 更新省级列表
    const provincialIndex = provincialList.findIndex(heritage => heritage.id === item.id);
    if (provincialIndex !== -1) {
      provincialList[provincialIndex].isBookmarked = !provincialList[provincialIndex].isBookmarked;
    }
    
    this.setData({
      nationalList: nationalList,
      provincialList: provincialList
    });
    
    wx.showToast({
      title: !item.isBookmarked ? '已取消收藏' : '已收藏',
      icon: 'none'
    });
  }
})