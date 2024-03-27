from typing import Dict, List

import yaml
from loguru import logger
from pydantic import BaseModel, validator

from .models.arp_scanner import ARPScanner  # noqa: F401
from .models.csv_scanner import CSVScanner  # noqa: F401
from .models.managers import BaseManager, SequentialManager  # noqa: F401
from .models.probes import BaseProbe, PingProbe  # noqa: F401
from .models.scanners import BaseScanner


def get_scanner_subclasses():
    subclasses = {cls.__name__: cls for cls in BaseScanner.__subclasses__()}
    logger.debug(f"Found scanner subclasses: {subclasses}")
    return subclasses


def get_probe_subclasses():
    subclasses = {cls.__name__: cls for cls in BaseProbe.__subclasses__()}
    logger.debug(f"Found probe subclasses: {subclasses}")
    return subclasses


def get_manager_subclasses():
    subclasses = {cls.__name__: cls for cls in BaseManager.__subclasses__()}
    logger.debug(f"Found manager subclasses: {subclasses}")
    return subclasses


class ScannerConfig(BaseModel):
    type: str
    config: Dict

    @validator("type")
    def validate_type(cls, v):
        scanner_subclasses = get_scanner_subclasses()
        if v not in scanner_subclasses:
            logger.error(
                f"Invalid scanner type: {v}. Available types: {', '.join(scanner_subclasses)}"
            )
            raise ValueError(
                f"Invalid scanner type: {v}. Available types: {', '.join(scanner_subclasses)}"
            )
        return v


class ProbeConfig(BaseModel):
    type: str
    config: Dict

    @validator("type")
    def validate_type(cls, v):
        probe_subclasses = get_probe_subclasses()
        if v not in probe_subclasses:
            logger.error(
                f"Invalid probe type: {v}. Available types: {', '.join(probe_subclasses)}"
            )
            raise ValueError(
                f"Invalid probe type: {v}. Available types: {', '.join(probe_subclasses)}"
            )
        return v


class ManagerConfig(BaseModel):
    type: str
    config: Dict
    probes: List[ProbeConfig]

    @validator("type")
    def validate_type(cls, v):
        manager_subclasses = get_manager_subclasses()
        if v not in manager_subclasses:
            logger.error(
                f"Invalid manager type: {v}. Available types: {', '.join(manager_subclasses)}"
            )
            raise ValueError(
                f"Invalid manager type: {v}. Available types: {', '.join(manager_subclasses)}"
            )
        return v


class Config(BaseModel):
    scanners: List[ScannerConfig]
    managers: List[ManagerConfig]


def load_config(config_file):
    try:
        with open(config_file, "r") as file:
            config_data = yaml.safe_load(file)
            config = Config(**config_data)
            logger.debug(f"Loaded configuration: {config}")
            return config
    except FileNotFoundError as e:
        logger.error(f"Configuration file '{config_file}' not found.")
        raise FileNotFoundError(f"Configuration file '{config_file}' not found.") from e
    except Exception as e:
        logger.exception(f"Error loading configuration: {e}")
        raise


def create_scanners(config):
    scanner_subclasses = get_scanner_subclasses()
    scanners = []
    for scanner_config in config.scanners:
        try:
            scanner_class = scanner_subclasses[scanner_config.type]
            scanner = scanner_class(**scanner_config.config)
            scanners.append(scanner)
            logger.debug(f"Created scanner: {scanner}")
        except KeyError as e:
            error_message = f"Invalid scanner type: {scanner_config.type}"
            logger.error(error_message)
            raise ValueError(error_message) from e
        except Exception as e:
            logger.exception(f"Error creating scanner: {scanner_config.type}")
            raise RuntimeError(
                f"Unexpected error creating scanner: {scanner_config.type}"
            ) from e
    return scanners


def create_managers(config, nodes):
    """
    Creates manager instances based on the provided configuration.

    Args:
        config (Config): The configuration object containing manager configurations.
        nodes (list): The list of nodes to be managed.

    Returns:
        list: A list of instantiated manager objects.
    """
    manager_subclasses = get_manager_subclasses()
    probe_subclasses = get_probe_subclasses()
    managers = []
    for manager_config in config.managers:
        probes = []
        for probe_config in manager_config.probes:
            probe_class = probe_subclasses[probe_config.type]
            probe = probe_class(nodes=nodes, **probe_config.config)
            probes.append(probe)

        manager_class = manager_subclasses[manager_config.type]
        manager = manager_class(probes=probes, **manager_config.config)
        managers.append(manager)
        logger.debug(f"Created manager: {manager}")
    return managers
