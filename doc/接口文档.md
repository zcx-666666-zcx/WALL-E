# 接口文档 http://localhost:8080/开头

## 1. 用户相关接口
- **登录**
  - URL与请求格式: /login POST
  - 参数: 
    username:string 必填 用户名
    password:string 必填 密码
  - 响应格式：
    { 
        "code": 1,
        "msg": "success",
        "data": {
            "id": null,
            "username": "刘华韬",
            "password": "123456",
            "token": "eyJhbGciOiJIUzI1NiJ9.eyJuYW1lIjoi5YiY5Y2O6Z-sIiwiaWQiOm51bGwsImV4cCI6MTc2NzQzMDM2Nn0.df51WvHPc5O9xVg7Pm0cuQqCKqjxin6Ac4GgIOhlUi4"
        }
    }

- **获取用户ID接口**
  - URL与请求格式: /users/getId/{username} GET
  - 参数:
    username:string 必填 用户名
  - 响应格式:
    {
        "code": 1,
        "msg": "success",
        "data": {
            userId:1
        }
    }

## 2. 事件相关接口
- **添加事件接口**
  - URL与请求格式: /events/search/{userId} GET
  - 参数: 
    elementName:string 必填 时间名
    eventDate:Date 必填 第一次触发时间
    repeatDays:int 重复周期
    eventTime:Time 必填 触发时间
    priority:int 必填 优先级
    description:string 必填 事件描述
    machines:string 必填 绑定设备号
    userId:int 必填 用户id
  - 响应格式：
    { 
        "code": 1,
        "msg": "success",
        "data": 1
    }

- **删除事件接口**
  - URL与请求格式: /events/delete DELETE
  - 参数:
    eventName:string 必填 事件名称
    userId:int 必填 用户id
  - 响应格式:
    {
        "code": 1,
        "msg": "success",
        "data": 1
    }

- **事件查询接口**
  - URL与请求格式: /events/searchOne POST
  - 参数:
    eventName:string 必填 事件名称
    userId:int 必填 用户id
  - 响应格式:
    {
    "code": 1,
    "msg": "success",
    "data": {
        "id": 19,
        "eventName": "事件1",
        "eventDate": "2026-01-02",
        "eventTime": "22:54:00",
        "repeatDays": 2,
        "priority": "HIGH",
        "machines": "00001",
        "description": "测试事件1",
        "userId": "1"
        }
    }

- **更新事件接口**
  - URL与请求格式: /events/update PUT
  - 参数:
    elementName:string 必填 时间名
    eventDate:Date 必填 第一次触发时间
    repeatDays:int 重复周期
    eventTime:Time 必填 触发时间
    priority:int 必填 优先级
    description:string 必填 事件描述
    machines:string 必填 绑定设备号
    userId:int 必填 用户id
  - 响应格式:
    {
        "code": 1,
        "msg": "success",
        "data": 1
    }

- **获取事件列表接口**
  - URL与请求格式: /events/search/{userId} GET
  - 参数:
    userId:int 必填 用户id
  - 响应格式:
    {
        "code": 1,
        "msg": "success",
        "data": {
            "rows": [
                {
                    "id": 19,
                    "eventName": "事件1",
                    "eventDate":    "2026-01-02",
                    "eventTime": "22:54:00",
                    "repeatDays": 2,
                    "priority": "HIGH",
                    "machines": "00001",
                    "description": "测试事件    1",
                    "userId": "1"
                },
                {
                    "id": 22,
                    "eventName": "事件2",
                   "eventDate":        "2026-01-03",
                    "eventTime": "17:13:00",
                    "repeatDays": 11,
                    "priority": "HIGH",
                    "machines": "00001",
                    "description": "事件2",
                    "userId": "1"
                }
            ]
        }
    }
## 3. 联系人相关接口
- **获取联系人列表接口**
  - URL与请求格式: /contractUser/search/{userId} GET
  - 参数: 
    userId:int 必填 用户ID
  - 响应格式：
  {
        "code": 1,
        "msg": "success",
        "data": {
            "rows": [
                {
                    "id": 7,
                    "contractName": "联 联系人1",
                    "contractPhoneNumber": "18210698846",
                    "userId": 1
                }
            ]
        }
    }
    

- **删除联系人接口**
  - URL与请求格式:/contractUser/delete DELETE
  - 参数:
    contractName:string 必填 联系人姓名
    userId:int 必填 用户id
  - 响应格式:
    {
        "code": 1,
        "msg": "success",
        "data": 1
    }

- **添加联系人接口**
  - URL与请求格式:/contractUser/add POST
  - 参数:
    contractName:string 必填 联系人姓名
    contractPhoneNumber:string 必填 联系人电话号
    userId:int 必填 用户id
  - 响应格式:
    {
        "code": 1,
        "msg": "success",
        "data": 1
    }
## 4. 设备相关接口
- **获取设备列表接口**
  - URL与请求格式: /contractMachine/search/{userId} GET
  - 参数: 
    userId:int 必填 用户ID
  - 响应格式：
  {
        "code": 1,
        "msg": "success",
        "data": {
            "rows": [
                {
                    "id": 7,
                    "contractName": "联 联系人1",
                    "contractPhoneNumber": "18210698846",
                    "userId": 1
                }
            ]
        }
    }
    

- **删除设备接口**
  - URL与请求格式:/contractMachine/delete DELETE
  - 参数:
    machines:string 必填 设备名
    userId:int 必填 用户id
  - 响应格式:
    {
        "code": 1,
        "msg": "success",
        "data": 1
    }

- **添加设备接口**
  - URL与请求格式:/contractMachine/add POST
  - 参数:
    machines:string 必填 设备姓名
    connectionId:string 必填 设备号
    userId:int 必填 用户id
  - 响应格式:
    {
        "code": 1,
        "msg": "success",
        "data": 1
    }

## 5. 指令相关接口
- **获取设备列表接口**
  - URL与请求格式: /command/search POST
  - 参数: 
    machines:string 必填 设备名
    userId:int 必填 用户ID
  - 响应格式：{
    "code": 1,
    "msg": "success",
    "data": {
        "rows": [
            {
                "id": 1,
                "commandName": "往前走",
                "commandCode": "成功执行",
                "time": "2026-01-02T22:59:37",
                "machines": "测试设备1",
                "userId": "1"
            }
        ]
    }
}
  