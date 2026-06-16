"""Supergit 설정 관리 모듈"""

import json
import os
from pathlib import Path


CONFIG_PATH = Path.home() / ".supergit" / "config.json"


def _default_config():
    return {
        "language": "ko",
        "theme": "dark",
        "recent_repos": [],
    }


def load_config() -> dict:
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            default = _default_config()
            default.update(cfg)
            return default
        except Exception:
            pass
    return _default_config()


def save_config(cfg: dict):
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)


def add_recent_repo(cfg: dict, path: str):
    repos = cfg.get("recent_repos", [])
    if path in repos:
        repos.remove(path)
    repos.insert(0, path)
    cfg["recent_repos"] = repos[:10]  # 최대 10개
