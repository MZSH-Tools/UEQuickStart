# -*- coding: utf-8 -*-
"""编译管理器 - 业务逻辑层"""

import subprocess
import threading
from pathlib import Path
from typing import Callable, Optional


class BuildMgr:
    """编译管理器"""

    def __init__(self):
        self.IsBuilding: bool = False
        self.BuildSuccess: bool = False
        self.Process: Optional[subprocess.Popen] = None

    def StartBuild(
        self,
        ProjectName: str,
        ProjectPath: Path,
        EnginePath: str,
        OnLog: Callable[[str], None],
        OnSuccess: Callable[[], None],
        OnError: Callable[[str], None],
        Platform: str = "Win64",
        Configuration: str = "Development",
        AdditionalArgs: list[str] = None
    ):
        """开始编译（异步）"""
        if self.IsBuilding:
            return

        self.IsBuilding = True
        self.BuildSuccess = False

        Thread = threading.Thread(
            target=self.RunBuild,
            args=(ProjectName, ProjectPath, EnginePath, OnLog, OnSuccess, OnError,
                  Platform, Configuration, AdditionalArgs or []),
            daemon=True
        )
        Thread.start()

    def StopBuild(self):
        """停止编译进程"""
        if self.Process and self.Process.poll() is None:
            try:
                self.Process.terminate()
                self.Process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self.Process.kill()
            except Exception:
                pass
        self.IsBuilding = False
        self.Process = None

    def RunBuild(
        self,
        ProjectName: str,
        ProjectPath: Path,
        EnginePath: str,
        OnLog: Callable[[str], None],
        OnSuccess: Callable[[], None],
        OnError: Callable[[str], None],
        Platform: str,
        Configuration: str,
        AdditionalArgs: list[str]
    ):
        """执行编译（后台线程）"""
        BuildBat = Path(EnginePath) / "Engine/Build/BatchFiles/Build.bat"

        if not BuildBat.exists():
            self.IsBuilding = False
            OnError(f"找不到 Build.bat: {BuildBat}")
            return

        # 构建编译命令
        Cmd = [
            str(BuildBat),
            f"{ProjectName}Editor",
            Platform,
            Configuration,
            f"-Project={ProjectPath}",
            "-WaitMutex",
            "-FromMsBuild"
        ] + AdditionalArgs

        OnLog(f"执行命令: {' '.join(Cmd)}")

        try:
            self.Process = subprocess.Popen(
                Cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='gbk',
                errors='replace',
                cwd=str(ProjectPath.parent),
                shell=True
            )

            # 实时读取输出
            for Line in self.Process.stdout:
                Line = Line.strip()
                if Line:
                    OnLog(Line)

            self.Process.wait()

            self.IsBuilding = False
            if self.Process.returncode == 0:
                self.BuildSuccess = True
                OnSuccess()
            else:
                OnError(f"编译失败，返回码: {self.Process.returncode}")

        except Exception as E:
            self.IsBuilding = False
            OnError(f"编译异常: {E}")
