# -*- coding: utf-8 -*-
"""主窗口 - UI 层"""

import tkinter as tk
from tkinter import ttk, scrolledtext
from datetime import datetime
from pathlib import Path

from Source.Data.ProjectInfo import ProjectData, LoadProjectInfo
from Source.Logic.BuildMgr import BuildMgr


class MainWindow:
    """主窗口"""

    def __init__(self, ScriptDir: Path):
        self.ScriptDir = ScriptDir
        self.ProjectData: ProjectData = None
        self.BuildMgr = BuildMgr()

        self.Root = tk.Tk()
        self.Root.title("UE Build Tool")
        self.Root.geometry("600x450")
        self.Root.resizable(True, True)

        self._SetupUI()
        self.Root.after(100, self._LoadProjectInfo)

    def _SetupUI(self):
        """创建界面"""
        # 信息区域
        InfoFrame = ttk.LabelFrame(self.Root, text="项目信息", padding=10)
        InfoFrame.pack(fill=tk.X, padx=10, pady=5)

        # 项目名
        ProjFrame = ttk.Frame(InfoFrame)
        ProjFrame.pack(fill=tk.X, pady=2)
        ttk.Label(ProjFrame, text="项目:", width=8).pack(side=tk.LEFT)
        self.ProjectLabel = ttk.Label(ProjFrame, text="检测中...", foreground="gray")
        self.ProjectLabel.pack(side=tk.LEFT, fill=tk.X)

        # 引擎版本
        EngineFrame = ttk.Frame(InfoFrame)
        EngineFrame.pack(fill=tk.X, pady=2)
        ttk.Label(EngineFrame, text="引擎:", width=8).pack(side=tk.LEFT)
        self.EngineLabel = ttk.Label(EngineFrame, text="检测中...", foreground="gray")
        self.EngineLabel.pack(side=tk.LEFT, fill=tk.X)

        # 状态
        StatusFrame = ttk.Frame(InfoFrame)
        StatusFrame.pack(fill=tk.X, pady=2)
        ttk.Label(StatusFrame, text="状态:", width=8).pack(side=tk.LEFT)
        self.StatusLabel = ttk.Label(StatusFrame, text="就绪", foreground="blue")
        self.StatusLabel.pack(side=tk.LEFT)

        # 日志区域
        LogFrame = ttk.LabelFrame(self.Root, text="编译日志", padding=10)
        LogFrame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.LogText = scrolledtext.ScrolledText(
            LogFrame,
            height=15,
            font=("Consolas", 9),
            state=tk.DISABLED,
            wrap=tk.WORD
        )
        self.LogText.pack(fill=tk.BOTH, expand=True)

    def _Log(self, Msg: str):
        """添加日志"""
        Timestamp = datetime.now().strftime("%H:%M:%S")
        self.LogText.config(state=tk.NORMAL)
        self.LogText.insert(tk.END, f"[{Timestamp}] {Msg}\n")
        self.LogText.see(tk.END)
        self.LogText.config(state=tk.DISABLED)

    def _LoadProjectInfo(self):
        """加载项目信息"""
        self._Log("正在检测项目信息...")

        self.ProjectData = LoadProjectInfo(self.ScriptDir)

        if self.ProjectData.ErrorMsg:
            self._Log(f"错误: {self.ProjectData.ErrorMsg}")
            self.StatusLabel.config(text="错误", foreground="red")
            return

        self.ProjectLabel.config(text=self.ProjectData.Name, foreground="black")
        self.EngineLabel.config(text=f"Unreal Engine {self.ProjectData.EngineVersion}", foreground="black")
        self._Log(f"找到项目: {self.ProjectData.Name}")
        self._Log(f"引擎版本: {self.ProjectData.EngineVersion}")
        self._Log(f"引擎路径: {self.ProjectData.EnginePath}")

        # 自动开始编译
        self.Root.after(500, self._StartBuild)

    def _StartBuild(self):
        """开始编译"""
        self.StatusLabel.config(text="编译中...", foreground="orange")
        self._Log("开始编译项目...")

        self.BuildMgr.StartBuild(
            ProjectName=self.ProjectData.Name,
            ProjectPath=self.ProjectData.Path,
            EnginePath=self.ProjectData.EnginePath,
            OnLog=lambda Msg: self.Root.after(0, lambda: self._Log(Msg)),
            OnSuccess=lambda: self.Root.after(0, self._OnBuildSuccess),
            OnError=lambda Msg: self.Root.after(0, lambda: self._OnBuildError(Msg))
        )

    def _OnBuildSuccess(self):
        """编译成功，自动打开项目并关闭"""
        self.StatusLabel.config(text="编译成功!", foreground="green")
        self._Log("=" * 50)
        self._Log("编译成功完成!")
        self._Log("=" * 50)

        # 自动打开项目
        self._Log(f"正在打开项目: {self.ProjectData.Path}")
        Success, ErrorMsg = self.BuildMgr.OpenProject(
            self.ProjectData.Path,
            self.ProjectData.EnginePath
        )

        if Success:
            self._Log("编辑器启动中，即将关闭...")
            self.Root.after(1500, self.Root.quit)
        else:
            self._Log(f"错误: {ErrorMsg}")
            self.StatusLabel.config(text="打开失败", foreground="red")

    def _OnBuildError(self, ErrorMsg: str):
        """编译失败，保持显示等待用户关闭"""
        self.StatusLabel.config(text="编译失败", foreground="red")
        self._Log(f"错误: {ErrorMsg}")
        self._Log("=" * 50)
        self._Log("编译失败，请检查日志后手动关闭窗口")
        self._Log("=" * 50)

    def Run(self):
        """运行应用"""
        self.Root.mainloop()
