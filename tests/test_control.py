import pytest

from poolctl.control import delay_active, extract_delay, find_circuit, normalize_name
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


def test_delay_active():
    assert delay_active({"cleaner": 1, "pool": 0, "spa": 0}) is True
    assert delay_active({"cleaner": 0, "pool": 0, "spa": 0}) is False
    assert delay_active({"cleaner": None, "pool": 0, "spa": 0}) is False


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
