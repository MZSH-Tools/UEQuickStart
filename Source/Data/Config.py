# -*- coding: utf-8 -*-
"""配置管理模块"""

import json
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional

# 默认配置文件名
CONFIG_FILE_NAME = "UEQuickBuild.json"


@dataclass
class BuildConfig:
    """编译配置"""
    Platform: str = "Win64"
    Configuration: str = "Development"
    AdditionalArgs: list[str] = field(default_factory=list)


@dataclass
class AppConfig:
    """应用配置"""
    Build: BuildConfig = field(default_factory=BuildConfig)


def LoadConfig(ConfigDir: Path) -> AppConfig:
    """加载配置文件，不存在则返回默认配置"""
    ConfigPath = ConfigDir / CONFIG_FILE_NAME
    if not ConfigPath.exists():
        return AppConfig()

    try:
        with open(ConfigPath, 'r', encoding='utf-8') as F:
            Data = json.load(F)

        BuildData = Data.get("Build", {})
        Build = BuildConfig(
            Platform=BuildData.get("Platform", "Win64"),
            Configuration=BuildData.get("Configuration", "Development"),
            AdditionalArgs=BuildData.get("AdditionalArgs", [])
        )

        return AppConfig(Build=Build)
    except Exception:
        return AppConfig()


def SaveConfig(ConfigDir: Path, Config: AppConfig) -> bool:
    """保存配置文件"""
    ConfigPath = ConfigDir / CONFIG_FILE_NAME
    try:
        with open(ConfigPath, 'w', encoding='utf-8') as F:
            json.dump(asdict(Config), F, indent=2, ensure_ascii=False)
        return True
    except Exception:
        return False
