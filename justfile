set shell := ["bash", "-cu"]

venv := ".venv"
python := venv + "/bin/python"
pip := venv + "/bin/pip"
pytest := venv + "/bin/pytest"

default:
    just --list

install:
    ./script/install

reinstall:
    ./script/install

setup:
    python3 -m venv {{venv}}
    {{pip}} install -e ".[dev]"

test:
    {{venv}}/bin/ruff format --check poolctl tests
    {{venv}}/bin/ruff check poolctl tests
    {{venv}}/bin/detect-secrets scan --baseline .secrets.baseline
    PYTHONPATH=. {{pytest}} -q

test-integration:
    poolctl status --help >/dev/null

test-all:
    just test
    just test-integration

discover:
    poolctl discover

status:
    poolctl status

circuits:
    poolctl circuits

bodies:
    poolctl bodies

pumps:
    poolctl pumps

raw:
    poolctl status --raw
