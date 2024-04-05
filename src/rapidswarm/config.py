import os
from typing import Dict, List

import yaml
from loguru import logger
from pydantic import BaseModel, field_validator

from .models.reporters import BaseReporter  # noqa: F401
from .models.scanners import BaseScanner  # noqa: F401
from .plugin_loader import load_plugins


class ScannerConfig(BaseModel):
    type: str
    config: Dict

    @field_validator("type")
    def validate_type(cls, v):
        loaded_plugins = load_plugins()
        loaded_scanners = loaded_plugins["scanners"]
        if v not in loaded_scanners:
            logger.error(
                f"Invalid scanner type: {v}. Available types: {', '.join(loaded_scanners)}"
            )
            raise ValueError(
                f"Invalid scanner type: {v}. Available types: {', '.join(loaded_scanners)}"
            )
        return v


class ProbeConfig(BaseModel):
    type: str
    config: Dict

    @field_validator("type")
    def validate_type(cls, v):
        loaded_plugins = load_plugins()
        loaded_probes = loaded_plugins["probes"]
        if v not in loaded_probes:
            logger.error(
                f"Invalid probe type: {v}. Available types: {', '.join(loaded_probes)}"
            )
            raise ValueError(
                f"Invalid probe type: {v}. Available types: {', '.join(loaded_probes)}"
            )
        return v


class ManagerConfig(BaseModel):
    type: str
    config: Dict
    probes: List[ProbeConfig]

    @field_validator("type")
    def validate_type(cls, v):
        loaded_plugins = load_plugins()
        loaded_managers = loaded_plugins["managers"]
        if v not in loaded_managers:
            logger.error(
                f"Invalid manager type: {v}. Available types: {', '.join(loaded_managers)}"
            )
            raise ValueError(
                f"Invalid manager type: {v}. Available types: {', '.join(loaded_managers)}"
            )
        return v


class ReporterConfig(BaseModel):
    type: str
    config: Dict

    @field_validator("type")
    def validate_type(cls, v):
        loaded_plugins = load_plugins()
        loaded_reporters = loaded_plugins["reporters"]
        if v not in loaded_reporters:
            logger.error(
                f"Invalid reporter type: {v}. Available types: {', '.join(loaded_reporters)}"
            )
            raise ValueError(
                f"Invalid reporter type: {v}. Available types: {', '.join(loaded_reporters)}"
            )
        return v


class Config(BaseModel):
    scanners: List[ScannerConfig]
    managers: List[ManagerConfig]
    reporters: List[ReporterConfig]


def load_config(config_file):
    config_file_path = os.path.abspath(config_file)
    try:
        with open(config_file_path, "r") as file:
            config_data = yaml.safe_load(file)
            config = Config(**config_data)
            logger.debug(f"Loaded configuration: {config}")
            return config
    except FileNotFoundError as e:
        logger.error(f"Configuration file '{config_file_path}' not found.")
        raise FileNotFoundError(
            f"Configuration file '{config_file_path}' not found."
        ) from e
    except Exception as e:
        logger.exception(f"Error loading configuration: {e}")
        raise


def create_scanners(config):
    loaded_plugins = load_plugins()
    loaded_scanners = loaded_plugins["scanners"]
    return [
        scanner_class(**scanner_config.config)
        for scanner_config in config.scanners
        for scanner_class in loaded_scanners.values()
        if scanner_class.__name__ == scanner_config.type
    ]


def create_reporters(config):
    loaded_plugins = load_plugins()
    loaded_reporters = loaded_plugins["reporters"]
    return [
        reporter_class(**reporter_config.config)
        for reporter_config in config.reporters
        for reporter_class in loaded_reporters.values()
        if reporter_class.__name__ == reporter_config.type
    ]


def create_managers(config, nodes):
    logger.debug(f"Creating managers from config: {config}")
    loaded_plugins = load_plugins()
    logger.debug(f"Loaded plugins: {loaded_plugins}")
    loaded_managers = loaded_plugins["managers"]
    logger.debug(f"Loaded managers: {loaded_managers}")
    loaded_probes = loaded_plugins["probes"]
    logger.debug(f"Loaded probes: {loaded_probes}")

    managers = []
    for manager_config in config.managers:
        probes = []
        for probe_config in manager_config.probes:
            probe_class = loaded_probes[probe_config.type]
            probe = probe_class(nodes=nodes, **probe_config.config)
            probes.append(probe)

        manager_class = loaded_managers[manager_config.type]
        manager = manager_class(probes=probes, **manager_config.config)
        managers.append(manager)
        logger.debug(f"Created manager: {manager}")
    return managers
