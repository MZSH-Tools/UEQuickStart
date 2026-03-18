# UEBuildToGO 使用教程

## 使用前提

机器上已成功运行过一次项目（确保编译环境已配置好）

## 快速开始

1. 将 `UEBuildTool.exe` 放到项目根目录（与 `.uproject` 同级）
2. 双击运行
3. 等待编译完成，自动打开项目

## 配置说明

### 自动检测项

| 项目 | 来源 |
|------|------|
| 项目名称 | `.uproject` 文件名 |
| 引擎版本 | `.uproject` 中的 `EngineAssociation` |
| 引擎路径 | Windows 注册表 / Epic Games Launcher 配置 |

### 可选配置文件

在项目根目录创建 `UEBuildConfig.json` 可自定义编译行为：

```json
{
  "Build": {
    "Platform": "Win64",
    "Configuration": "Development",
    "AdditionalArgs": []
  },
  "AutoOpenProject": true,
  "AutoCloseOnSuccess": true,
  "CloseDelayMs": 1500
}
```

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| Build.Platform | Win64 | 目标平台 |
| Build.Configuration | Development | 编译配置（Development/Shipping 等） |
| Build.AdditionalArgs | [] | 额外编译参数 |
| AutoOpenProject | true | 编译成功后自动打开项目 |
| AutoCloseOnSuccess | true | 打开项目后自动关闭工具 |
| CloseDelayMs | 1500 | 关闭延迟（毫秒） |

## 常见问题

### Q: 提示"未找到 .uproject 文件"

**原因**：工具没有放在 UE 项目根目录

**解决**：将 `UEBuildTool.exe` 或 `Main.py` + `Source/` 复制到 `.uproject` 文件所在目录

---

### Q: 提示"无法找到引擎安装路径"

**原因**：引擎不是通过 Epic Games Launcher 安装，或注册表信息丢失

**解决**：
1. 确认引擎是通过 Launcher 安装
2. 尝试在 Launcher 中验证引擎文件
3. 重新安装引擎

---

### Q: 编译失败

**解决**：查看日志窗口中的具体错误信息，联系程序同学协助排查

---

### Q: 跨平台协作（Mac/Linux）源码换行符导致编译失败

**原因**：Mac/Linux 使用 LF (`\n`) 或 CR (`\r`) 换行符，Windows 上 MSVC 编译器可能无法正确处理

**解决**：工具会在编译前自动扫描并修复源码文件的换行符为 CRLF (`\r\n`)，无需手动处理

**扫描范围**：
- `Source/`、`ThirdParty/` 目录
- `Plugins/` 下递归查找所有 `Source/` 和 `ThirdParty/` 目录

**支持文件类型**：`.h`、`.c`、`.cpp`、`.cs`、`.inl`

---

### Q: 支持 UE4 吗？

**支持**。工具会自动检测编辑器：
- UE5: `UnrealEditor.exe`
- UE4: `UE4Editor.exe`

---

### Q: 支持源码编译的引擎吗？

**支持**。工具会自动识别 `.uproject` 中的 GUID 格式引擎版本，并从注册表获取对应的引擎路径。

---

### Q: 支持 macOS / Linux 吗？

**暂不支持**。当前仅支持 Windows，跨平台功能待开发。
