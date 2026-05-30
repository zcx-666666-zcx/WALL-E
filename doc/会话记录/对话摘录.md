# 对话与答疑摘录

> 便于后续 AI 了解用户背景与已解释过的概念，避免重复说明。

## 用户：介绍 doc 文档、需求与规划

AI 归纳：WALL-E = Web + Spring Boot + 小程序 + 树莓派；Windows 作服务器，FRP 公网；业务含登录、事件、联系人、设备、命令管理。

## 用户：演示规模改为 5 人；提供 FRP 隧道截图

- 修改 `doc/frp-windows-deploy.md`：50 人 → 5 人
- 记录域名 `zzuli525walle.fucku.top`，隧道 `127.0.0.1:8088`

## 用户：Docker 不好用、MySQL 可以；不会 CNAME；路径要改；扫描 Nginx/Maven

- Docker 引擎 500 → 本机 MySQL
- DNS 已生效，用户无需手配 CNAME
- 路径 `D:\WALL-E` → `D:\Projects\WALL-E`
- 安装 Nginx、Maven、MySQL；新增 `install-windows-deps.ps1`

## 用户：mysqld 是什么？

**答：** `mysqld` = MySQL 服务端程序，监听 3306 存数据；与客户端 `mysql` 命令不同。当前未注册 Windows 服务，重启电脑后需再运行 `start-mysql.ps1`。

## 用户：DNS 控制台、A/AAAA/CNAME 区别

**答：**

- DNS 控制台 = 域名商网站的「解析设置」
- A → IPv4；AAAA → IPv6；CNAME → 另一个域名
- FRP 自定义域名用 CNAME；同一主机记录不要 A 与 CNAME 混用
- 用户域名已 CNAME 到 `xg-4.frp.one`

## 用户：域名能否另买、是否限带宽

**答：** 域名只是地址；注册商一般不限制带宽；瓶颈在 FRP 免费隧道和家宽上行。

## 用户：ChmlFrp + 花生壳 vicp.fun 混用失败

**答：** `vicp.fun` 是花生壳的域名，不能作 ChmlFrp 自定义域名（无法 CNAME、北京节点要备案）。ChmlFrp 隧道成功 ≠ 能访问。应二选一，推荐继续花生壳。

## 收工（2026-05-29）

- 记录整理至 `doc/curso_chatlog/`，明日从 `tomorrow-handoff.md` 继续
