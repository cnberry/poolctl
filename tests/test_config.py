import stat

from poolctl.config import CONFIG_PATH, get_adapter_config, load_config, set_adapter_config


def test_system_config_path_is_the_default():
    assert CONFIG_PATH.as_posix() == "/usr/local/config/poolctl/config.json"


def test_load_config_missing(monkeypatch, tmp_path):
    monkeypatch.setattr("poolctl.config.CONFIG_DIR", tmp_path / ".config" / "poolctl")
    monkeypatch.setattr(
        "poolctl.config.CONFIG_PATH", tmp_path / ".config" / "poolctl" / "config.json"
    )
    assert load_config() == {}
    assert get_adapter_config() is None


def test_set_and_get_adapter_config(monkeypatch, tmp_path):
    monkeypatch.setattr("poolctl.config.CONFIG_DIR", tmp_path / ".config" / "poolctl")
    monkeypatch.setattr(
        "poolctl.config.CONFIG_PATH", tmp_path / ".config" / "poolctl" / "config.json"
    )
    set_adapter_config(
        {
            "ip": "192.0.2.10",
            "port": 80,
            "name": "Pentair: EXAMPLE",
            "gtype": 2,
            "gsubtype": 12,
        }
    )
    adapter = get_adapter_config()
    assert adapter["ip"] == "192.0.2.10"
    assert adapter["port"] == 80
    assert adapter["name"] == "Pentair: EXAMPLE"
    mode = stat.S_IMODE((tmp_path / ".config" / "poolctl" / "config.json").stat().st_mode)
    assert mode == 0o600


def test_config_path_can_be_overridden(monkeypatch, tmp_path):
    override = tmp_path / "private" / "pool.json"
    monkeypatch.setenv("POOLCTL_CONFIG", str(override))
    set_adapter_config({"ip": "192.0.2.10", "port": 80})
    assert override.exists()
    assert get_adapter_config()["ip"] == "192.0.2.10"
