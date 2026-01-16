# -*- coding: utf-8 -*-
"""项目信息数据访问层"""

import json
import os
import re
import winreg
from pathlib import Path
from dataclasses import dataclass


@dataclass
class ProjectData:
    """项目数据"""
    Name: str = ""
    Path: Path = None
    EngineVersion: str = ""
    EnginePath: str = ""
    ErrorMsg: str = ""


def FindUProject(SearchDir: Path) -> Path:
    """查找 .uproject 文件"""
    UProjectFiles = list(SearchDir.glob("*.uproject"))
    return UProjectFiles[0] if UProjectFiles else None


def ReadProjectFile(UProjectPath: Path) -> dict:
    """读取 .uproject 文件内容"""
    with open(UProjectPath, 'r', encoding='utf-8') as F:
        return json.load(F)


def IsGUID(Value: str) -> bool:
    """判断字符串是否为 GUID 格式（源码编译的引擎使用 GUID 标识）"""
    GuidPattern = r"^\{?[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\}?$"
    return bool(re.match(GuidPattern, Value))


def GetEnginePathFromBuilds(Guid: str) -> str:
    """从注册表 Builds 获取源码编译引擎路径（GUID 关联）"""
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"SOFTWARE\Epic Games\Unreal Engine\Builds") as Key:
            Value, _ = winreg.QueryValueEx(Key, Guid)
            if Value and Path(Value).exists():
                return Value
    except WindowsError:
        pass
    return ""


def GetEnginePathFromRegistry(Version: str) -> str:
    """从 Windows 注册表获取引擎安装路径"""
    RegistryPaths = [
        (winreg.HKEY_LOCAL_MACHINE, rf"SOFTWARE\EpicGames\Unreal Engine\{Version}"),
        (winreg.HKEY_CURRENT_USER, rf"SOFTWARE\EpicGames\Unreal Engine\{Version}"),
        (winreg.HKEY_LOCAL_MACHINE, rf"SOFTWARE\WOW6432Node\EpicGames\Unreal Engine\{Version}"),
    ]

    for HKey, RegPath in RegistryPaths:
        try:
            with winreg.OpenKey(HKey, RegPath) as Key:
                Value, _ = winreg.QueryValueEx(Key, "InstalledDirectory")
                if Value and Path(Value).exists():
                    return Value
        except WindowsError:
            continue
    return ""


def GetEnginePathFromLauncher(Version: str) -> str:
    """从 Epic Games Launcher 配置获取引擎路径"""
    LauncherDatPaths = [
        Path(os.environ.get("PROGRAMDATA", "C:/ProgramData")) / "Epic/UnrealEngineLauncher/LauncherInstalled.dat",
        Path(os.environ.get("LOCALAPPDATA", "")) / "EpicGamesLauncher/Saved/Config/Windows/LauncherInstalled.dat",
    ]

    for DatPath in LauncherDatPaths:
        if DatPath.exists():
            try:
                with open(DatPath, 'r', encoding='utf-8') as F:
                    Data = json.load(F)
                for Item in Data.get("InstallationList", []):
                    if Item.get("AppName", "").endswith(Version):
                        InstallLoc = Item.get("InstallLocation", "")
                        if InstallLoc and Path(InstallLoc).exists():
                            return InstallLoc
            except Exception:
                continue
    return ""


def LoadProjectInfo(ScriptDir: Path) -> ProjectData:
    """加载项目信息"""
    Result = ProjectData()

    # 查找 .uproject 文件
    UProjectPath = FindUProject(ScriptDir)
    if not UProjectPath:
        Result.ErrorMsg = "未找到 .uproject 文件，请将此工具放置在 UE 项目根目录"
        return Result

    Result.Path = UProjectPath
    Result.Name = UProjectPath.stem

    # 读取引擎版本
    try:
        ProjectJson = ReadProjectFile(UProjectPath)
        Result.EngineVersion = ProjectJson.get("EngineAssociation", "")
    except Exception as E:
        Result.ErrorMsg = f"无法读取 .uproject 文件: {E}"
        return Result

    if not Result.EngineVersion:
        Result.ErrorMsg = "未找到引擎版本信息"
        return Result

    # 获取引擎路径
    if IsGUID(Result.EngineVersion):
        # GUID 格式：源码编译的引擎，从 Builds 注册表获取
        Result.EnginePath = GetEnginePathFromBuilds(Result.EngineVersion)
    else:
        # 版本号格式：优先级 注册表 > Launcher
        Result.EnginePath = (
            GetEnginePathFromRegistry(Result.EngineVersion) or
            GetEnginePathFromLauncher(Result.EngineVersion)
        )

    if not Result.EnginePath:
        Result.ErrorMsg = f"无法找到 Unreal Engine {Result.EngineVersion} 的安装路径"
        return Result

    return Result
