from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

ENV_CONFIG_PATH = "POOLCTL_CONFIG"
CONFIG_DIR = Path("/usr/local/config/poolctl")
CONFIG_PATH = CONFIG_DIR / "config.json"


def config_path() -> Path:
    override = os.environ.get(ENV_CONFIG_PATH)
    return Path(override).expanduser() if override else CONFIG_PATH


def load_config() -> dict[str, Any]:
    path = config_path()
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def save_config(config: dict[str, Any]) -> None:
    path = config_path()
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    path.parent.chmod(0o700)
    flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC
    descriptor = os.open(path, flags, 0o600)
    with os.fdopen(descriptor, "w") as config_file:
        json.dump(config, config_file, indent=2, sort_keys=True)
        config_file.write("\n")
    path.chmod(0o600)


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
