# -*- coding: utf-8 -*-
"""统一日志模块"""

import logging
import sys

# 全局 Logger 实例
GLogger: logging.Logger = None


def SetupLogger(Name: str = "UEBuildTool", Level: int = logging.DEBUG) -> logging.Logger:
    """初始化日志模块"""
    global GLogger

    GLogger = logging.getLogger(Name)
    GLogger.setLevel(Level)

    # 避免重复添加 Handler
    if not GLogger.handlers:
        Handler = logging.StreamHandler(sys.stdout)
        Handler.setLevel(Level)
        Formatter = logging.Formatter("[%(levelname)s] %(message)s")
        Handler.setFormatter(Formatter)
        GLogger.addHandler(Handler)

    return GLogger


def GetLogger() -> logging.Logger:
    """获取 Logger 实例"""
    global GLogger
    if GLogger is None:
        SetupLogger()
    return GLogger


def Debug(Msg: str):
    """调试日志"""
    GetLogger().debug(Msg)


def Info(Msg: str):
    """信息日志"""
    GetLogger().info(Msg)


def Warning(Msg: str):
    """警告日志"""
    GetLogger().warning(Msg)


def Error(Msg: str):
    """错误日志"""
    GetLogger().error(Msg)
