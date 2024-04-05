import pytest

from rapidswarm.models.scanners import BaseScanner


class DummyScanner(BaseScanner):
    pass


def test_base_scanner_scan_not_implemented():
    dummy_scanner = DummyScanner()
    with pytest.raises(NotImplementedError):
        dummy_scanner.scan()


def test_base_scanner_validate_not_implemented():
    dummy_scanner = DummyScanner()
    with pytest.raises(NotImplementedError):
        dummy_scanner.validate()


class ImplementedScanner(BaseScanner):
    def scan(self):
        return "scan implemented"

    def validate(self):
        return "validate implemented"


def test_implemented_scanner_scan():
    scanner = ImplementedScanner()
    assert scanner.scan() == "scan implemented"


def test_implemented_scanner_validate():
    scanner = ImplementedScanner()
    assert scanner.validate() == "validate implemented"
