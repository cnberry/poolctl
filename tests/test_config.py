from poolctl.config import get_adapter_config, load_config, set_adapter_config


def test_load_config_missing(monkeypatch, tmp_path):
    monkeypatch.setattr("poolctl.config.CONFIG_DIR", tmp_path / ".config" / "poolctl")
    monkeypatch.setattr("poolctl.config.CONFIG_PATH", tmp_path / ".config" / "poolctl" / "config.json")
    assert load_config() == {}
    assert get_adapter_config() is None


def test_set_and_get_adapter_config(monkeypatch, tmp_path):
    monkeypatch.setattr("poolctl.config.CONFIG_DIR", tmp_path / ".config" / "poolctl")
    monkeypatch.setattr("poolctl.config.CONFIG_PATH", tmp_path / ".config" / "poolctl" / "config.json")
    set_adapter_config({"ip": "192.168.4.33", "port": 80, "name": "Pentair: 07-DF-E2", "gtype": 2, "gsubtype": 12})
    adapter = get_adapter_config()
    assert adapter["ip"] == "192.168.4.33"
    assert adapter["port"] == 80
    assert adapter["name"] == "Pentair: 07-DF-E2"
