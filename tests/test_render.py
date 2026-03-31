from poolctl.render import enum_value, onoff, render_bodies, render_circuits, render_pumps, render_status, summarize


def sample_payload():
    return {
        "adapter": {"name": "Pentair: EXAMPLE", "ip": "192.168.1.50", "port": 80},
        "data": {
            "controller": {
                "model": {"value": "EasyTouch2 4P"},
                "sensor": {
                    "air_temperature": {"value": 64},
                    "salt_ppm": {"value": 2750},
                },
            },
            "body": {
                "0": {
                    "name": "Pool",
                    "last_temperature": {"value": 66},
                    "heat_mode": {"value": 1, "enum_options": ["Off", "Solar"]},
                    "heat_setpoint": {"value": 85},
                    "heat_state": {"value": 0, "enum_options": ["Off", "Heater"]},
                },
                "1": {
                    "name": "Spa",
                    "last_temperature": {"value": 65},
                    "heat_mode": {"value": 0, "enum_options": ["Off", "Solar"]},
                    "heat_setpoint": {"value": 100},
                    "heat_state": {"value": 0, "enum_options": ["Off", "Heater"]},
                },
            },
            "circuit": {
                "500": {"circuit_id": 500, "name": "Spa", "value": 0, "function": 1, "interface": 1},
                "505": {"circuit_id": 505, "name": "Pool", "value": 1, "function": 2, "interface": 0},
            },
            "pump": {
                "0": {
                    "data": 134,
                    "state": {"value": 1},
                    "rpm_now": {"value": 2750},
                    "watts_now": {"value": 1036},
                    "gpm_now": {"value": 255},
                }
            },
        },
    }


def test_enum_value_handles_valid_and_missing():
    assert enum_value({"value": 1, "enum_options": ["Off", "Solar"]}) == "Solar"
    assert enum_value({"value": 9, "enum_options": ["Off", "Solar"]}) == 9
    assert enum_value(None) is None


def test_onoff():
    assert onoff(0) == "off"
    assert onoff(1) == "on"


def test_summarize():
    summary = summarize(sample_payload())
    assert summary["model"] == "EasyTouch2 4P"
    assert summary["air_temp_f"] == 64
    assert summary["salt_ppm"] == 2750
    assert summary["bodies"]["0"]["heat_mode"] == "Solar"
    assert summary["circuits"][1]["name"] == "Pool"
    assert summary["pumps"]["0"]["rpm"] == 2750


def test_renderers():
    summary = summarize(sample_payload())
    status = render_status(summary)
    circuits = render_circuits(summary)
    bodies = render_bodies(summary)
    pumps = render_pumps(summary)

    assert "Adapter: Pentair: EXAMPLE @ 192.168.1.50:80" in status
    assert "500  off  Spa" in circuits
    assert "Pool: 66°F, heat_mode=Solar" in bodies
    assert "pump 0: on rpm=2750 watts=1036 gpm=255" in pumps
