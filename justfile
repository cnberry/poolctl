set shell := ["bash", "-cu"]

venv := ".venv"
python := venv + "/bin/python"
pip := venv + "/bin/pip"
pytest := venv + "/bin/pytest"

default:
    just --list

install:
    pipx install --editable .

reinstall:
    -pipx uninstall poolctl
    pipx install --editable .

setup:
    python3 -m venv {{venv}}
    {{pip}} install -e .
    {{pip}} install pytest

test:
    PYTHONPATH=. {{pytest}} -q

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
