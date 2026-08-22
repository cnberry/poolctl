import asyncio

import pytest

from poolctl import control
from poolctl.control import HEAT_MODES, extract_delay, find_body, find_circuit, normalize_name
from poolctl.protocol import CANCEL_DELAY_QUERY


@pytest.fixture
def summary():
    return {
        "circuits": [
            {"id": 501, "name": "Cleaner", "state": "off"},
            {"id": 502, "name": "Pool Light", "state": "off"},
            {"id": 503, "name": "High Speed", "state": "off"},
        ]
    }


def test_normalize_name():
    assert normalize_name("  Pool   Light ") == "pool light"


def test_find_circuit_exact(summary):
    circuit = find_circuit(summary, "Cleaner")
    assert circuit["id"] == 501


def test_find_circuit_partial(summary):
    circuit = find_circuit(summary, "pool light")
    assert circuit["id"] == 502


def test_find_circuit_missing(summary):
    with pytest.raises(ValueError, match="No circuit matched"):
        find_circuit(summary, "Jets")


def test_extract_delay():
    data = {
        "controller": {
            "sensor": {
                "cleaner_delay": {"value": 1},
                "pool_delay": {"value": 0},
                "spa_delay": {"value": 2},
            }
        }
    }
    assert extract_delay(data) == {"cleaner": 1, "pool": 0, "spa": 2}


def test_cancel_delay_opcode_is_pinned():
    assert CANCEL_DELAY_QUERY == 12580


def heat_data():
    return {
        "controller": {"sensor": {}},
        "body": {
            "0": {
                "body_type": 0,
                "name": "Pool",
                "last_temperature": {"value": 79},
                "heat_mode": {
                    "value": 1,
                    "enum_options": ["Off", "Solar", "Solar Preferred", "Heater"],
                },
                "heat_setpoint": {"value": 88},
                "heat_state": {"value": 1, "enum_options": ["Off", "Solar", "Heater"]},
                "min_setpoint": 40,
                "max_setpoint": 104,
            },
            "1": {
                "body_type": 1,
                "name": "Spa",
                "last_temperature": {"value": 70},
                "heat_mode": {
                    "value": 0,
                    "enum_options": ["Off", "Solar", "Solar Preferred", "Heater"],
                },
                "heat_setpoint": {"value": 100},
                "heat_state": {"value": 0, "enum_options": ["Off", "Solar", "Heater"]},
                "min_setpoint": 40,
                "max_setpoint": 104,
            },
        },
        "circuit": {},
        "pump": {},
    }


def heat_summary():
    return control.summarize({"adapter": {}, "data": heat_data()})


def test_find_body_accepts_exact_name_or_id():
    assert find_body(heat_summary(), "pool")["id"] == 0
    assert find_body(heat_summary(), "1")["name"] == "Spa"
    with pytest.raises(ValueError, match="No body matched"):
        find_body(heat_summary(), "hot tub")


def test_heat_mode_contract_is_stable():
    assert HEAT_MODES == {"off": 0, "solar": 1, "solar-preferred": 2, "heater": 3}


def test_heat_status_returns_all_bodies_or_one_body(monkeypatch):
    async def fetch_status(host=None):
        return {"adapter": {}, "data": heat_data()}

    monkeypatch.setattr(control, "fetch_status", fetch_status)
    bodies = asyncio.run(control.heat_status())
    assert set(bodies) == {"0", "1"}
    assert asyncio.run(control.heat_status("pool"))["heat_setpoint_f"] == 88


class FakeHeatGateway:
    instances = []

    def __init__(self):
        self.data = heat_data()
        self.mode_writes = []
        self.temp_writes = []
        self.instances.append(self)

    async def async_connect(self, **adapter):
        self.adapter = adapter

    async def async_update(self):
        return None

    def get_data(self):
        return self.data

    async def async_set_heat_mode(self, body, mode):
        self.mode_writes.append((body, mode))
        self.data["body"][str(body)]["heat_mode"]["value"] = mode

    async def async_set_heat_temp(self, body, temperature):
        self.temp_writes.append((body, temperature))
        self.data["body"][str(body)]["heat_setpoint"]["value"] = temperature

    async def async_disconnect(self):
        return None


def install_fake_heat_gateway(monkeypatch):
    FakeHeatGateway.instances.clear()

    async def resolve_adapter(host=None):
        return {"ip": host or "192.0.2.10", "port": 80}

    monkeypatch.setattr(control, "ScreenLogicGateway", FakeHeatGateway)
    monkeypatch.setattr(control, "resolve_adapter", resolve_adapter)


def test_set_heat_mode_reports_post_write_state(monkeypatch):
    install_fake_heat_gateway(monkeypatch)
    result = asyncio.run(control.set_heat_mode("pool", "solar-preferred"))
    gateway = FakeHeatGateway.instances[0]
    assert gateway.mode_writes == [(0, 2)]
    assert result["status_before"]["heat_mode"] == "Solar"
    assert result["status_after"]["heat_mode"] == "Solar Preferred"


def test_set_heat_temp_validates_limits_and_reports_state(monkeypatch):
    install_fake_heat_gateway(monkeypatch)
    result = asyncio.run(control.set_heat_temp("pool", 90))
    gateway = FakeHeatGateway.instances[0]
    assert gateway.temp_writes == [(0, 90)]
    assert result["status_after"]["heat_setpoint_f"] == 90

    with pytest.raises(ValueError, match="between 40 and 104"):
        asyncio.run(control.set_heat_temp("pool", 105))
    assert FakeHeatGateway.instances[1].temp_writes == []
