# AR体验界面接口文档

## 1. 概述

本文档详细描述了AR体验界面所需的所有后端接口，供后端开发人员实现相应功能。

## 2. 接口列表

### 2.1 获取AR体验项目列表
#### 接口地址
```
GET /api/ar/projects
```

#### 请求参数
| 参数名 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| category | string | 否 | 分类筛选条件 |
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
        "name": "青铜器复原体验",
        "description": "通过AR技术还原古代青铜器的制作过程",
        "imageUrl": "https://example.com/ar_1.jpg",
        "thumbUrl": "https://example.com/ar_thumb_1.jpg",
        "duration": "15分钟",
        "category": "文物复原"
      },
      {
        "id": 2,
        "name": "古画复活体验",
        "description": "利用AR技术让古画中的场景动起来",
        "imageUrl": "https://example.com/ar_2.jpg",
        "thumbUrl": "https://example.com/ar_thumb_2.jpg",
        "duration": "12分钟",
        "category": "艺术欣赏"
      }
    ],
    "total": 100,
    "page": 1,
    "size": 10,
    "hasNext": true
  }
}
```

### 2.2 获取AR体验项目详情
#### 接口地址
```
GET /api/ar/projects/{id}
```

#### 请求参数
路径参数：
- id: AR项目ID

#### 响应参数
```json
{
  "success": true,
  "message": "获取成功",
  "data": {
    "id": 1,
    "name": "青铜器复原体验",
    "description": "通过AR技术还原古代青铜器的制作过程",
    "detail": "本体验项目通过先进的AR技术，带领用户穿越时空，亲身体验中国古代青铜器的制作全过程。从选料、制模、浇铸到打磨，每一个环节都力求真实再现古代工匠的精湛技艺。",
    "instruction": "1. 确保设备电量充足\n2. 选择光线充足的环境\n3. 按照提示逐步操作\n4. 注意观察每个制作环节的细节",
    "imageUrl": "https://example.com/ar_1.jpg",
    "modelUrl": "https://example.com/models/bronze.glb",
    "duration": "15分钟",
    "category": "文物复原",
    "relatedHeritages": [
      {
        "id": 1,
        "name": "青铜器制作技艺",
        "level": "国家级"
      }
    ]
  }
}
```

### 2.3 记录AR体验历史
#### 接口地址
```
POST /api/ar/history
```

#### 请求参数
```json
{
  "projectId": 1,
  "duration": 900  // 体验时长（秒）
}
```

#### 响应参数
```json
{
  "success": true,
  "message": "记录成功"
}
```

### 2.4 获取用户AR体验历史
#### 接口地址
```
GET /api/ar/history
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
        "projectId": 1,
        "projectName": "青铜器复原体验",
        "projectThumb": "https://example.com/ar_thumb_1.jpg",
        "startTime": "2024-05-20 14:30:00",
        "duration": 900
      },
      {
        "id": 2,
        "projectId": 2,
        "projectName": "古画复活体验",
        "projectThumb": "https://example.com/ar_thumb_2.jpg",
        "startTime": "2024-05-18 10:15:00",
        "duration": 720
      }
    ],
    "total": 2,
    "page": 1,
    "size": 10,
    "hasNext": false
  }
}
```

### 2.5 获取AR体验统计数据
#### 接口地址
```
GET /api/ar/statistics
```

#### 请求参数
无

#### 响应参数
```json
{
  "success": true,
  "message": "获取成功",
  "data": {
    "totalExperiences": 128,
    "totalDuration": 124500,
    "favoriteProject": {
      "id": 1,
      "name": "青铜器复原体验",
      "count": 45
    },
    "recentExperiences": [
      {
        "date": "2024-05-20",
        "count": 12
      },
      {
        "date": "2024-05-19",
        "count": 8
      }
    ]
  }
}
```

## 3. 图片资源说明

### 3.1 AR项目封面图
- 尺寸建议：800px * 600px (宽高比 4:3)
- 格式：jpg/png
- 文件大小：建议不超过200KB
- 内容：AR项目的代表性场景截图或概念图

### 3.2 AR项目缩略图
- 尺寸建议：200px * 200px (正方形)
- 格式：jpg/png
- 文件大小：建议不超过50KB
- 内容：与封面图内容一致但尺寸更小的版本

### 3.3 AR模型文件
- 格式：glb/gltf
- 文件大小：建议不超过10MB
- 内容：AR体验所需的3D模型文件

## 4. 错误响应格式

所有接口在发生错误时均返回以下格式：
```json
{
  "success": false,
  "error": "错误信息"
}
```

## 5. 权限要求

所有接口均需要用户认证，在请求头中添加：
```
Authorization: Bearer <token>
```

## 6. 分页参数说明

对于支持分页的接口，分页参数遵循以下规范：
- page: 页码，从1开始计数
- size: 每页条数，建议范围10-50
- 返回数据中包含total(总条数)、hasNext(是否有下一页)等分页信息

## 7. 数据安全要求

1. 用户体验历史数据属于敏感信息，必须严格保密
2. AR模型文件需要防盗链处理
3. 所有接口通信必须通过HTTPS加密传输