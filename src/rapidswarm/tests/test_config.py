from unittest.mock import mock_open, patch

import pytest

from rapidswarm.config import Config, ScannerConfig, create_scanners, load_config
from rapidswarm.models.scanners import BaseScanner


# Mocking a subclass of BaseScanner for testing
class MockScanner(BaseScanner):
    pass


# Fixture to mock the yaml.safe_load function
@pytest.fixture
def mock_yaml_safe_load(monkeypatch):
    def mock_load(*args, **kwargs):
        return {
            "managers": [
                {
                    "name": "manager1",
                    "type": "SequentialManager",
                    "config": {},  # Added an empty config here
                    "probes": [{"type": "DummyProbe", "config": {}}],
                }
            ],
            "scanners": [{"type": "MockScanner", "config": {"some_key": "some_value"}}],
        }

    monkeypatch.setattr("yaml.safe_load", mock_load)


# Fixture to mock get_scanner_subclasses function
@pytest.fixture
def mock_scanner_subclasses(monkeypatch):
    monkeypatch.setattr(
        "rapidswarm.config.get_scanner_subclasses", lambda: {"MockScanner": MockScanner}
    )


def test_load_config(mock_yaml_safe_load):
    with patch("builtins.open", mock_open(read_data="data")) as mock_file:
        config = load_config("dummy_path")
        assert isinstance(config, Config)
        assert len(config.scanners) == 1
        assert config.scanners[0].type == "MockScanner"
        assert len(config.managers) == 1
        assert config.managers[0].type == "SequentialManager"
        assert config.managers[0].probes[0].type == "DummyProbe"
        mock_file.assert_called_once_with("dummy_path", "r")


def test_create_scanners(mock_scanner_subclasses):
    config_data = {
        "managers": [
            {
                "type": "SequentialManager",
                "config": {},  # Added an empty config here
                "probes": [{"type": "DummyProbe", "config": {}}],
            }
        ],
        "scanners": [{"type": "MockScanner", "config": {"some_key": "some_value"}}],
    }
    config = Config(**config_data)
    scanners = create_scanners(config)
    assert len(scanners) == 1
    assert isinstance(scanners[0], MockScanner)


def test_scanner_config_validation_invalid_type():
    with pytest.raises(ValueError):
        ScannerConfig(type="InvalidScanner", config={})


def test_scanner_config_validation_valid_type(mock_scanner_subclasses):
    # Directly creating a ScannerConfig with a valid type should not raise an error
    valid_scanner_config = ScannerConfig(type="MockScanner", config={})
    assert valid_scanner_config.type == "MockScanner"
