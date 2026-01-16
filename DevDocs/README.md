# UEBuildToGO - 开发文档

## 项目大纲

一键编译并打开 UE 项目的 GUI 工具，替代 IDE 编译流程。

### 架构

```
Main.py (入口)
    ↓
Source/UI/MainWindow.py (界面层)
    ↓
Source/Logic/BuildMgr.py (业务逻辑层)
    ↓
Source/Data/
├── ProjectInfo.py (项目信息)
└── Config.py (配置管理)

Source/Utils/
└── Logger.py (日志模块)
```

### 核心流程

1. 加载配置文件 `UEBuildConfig.json`（可选）
2. 检测 `.uproject` 文件 → 获取项目名、引擎版本
3. 从注册表/Launcher 配置获取引擎路径（支持 GUID 源码引擎）
4. 调用 `Engine/Build/BatchFiles/Build.bat` 编译
5. 编译成功后启动 `UnrealEditor.exe` 打开项目

## 功能进度

| 功能 | 状态 | 说明 |
|------|------|------|
| 项目检测 | ✅ 完成 | [链接](编译功能/) |
| 引擎路径获取 | ✅ 完成 | 支持 GUID 源码引擎 |
| 编译执行 | ✅ 完成 | [链接](编译功能/) |
| 打开项目 | ✅ 完成 | [链接](编译功能/) |
| 配置文件 | ✅ 完成 | 平台/配置/自动打开等 |
| 进程管理 | ✅ 完成 | 窗口关闭时清理编译进程 |
| 跨平台支持 | ⏳ 待开始 | macOS/Linux |

## 当前任务

- [x] Windows 版本基础功能
- [x] 配置文件支持
- [x] GUID 引擎版本支持
- [ ] 实际项目测试验证
- [ ] 打包成 EXE 发布

## 阻塞与待讨论

| 事项 | 类型 | 说明 |
|------|------|------|
| 暂无 | - | - |
