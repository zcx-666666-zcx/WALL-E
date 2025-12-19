// pages/newsDetail/newsDetail.js
import { request } from '../../utils/util.js'

Page({
  data: {
    newsDetail: {}
  },

  onLoad: function (options) {
    // 获取传递过来的新闻ID或其他标识
    const newsId = options.id;
    
    // 这里应该从后端获取新闻详情数据
    // 暂时使用模拟数据演示
    if (newsId) {
      this.loadNewsDetail(newsId);
    } else {
      // 默认示例数据
      this.setData({
        newsDetail: {
          title: "默认新闻标题",
          image: "http://localhost:8001/uploads/news_index/sample_news.jpg",
          description: "这是新闻的详细内容。在这里您可以添加任意长度的文章内容，包括非遗项目的详细介绍、历史渊源、传承现状等等。"
        }
      });
    }
  },

  loadNewsDetail: function(id) {
    // 从后端获取新闻详情
    request({
      url: `/news/${id}`
    }).then(data => {
      this.setData({
        newsDetail: data
      });
    }).catch(err => {
      console.error('获取新闻详情失败:', err);
      wx.showToast({
        title: '加载新闻详情失败',
        icon: 'none'
      });
      
      // 使用模拟数据
      this.setData({
        newsDetail: {
          title: "新闻标题 " + id,
          image: "http://localhost:8001/uploads/news_index/news_" + id + ".jpg",
          description: "这是新闻ID为 " + id + " 的详细内容。在这里可以展示非遗项目的详细介绍、历史渊源、传承现状等等。非遗文化是中华民族的瑰宝，值得我们去传承和发扬光大。"
        }
      });
    });
  }
});