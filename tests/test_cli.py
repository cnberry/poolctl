import subprocess
import sys


def run_cli(*args):
    return subprocess.run(
        [sys.executable, "-m", "poolctl.cli", *args],
        check=False,
        capture_output=True,
        text=True,
    )


def test_heat_command_help_is_available_without_hardware():
    result = run_cli("heat", "status", "--help")
    assert result.returncode == 0
    assert "body name or numeric ID" in result.stdout


def test_heat_writes_require_yes_before_hardware_access():
    result = run_cli("heat", "set", "pool", "solar-preferred")
    assert result.returncode != 0
    assert "Refusing to change heat settings without --yes" in result.stderr
