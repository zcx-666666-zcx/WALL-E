# 非遗传承微信小程序

## 项目结构

```
├── app.js                 # 小程序入口文件
├── app.json              # 小程序全局配置
├── app.wxss              # 小程序全局样式
├── pages/                # 页面目录
│   ├── index/            # 首页
│   │   ├── index.js      # 页面逻辑
│   │   ├── index.json    # 页面配置
│   │   ├── index.wxml    # 页面结构
│   │   └── index.wxss    # 页面样式
│   ├── Heritage/         # 非遗名录页面
│   │   ├── Heritage.js
│   │   ├── Heritage.json
│   │   ├── Heritage.wxml
│   │   └── Heritage.wxss
│   ├── ARExperience/     # AR体验页面
│   │   ├── ARExperience.js
│   │   ├── ARExperience.json
│   │   ├── ARExperience.wxml
│   │   └── ARExperience.wxss
│   ├── InheritorCommunit/ # 传承人社区页面
│   │   ├── InheritorCommunit.js
│   │   ├── InheritorCommunit.json
│   │   ├── InheritorCommunit.wxml
│   │   └── InheritorCommunit.wxss
│   ├── PersonalCenter/   # 个人中心页面
│   │   ├── PersonalCenter.js
│   │   ├── PersonalCenter.json
│   │   ├── PersonalCenter.wxml
│   │   └── PersonalCenter.wxss
│   └── logs/             # 日志页面
├── utils/                # 工具函数
│   └── util.js
├── project.config.json   # 项目配置
└── sitemap.json         # 站点地图
```

## 功能特性

### 首页 (index)
- 轮播图展示
- 非遗动态新闻
- 推荐非遗项目
- AR体验入口

### 非遗名录 (Heritage)
- 分类筛选功能
- 国家级和省级非遗项目展示
- 收藏功能
- 项目详情查看

### AR体验 (ARExperience)
- AR项目介绍
- 热门AR体验项目
- 体验指南
- 体验记录

### 传承人社区 (InheritorCommunit)
- 国家级传承人展示
- 技艺展示视频
- 社区活动
- 社区动态和互动

### 个人中心 (PersonalCenter)
- 用户信息展示
- 我的收藏
- 我的创作
- 预约体验管理
- 功能菜单

## 技术特点

1. **响应式设计**: 适配不同屏幕尺寸
2. **中国风设计**: 采用传统色彩和元素
3. **交互体验**: 丰富的用户交互功能
4. **模块化结构**: 清晰的代码组织结构
5. **数据驱动**: 使用数据绑定实现动态内容

## 开发说明

1. 所有页面都支持下拉刷新
2. 使用了微信小程序的tabBar导航
3. 图片资源使用在线CDN链接
4. 样式使用rpx单位适配不同设备
5. 交互功能使用Toast和Modal提供用户反馈

## 运行方式

1. 使用微信开发者工具打开项目
2. 配置AppID（测试可使用测试号）
3. 点击编译运行即可预览

## 注意事项

- 图片资源为示例链接，实际使用时需要替换为有效资源
- AR功能需要真机测试，模拟器可能无法完全展示效果
- 部分功能为演示版本，实际部署时需要对接后端API
