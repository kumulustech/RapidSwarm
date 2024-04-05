# rapidswarm.py

from pydantic import ValidationError

from loguru import logger

from rapidswarm.config import (
    load_config,
    create_scanners,
    create_managers,
    create_reporters,
)


class RapidSwarm:
    def __init__(self, config_file, verbose=False):
        self.config_file = config_file
        self.config = None
        self.scanners = []
        self.managers = []
        self.reporters = []
        self.scanned_nodes = []
        self.verbose = verbose

    def load_config(self):
        try:
            self.config = load_config(self.config_file)
            logger.debug(f"Loaded configuration from {self.config_file}")
        except FileNotFoundError as e:
            logger.error(f"Configuration file '{self.config_file}' not found.")
            raise FileNotFoundError(
                f"Configuration file '{self.config_file}' not found."
            ) from e
        except ValidationError as e:
            logger.error(f"Invalid configuration: {e}")
            raise ValidationError(f"Invalid configuration: {e}") from e

    def create_scanners(self):
        try:
            self.scanners = create_scanners(self.config)
            logger.debug(f"Created scanners: {self.scanners}")
        except ValidationError as e:
            logger.error(f"Invalid scanner configuration: {e}")
            raise ValidationError(f"Invalid scanner configuration: {e}") from e

    def create_reporters(self):
        try:
            self.reporters = create_reporters(self.config)
            logger.debug(f"Created reporters: {self.reporters}")
        except ValidationError as e:
            logger.error(f"Invalid reporter configuration: {e}")
            raise ValidationError(f"Invalid reporter configuration: {e}") from e

    def run_scanners(self):
        scanned_nodes = []
        for scanner in self.scanners:
            logger.info(f"Running scanner: {type(scanner).__name__}")
            nodes = scanner.scan()
            scanned_nodes.extend(nodes)
            logger.info("Scanned nodes:")
            for node in nodes:
                logger.info(node)
            logger.info("")
        self.scanned_nodes = scanned_nodes

    def create_managers(self):
        try:
            self.managers = create_managers(self.config, self.scanned_nodes)
            logger.debug(f"Created managers: {self.managers}")
        except ValidationError as e:
            logger.error(f"Invalid manager configuration: {e}")
            raise ValidationError(f"Invalid manager configuration: {e}") from e

    def run_managers(self):
        results = []
        for manager in self.managers:
            manager_results = manager.run()
            results.extend(manager_results)

        # Run the reporters after the managers have finished
        for reporter in self.reporters:
            reporter.report(results)

        return results
