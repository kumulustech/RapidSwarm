from typing import Dict, List

import yaml
from loguru import logger
from pydantic import BaseModel, validator

from .models.csv_scanner import CSVScanner
from .models.scanners import BaseScanner


def get_scanner_subclasses():
    subclasses = {cls.__name__: cls for cls in BaseScanner.__subclasses__()}
    logger.debug(f"Found scanner subclasses: {subclasses}")
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


class Config(BaseModel):
    scanners: List[ScannerConfig]


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
    for scanner_config in config.scanners:  # Directly iterate over the list
        try:
            scanner_class = scanner_subclasses[scanner_config.type]
            scanner = scanner_class(**scanner_config.config)
            scanners.append(scanner)
            logger.debug(f"Created scanner: {scanner}")
        except KeyError as e:
            logger.error(f"Invalid scanner type: {scanner_config.type}")
            raise ValueError(f"Invalid scanner type: {scanner_config.type}") from e
        except Exception as e:
            logger.exception(f"Error creating scanner: {scanner_config.type}")
            raise
    return scanners
