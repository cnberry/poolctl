import pytest

from poolctl.control import find_circuit, normalize_name


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
