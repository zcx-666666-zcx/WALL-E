# WALL-E 三维建模资料

更新时间：2026-06-08

本目录用于集中保存 WALL-E / 星护安庭项目的可编辑 3D 建模源文件，方便后续比赛材料整理、产品三维模型提交、结构说明和制造文档编写。

## 目录结构

```text
doc/三维建模资料/
  README.md
  FILELIST.md
  source/
    可编辑瓦力/
      Wall-e_Assembly_NotForPrinting.STEP
      Wall-e_Assembly_NotForPrinting2.SLDASM
      Body Assembly.SLDASM
      Head Assembly.SLDASM
      Neck Assembly.SLDASM
      TankTracks.SLDASM
      ...
```

## 文件概况

源文件来自：

`/Users/zhangchenxi/Desktop/西门子规划/可编辑瓦力`

已整理入库：

| 类型 | 数量 | 用途 |
| --- | ---: | --- |
| `.STEP` | 80 | 通用 CAD 交换格式，适合比赛提交、跨软件查看和导出截图 |
| `.SLDPRT` | 69 | SolidWorks 零件源文件 |
| `.SLDASM` | 8 | SolidWorks 装配源文件 |
| `.3mf` | 6 | 3D 打印/网格制造相关格式 |

总计 163 个文件，约 40 MB。全量清单见 [FILELIST.md](FILELIST.md)。

## 关键装配文件

优先关注以下文件：

| 文件 | 说明 |
| --- | --- |
| `source/可编辑瓦力/Wall-e_Assembly_NotForPrinting.STEP` | 完整装配的通用 STEP 文件，优先用于比赛提交和跨平台查看 |
| `source/可编辑瓦力/Wall-e_Assembly_NotForPrinting2.SLDASM` | 完整 SolidWorks 装配文件 |
| `source/可编辑瓦力/Body Assembly.SLDASM` | 机身装配 |
| `source/可编辑瓦力/Head Assembly.SLDASM` | 头部装配 |
| `source/可编辑瓦力/Neck Assembly.SLDASM` | 颈部装配 |
| `source/可编辑瓦力/TankTracks.SLDASM` | 履带/底盘相关装配 |
| `source/可编辑瓦力/Left Wheels Assembly.SLDASM` | 左侧轮组装配 |
| `source/可编辑瓦力/Right Wheels Assembly.SLDASM` | 右侧轮组装配 |

## 比赛提交包建议

西门子杯或其他实物组比赛要求“产品三维模型源文件”时，建议从本目录整理：

```text
04_产品三维模型源文件/
  Wall-e_Assembly_NotForPrinting.STEP
  Wall-e_Assembly_NotForPrinting2.SLDASM
  Body Assembly.SLDASM
  Head Assembly.SLDASM
  Neck Assembly.SLDASM
  TankTracks.SLDASM
  关键零件/
  assembly_screenshot.png
  model_file说明.txt
```

如果提交平台限制文件数量，优先提交：

1. `Wall-e_Assembly_NotForPrinting.STEP`
2. `Wall-e_Assembly_NotForPrinting2.SLDASM`
3. 关键装配截图或爆炸图
4. 一页模型说明，写清楚建模软件、主要模块、制造方式和装配关系

## 后续需要补充

- 使用 SolidWorks 或可打开 STEP 的 CAD 软件导出 2-4 张截图：整机、爆炸图、底盘履带、头部/传感器区域。
- 根据真实样机补一份 BOM 与制造方式说明：3D 打印件、购买件、电子元件、线束和紧固件。
- 若某些模型来自公开参考或二次改造，需要在正式参赛材料中确认授权和引用口径。

## 注意事项

- 本目录已经包含可编辑源文件，不再只是路径说明。
- GitHub 单文件上传限制通常为 100 MB；当前最大文件约 12 MB，未超过限制。
- 不要在公开仓库上传含学校、队员、手机号、邮箱或报名信息的模型截图和说明文件。
