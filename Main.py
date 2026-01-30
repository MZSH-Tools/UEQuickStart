# -*- coding: utf-8 -*-
"""
UE Quick Start - 一键编译并启动 Unreal Engine 项目
将此工具放置于 .uproject 同级目录，双击运行即可
"""

import sys
import os
import shutil
import tempfile
from pathlib import Path

# PyInstaller 打包后隐藏控制台窗口（解决 console=False 的 bootloader bug）
if getattr(sys, 'frozen', False):
    import ctypes
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)


def CleanupMeiDirs():
    """清理 PyInstaller 遗留的 _MEI 临时目录"""
    if not getattr(sys, 'frozen', False):
        return  # 非打包环境，不处理

    CurMeiDir = getattr(sys, '_MEIPASS', None)
    TempDir = tempfile.gettempdir()

    for Name in os.listdir(TempDir):
        if Name.startswith('_MEI'):
            Path = os.path.join(TempDir, Name)
            # 跳过当前正在使用的目录
            if CurMeiDir and os.path.normcase(Path) == os.path.normcase(CurMeiDir):
                continue
            try:
                shutil.rmtree(Path)
            except Exception:
                pass  # 忽略删除失败（可能被其他进程占用）

# 获取脚本/exe 所在目录（兼容 PyInstaller 打包）
if getattr(sys, 'frozen', False):
    ScriptDir = Path(sys.executable).parent.resolve()
else:
    ScriptDir = Path(__file__).parent.resolve()
sys.path.insert(0, str(ScriptDir))

from Source.UI.MainWindow import MainWindow


def Main():
    CleanupMeiDirs()  # 清理旧的临时目录
    App = MainWindow(ScriptDir)
    App.Run()


if __name__ == "__main__":
    Main()
