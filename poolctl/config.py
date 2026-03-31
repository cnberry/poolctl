from __future__ import annotations

import json
from pathlib import Path
from typing import Any

CONFIG_DIR = Path.home() / ".config" / "poolctl"
CONFIG_PATH = CONFIG_DIR / "config.json"


def load_config() -> dict[str, Any]:
    if not CONFIG_PATH.exists():
        return {}
    return json.loads(CONFIG_PATH.read_text())


def save_config(config: dict[str, Any]) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(config, indent=2, sort_keys=True) + "\n")


def get_adapter_config() -> dict[str, Any] | None:
    config = load_config()
    adapter = config.get("adapter")
    if not isinstance(adapter, dict):
        return None
    return adapter


def set_adapter_config(adapter: dict[str, Any]) -> None:
    config = load_config()
    config["adapter"] = {
        "ip": adapter.get("ip"),
        "port": adapter.get("port", 80),
        "name": adapter.get("name"),
        "gtype": adapter.get("gtype"),
        "gsubtype": adapter.get("gsubtype"),
    }
    save_config(config)
