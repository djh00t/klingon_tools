import pytest
from klingon_tools.logtools import LogTools
import subprocess
from unittest.mock import patch

def test_command_state_decorator_success(mocker):
    mock_run = mocker.patch('subprocess.run')
    mock_run.return_value.returncode = 0

    @LogTools.method_state(name="Test Command")
    def dummy_command():
        return "echo 'Hello, World!'"

    dummy_command()
    mock_run.assert_called_once_with("echo 'Hello, World!'", check=True, shell=True)

def test_command_state_decorator_error(mocker):
    mock_run = mocker.patch('subprocess.run')
    mock_run.side_effect = subprocess.CalledProcessError(returncode=2, cmd="echo 'Hello, World!'")

    @LogTools.method_state(name="Test Command")
    def dummy_command():
        return "echo 'Hello, World!'"

    with pytest.raises(subprocess.CalledProcessError):
        dummy_command()
    mock_run.assert_called_once_with("echo 'Hello, World!'", check=True, shell=True)

def test_command_state_success(mocker):
    mock_run = mocker.patch('subprocess.run')
    mock_run.return_value.returncode = 0

    @LogTools.method_state(name="Test Command")
    def dummy_command():
        return "echo 'Hello, World!'"

    dummy_command()
    mock_run.assert_called_once_with("echo 'Hello, World!'", check=True, shell=True)

def test_command_state_error(mocker):
    mock_run = mocker.patch('subprocess.run')
    mock_run.side_effect = subprocess.CalledProcessError(returncode=2, cmd="echo 'Hello, World!'")

    @LogTools.method_state(name="Test Command")
    def dummy_command():
        return "echo 'Hello, World!'"

    with pytest.raises(subprocess.CalledProcessError):
        dummy_command()
    mock_run.assert_called_once_with("echo 'Hello, World!'", check=True, shell=True)
def test_command_state_error(mocker):
    mock_run = mocker.patch('subprocess.run')
    mock_run.side_effect = subprocess.CalledProcessError(returncode=2, cmd="echo 'Hello, World!'")

    commands = [("echo 'Hello, World!'", "Test Command")]

    with pytest.raises(subprocess.CalledProcessError) as excinfo:
        LogTools.command_state(commands)
    assert excinfo.value.returncode == 2
    assert excinfo.value.cmd == "echo 'Hello, World!'"
    mock_run.assert_called_once_with("echo 'Hello, World!'", check=True, shell=True)
