# -*- coding: utf-8 -*-
"""UE Quick Start - 一键编译并启动 Unreal Engine 项目

入口分发：有参数走 CLI（不加载 Tkinter），无参数启动 GUI。
"""

import sys
import os
import shutil
import tempfile
from pathlib import Path

# Windows 控制台默认 GBK，强制切 UTF-8 以免中文/emoji 编码崩
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


def _HideConsoleWhenGui():
    """打包后、无参数（GUI 模式）时隐藏控制台窗口"""
    if not getattr(sys, "frozen", False):
        return
    if len(sys.argv) > 1:
        return
    try:
        import ctypes
        ctypes.windll.user32.ShowWindow(
            ctypes.windll.kernel32.GetConsoleWindow(), 0
        )
    except Exception:
        pass


def CleanupMeiDirs():
    """清理 PyInstaller 遗留的 _MEI 临时目录"""
    if not getattr(sys, 'frozen', False):
        return

    CurMeiDir = getattr(sys, '_MEIPASS', None)
    TempDir = tempfile.gettempdir()

    for Name in os.listdir(TempDir):
        if Name.startswith('_MEI'):
            DirPath = os.path.join(TempDir, Name)
            if CurMeiDir and os.path.normcase(DirPath) == os.path.normcase(CurMeiDir):
                continue
            try:
                shutil.rmtree(DirPath)
            except Exception:
                pass


# 获取脚本/exe 所在目录（兼容 PyInstaller 打包）
if getattr(sys, 'frozen', False):
    ScriptDir = Path(sys.executable).parent.resolve()
else:
    ScriptDir = Path(__file__).parent.resolve()
sys.path.insert(0, str(ScriptDir))


def _DispatchCli() -> int:
    """CLI 模式：只编译不打开，不弹 GUI"""
    import argparse
    from Source.Data.ProjectInfo import LoadProjectInfo
    from Source.Data.Config import LoadConfig
    from Source.Logic.BuildMgr import BuildMgr

    Parser = argparse.ArgumentParser(prog="UEQuickStart", description="UE 项目一键编译工具")
    Parser.add_argument("--test", action="store_true", help="测试模式：只编译不打开编辑器")
    Parser.parse_args()

    # CLI 模式使用当前工作目录定位项目（区别于 GUI 模式使用脚本/exe 所在目录）
    WorkDir = Path.cwd()
    ProjectData = LoadProjectInfo(WorkDir)
    if ProjectData.ErrorMsg:
        print(f"错误: {ProjectData.ErrorMsg}")
        return 1

    print(f"项目: {ProjectData.Name}")
    print(f"引擎: Unreal Engine {ProjectData.EngineVersion}")
    print(f"路径: {ProjectData.EnginePath}")

    Config = LoadConfig(WorkDir)
    Mgr = BuildMgr()
    Result = {"Code": None}

    def OnLog(Msg):
        print(Msg)

    def OnSuccess():
        Result["Code"] = 0

    def OnError(Msg):
        print(f"错误: {Msg}")
        Result["Code"] = 1

    Mgr.RunBuild(
        ProjectName=ProjectData.Name,
        ProjectPath=ProjectData.Path,
        EnginePath=ProjectData.EnginePath,
        OnLog=OnLog,
        OnSuccess=OnSuccess,
        OnError=OnError,
        Platform=Config.Build.Platform,
        Configuration=Config.Build.Configuration,
        AdditionalArgs=Config.Build.AdditionalArgs,
    )

    return Result["Code"] or 0


def _DispatchGui() -> int:
    """GUI 模式：按需加载 Tkinter"""
    from Source.UI.MainWindow import MainWindow

    App = MainWindow(ScriptDir)
    App.Run()
    return 0


if __name__ == "__main__":
    CleanupMeiDirs()
    _HideConsoleWhenGui()
    if len(sys.argv) > 1:
        sys.exit(_DispatchCli())
    else:
        sys.exit(_DispatchGui())
