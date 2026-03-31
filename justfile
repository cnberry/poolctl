set shell := ["bash", "-cu"]

venv := ".venv"
python := venv + "/bin/python"
pip := venv + "/bin/pip"
pytest := venv + "/bin/pytest"

default:
    just --list

setup:
    python3 -m venv {{venv}}
    {{pip}} install -e .
    {{pip}} install pytest

test:
    PYTHONPATH=. {{pytest}} -q

discover:
    {{python}} poolctl.py discover

status:
    {{python}} poolctl.py status

circuits:
    {{python}} poolctl.py circuits

bodies:
    {{python}} poolctl.py bodies

pumps:
    {{python}} poolctl.py pumps

raw:
    {{python}} poolctl.py status --raw
