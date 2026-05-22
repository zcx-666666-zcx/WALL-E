# WALL-E

## 协作约定

- 默认分支：`main`
- 公司共享集成分支：`dev`
- 个人开发分支：`zhangcx_dev`
- `main` 和 `dev` 只通过 Pull Request 合并，不直接推送
- 提交信息使用中文

## 当前仓库结构

- `cpn_robot`：现阶段主要 Web 前端目录
- `miniprogram-3`：微信小程序目录
- `rpnRobot`：Spring Boot 后端目录
- `PI_V1.0`、`RobotFusion`、`VideoCallProject`、`walle-replica`：树莓派端/历史实验代码

## 当前已识别问题

- 远程存在多个历史分支：`EstaChance`、`WeChatProgramme`、`huangjin`、`网页前端`、`master`、`zcx_master`
- 根目录包含重复代码来源，部分分支曾做过“把子目录提升到根目录”的重组
- 仓库内存在嵌套 Git 仓库：`cpn_robot/.git`、`miniprogram-3/.git`
- 当前工作区有未跟踪文件：`VideoCallProject.zip`

## 整理原则

- 不直接删除远程历史分支，先确认是否仍有人在使用
- 后续新开发统一从 `zhangcx_dev` 或其它功能分支发起 PR 到 `dev`
- `dev` 验证通过后，再以 PR 合并到 `main`
- 如需进一步清理重复目录，优先按“保留一个事实来源目录，其他目录归档或移除”的方式逐步处理
