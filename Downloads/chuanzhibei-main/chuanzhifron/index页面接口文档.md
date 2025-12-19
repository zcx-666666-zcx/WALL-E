# 首页(index)接口文档

## 1. 概述

本文档详细描述了首页(index)所需的所有后端接口，供后端开发人员实现相应功能。

## 2. 接口列表

### 2.1 获取首页轮播图
#### 接口地址
```
GET /api/index/banner
```

#### 请求参数
无

#### 响应参数
```json
{
  "success": true,
  "message": "获取成功",
  "data": [
    {
      "id": 1,
      "title": "非遗传承人走进校园",
      "imageUrl": "https://example.com/banner1.jpg",
      "targetType": "news",  // 跳转类型：news(新闻详情)、heritage(非遗项目)、activity(活动详情)
      "targetId": 101
    },
    {
      "id": 2,
      "title": "传统工艺创新大赛",
      "imageUrl": "https://example.com/banner2.jpg",
      "targetType": "activity",
      "targetId": 201
    }
  ]
}
```

### 2.2 获取推荐非遗项目
#### 接口地址
```
GET /api/index/recommend-heritage
```

#### 请求参数
无

#### 响应参数
```json
{
  "success": true,
  "message": "获取成功",
  "data": [
    {
      "id": 1,
      "name": "景泰蓝制作技艺",
      "description": "景泰蓝制作技艺是中国传统工艺美术...",
      "imageUrl": "https://example.com/jingtai.jpg",
      "level": "国家级"
    },
    {
      "id": 2,
      "name": "蜀锦织造技艺",
      "description": "蜀锦织造技艺是四川省成都市地方传统...",
      "imageUrl": "https://example.com/shujin.jpg",
      "level": "国家级"
    },
    {
      "id": 3,
      "name": "景德镇瓷器",
      "description": "景德镇瓷器以其精美绝伦的工艺闻名世界...",
      "imageUrl": "https://example.com/ciqi.jpg",
      "level": "国家级"
    },
    {
      "id": 4,
      "name": "紫砂陶制作技艺",
      "description": "紫砂陶制作技艺主要流传于江苏省宜兴...",
      "imageUrl": "https://example.com/zisha.jpg",
      "level": "国家级"
    }
  ]
}
```

### 2.3 获取热门非遗分类
#### 接口地址
```
GET /api/index/popular-categories
```

#### 请求参数
无

#### 响应参数
```json
{
  "success": true,
  "message": "获取成功",
  "data": [
    {
      "id": 1,
      "name": "传统技艺",
      "iconUrl": "https://example.com/category_skill.png"
    },
    {
      "id": 2,
      "name": "传统戏剧",
      "iconUrl": "https://example.com/category_drama.png"
    },
    {
      "id": 3,
      "name": "传统音乐",
      "iconUrl": "https://example.com/category_music.png"
    },
    {
      "id": 4,
      "name": "民俗",
      "iconUrl": "https://example.com/category_folk.png"
    },
    {
      "id": 5,
      "name": "曲艺",
      "iconUrl": "https://example.com/category_quyi.png"
    }
  ]
}
```

### 2.4 获取最新非遗新闻
#### 接口地址
```
GET /api/index/latest-news
```

#### 请求参数
| 参数名 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| page | integer | 否 | 页码，默认为1 |
| size | integer | 否 | 每页条数，默认为5 |

#### 响应参数
```json
{
  "success": true,
  "message": "获取成功",
  "data": [
    {
      "id": 1,
      "title": "非遗传承人走进校园",
      "summary": "近日，多位非遗传承人走进XX小学，为学生们带来了一场精彩的文化盛宴...",
      "imageUrl": "https://example.com/news1.jpg",
      "publishTime": "2024-05-20 10:00:00",
      "viewCount": 1234,
      "likeCount": 56
    },
    {
      "id": 2,
      "title": "传统工艺创新大赛圆满落幕",
      "summary": "历时三个月的传统工艺创新大赛在XX市落下帷幕，共有来自全国各地的200余件作品参赛...",
      "imageUrl": "https://example.com/news2.jpg",
      "publishTime": "2024-05-18 15:30:00",
      "viewCount": 987,
      "likeCount": 42
    }
  ]
}
```

### 2.5 获取热门传承人
#### 接口地址
```
GET /api/index/popular-inheritors
```

#### 请求参数
无

#### 响应参数
```json
{
  "success": true,
  "message": "获取成功",
  "data": [
    {
      "id": 1,
      "name": "张明远",
      "skill": "剪纸",
      "avatarUrl": "https://example.com/master1.jpg",
      "title": "国家级传承人"
    },
    {
      "id": 2,
      "name": "李秀英",
      "skill": "苏绣",
      "avatarUrl": "https://example.com/master2.jpg",
      "title": "江苏省工艺美术大师"
    },
    {
      "id": 3,
      "name": "王建国",
      "skill": "景泰蓝",
      "avatarUrl": "https://example.com/master3.jpg",
      "title": "北京市工艺美术大师"
    }
  ]
}
```

### 2.6 获取特色AR体验
#### 接口地址
```
GET /api/index/featured-ar
```

#### 请求参数
无

#### 响应参数
```json
{
  "success": true,
  "message": "获取成功",
  "data": [
    {
      "id": 1,
      "name": "青铜器复原体验",
      "description": "通过AR技术还原古代青铜器的制作过程",
      "coverImageUrl": "https://example.com/ar1.jpg"
    },
    {
      "id": 2,
      "name": "古画复活体验",
      "description": "利用AR技术让古画中的场景动起来",
      "coverImageUrl": "https://example.com/ar2.jpg"
    }
  ]
}
```

## 3. 图片资源说明

### 3.1 轮播图(banner)
- 尺寸建议：750px * 300px (宽高比 5:2)
- 格式：jpg/png
- 文件大小：建议不超过200KB
- 内容：重要活动、新闻或特色非遗项目宣传图

### 3.2 推荐非遗项目图片
- 尺寸建议：300px * 200px (宽高比 3:2)
- 格式：jpg/png
- 文件大小：建议不超过100KB
- 内容：非遗项目的代表性图片

### 3.3 热门分类图标
- 尺寸建议：80px * 80px (正方形)
- 格式：png (支持透明背景)
- 文件大小：建议不超过20KB
- 内容：各个非遗分类的代表性图标

### 3.4 新闻图片
- 尺寸建议：200px * 150px (宽高比 4:3)
- 格式：jpg/png
- 文件大小：建议不超过80KB
- 内容：新闻相关内容配图

### 3.5 传承人头像
- 尺寸建议：100px * 100px (正方形)
- 格式：jpg/png
- 文件大小：建议不超过30KB
- 内容：传承人真实照片或肖像

### 3.6 AR体验封面图
- 尺寸建议：300px * 200px (宽高比 3:2)
- 格式：jpg/png
- 文件大小：建议不超过100KB
- 内容：AR体验项目的预览图

## 4. 错误响应格式

所有接口在发生错误时均返回以下格式：
```json
{
  "success": false,
  "error": "错误信息"
}
```

## 5. 权限要求

所有接口均为公开接口，无需用户认证即可访问。