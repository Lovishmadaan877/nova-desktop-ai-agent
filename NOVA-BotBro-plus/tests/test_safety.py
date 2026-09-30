from nova.orchestrator import SENSITIVE_WORDS
from nova.computer import ALLOWED_APPS


def test_sensitive_words():
    assert {'delete', 'password', 'purchase'} <= SENSITIVE_WORDS


def test_command_shell_is_not_allowlisted():
    assert 'cmd.exe' not in ALLOWED_APPS
    assert 'powershell.exe' not in ALLOWED_APPS


def test_safe_apps_are_allowlisted():
    assert {'mspaint.exe', 'notepad.exe', 'calc.exe'} <= ALLOWED_APPS
