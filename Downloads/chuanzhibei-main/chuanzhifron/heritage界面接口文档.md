# heritage界面接口文档

## 1. 概述

本文档详细描述了heritage非遗名录界面所需的所有后端接口，供后端开发人员实现相应功能。

## 2. 接口列表

### 21. 获取非遗项目分类
#### 接口地址
```
GET /api/heritage/categories
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
      "name": "传统美术",
      "iconUrl": "https://example.com/category_art.png"
    },
    {
      "id": 3,
      "name": "传统音乐",
      "iconUrl": "https://example.com/category_music.png"
    },
    {
      "id": 4,
      "name": "传统舞蹈",
      "iconUrl": "https://example.com/category_dance.png"
    },
    {
      "id": 5,
      "name": "传统戏剧",
      "iconUrl": "https://example.com/category_drama.png"
    },
    {
      "id": 6,
      "name": "曲艺",
      "iconUrl": "https://example.com/category_quyi.png"
    },
    {
      "id": 7,
      "name": "民俗",
      "iconUrl": "https://example.com/category_folk.png"
    }
  ]
}
```

### 2.2 获取非遗项目列表
#### 接口地址
```
GET /api/heritage/list
```

#### 请求参数
| 参数名 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| category | string | 否 | 分类筛选条件 |
| level | integer | 否 | 级别筛选条件(1-国家级, 2-省级, 3-市级) |
| keyword | string | 否 | 搜索关键词 |
| page | integer | 否 | 页码，默认为1 |
| size | integer | 否 | 每页条数，默认为10 |

#### 响应参数
```json
{
  "success": true,
  "message": "获取成功",
  "data": {
    "list": [
      {
        "id": 1,
        "name": "景泰蓝制作技艺",
        "category": "传统技艺",
        "level": 1,
        "region": "北京市",
        "imageUrl": "https://example.com/heritage_1.jpg",
        "introduction": "景泰蓝制作技艺是中国传统工艺美术之一，以其精美的造型和华丽的装饰而闻名..."
      },
      {
        "id": 2,
        "name": "苏绣",
        "category": "传统技艺",
        "level": 1,
        "region": "江苏省苏州市",
        "imageUrl": "https://example.com/heritage_2.jpg",
        "introduction": "苏绣是中国四大名绣之一，以其精细雅洁而著称..."
      }
    ],
    "total": 100,
    "page": 1,
    "size": 10,
    "hasNext": true
  }
}
```

### 2.3 获取非遗项目详情
#### 接口地址
```
GET /api/heritage/detail/{id}
```

#### 请求参数
路径参数：
- id: 非遗项目ID

#### 响应参数
```json
{
  "success": true,
  "message": "获取成功",
  "data": {
    "id": 1,
    "name": "景泰蓝制作技艺",
    "category": "传统技艺",
    "level": 1,
    "region": "北京市",
    "imageUrl": "https://example.com/heritage_1.jpg",
    "introduction": "景泰蓝制作技艺是中国传统工艺美术之一，以其精美的造型和华丽的装饰而闻名...",
    "description": "景泰蓝，又称\"铜胎掐丝珐琅\"，是一种在铜质胎型上用扁铜丝掐成各种图案，再填以各色珐琅釉料，经烧制、磨光、镀金等工序制成的工艺品。它集造型、色彩、装饰于一体，具有鲜明的民族风格和深刻的文化内涵。",
    "history": "景泰蓝工艺起源于元朝，成熟于明朝景泰年间，因其釉料多为蓝色而得名。清朝时期进一步发展，成为宫廷艺术的重要组成部分。新中国成立后，景泰蓝工艺得到了很好的保护和传承。",
    "status": "目前，景泰蓝制作技艺在北京、扬州等地均有传承，涌现出一批优秀的传承人和工艺大师。国家也出台了一系列保护措施，确保这一传统工艺得以延续和发展。",
    "relatedMasters": [
      {
        "id": 1,
        "name": "张同禄",
        "avatarUrl": "https://example.com/master_1.jpg",
        "title": "中国工艺美术大师"
      },
      {
        "id": 2,
        "name": "钟连盛",
        "avatarUrl": "https://example.com/master_2.jpg",
        "title": "北京市工艺美术大师"
      }
    ]
  }
}
```

### 2.4 收藏非遗项目
#### 接口地址
```
POST /api/heritage/favorite
```

#### 请求参数
```json
{
  "heritageId": 1
}
```

#### 响应参数
```json
{
  "success": true,
  "message": "收藏成功"
}
```

### 2.5 取消收藏非遗项目
#### 接口地址
```
DELETE /api/heritage/favorite/{id}
```

#### 请求参数
路径参数：
- id: 非遗项目ID

#### 响应参数
```json
{
  "success": true,
  "message": "取消收藏成功"
}
```

### 2.6 获取用户收藏的非遗项目
#### 接口地址
```
GET /api/heritage/favorites
```

#### 请求参数
| 参数名 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| page | integer | 否 | 页码，默认为1 |
| size | integer | 否 | 每页条数，默认为10 |

#### 响应参数
```json
{
  "success": true,
  "message": "获取成功",
  "data": {
    "list": [
      {
        "id": 1,
        "name": "景泰蓝制作技艺",
        "category": "传统技艺",
        "level": 1,
        "region": "北京市",
        "imageUrl": "https://example.com/heritage_1.jpg",
        "introduction": "景泰蓝制作技艺是中国传统工艺美术之一，以其精美的造型和华丽的装饰而闻名..."
      }
    ],
    "total": 1,
    "page": 1,
    "size": 10,
    "hasNext": false
  }
}
```

## 3. 图片资源说明

### 3.1 非遗项目图片
- 尺寸建议：800px * 600px (宽高比 4:3)
- 格式：jpg/png
- 文件大小：建议不超过200KB
- 内容：非遗项目的代表性图片

### 3.2 分类图标
- 尺寸建议：80px * 80px (正方形)
- 格式：png (支持透明背景)
- 文件大小：建议不超过20KB
- 内容：各个非遗分类的代表性图标

## 4. 错误响应格式

所有接口在发生错误时均返回以下格式：
```json
{
  "success": false,
  "error": "错误信息"
}
```

## 5. 权限要求

除获取分类和项目列表接口外，其他接口均需要用户认证，在请求头中添加：
```
Authorization: Bearer <token>
```

## 6. 分页参数说明

对于支持分页的接口，分页参数遵循以下规范：
- page: 页码，从1开始计数
- size: 每页条数，建议范围10-50
- 返回数据中包含total(总条数)、hasNext(是否有下一页)等分页信息