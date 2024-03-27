import argparse
import sys
from pathlib import Path

from loguru import logger
from pydantic import ValidationError

from rapidswarm.config import (
    create_managers,
    create_reporters,
    create_scanners,
    load_config,
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


def main():
    parser = argparse.ArgumentParser(
        description="RapidSwarm - A network scanning and testing tool."
    )
    parser.add_argument(
        "config_file", type=str, help="Path to the YAML configuration file."
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose logging."
    )
    args = parser.parse_args()

    if args.verbose:
        logger.remove()
        logger.add(sys.stderr, level="DEBUG")
    else:
        logger.remove()
        logger.add(sys.stderr, level="INFO")

    config_file = Path(args.config_file)
    if not config_file.is_file():
        logger.error(f"Configuration file '{config_file}' not found.")
        return

    try:
        rapidswarm = RapidSwarm(config_file, verbose=args.verbose)
        rapidswarm.load_config()
        rapidswarm.create_scanners()
        rapidswarm.run_scanners()

        # Create and run managers and reporters within the RapidSwarm instance
        rapidswarm.create_managers()
        rapidswarm.create_reporters()
        results = rapidswarm.run_managers()

        logger.info(f"Scan and testing results: {results}")

    except FileNotFoundError as e:
        logger.error(f"Error: {e}")
    except ValidationError as e:
        logger.error(f"Error: {e}")
    except Exception as e:
        logger.exception(f"An unexpected error occurred: {e}")
        if args.verbose:
            logger.debug(f"Config: {rapidswarm.config}")
            logger.debug(f"Scanners: {rapidswarm.scanners}")
            logger.debug(f"Managers: {rapidswarm.managers}")
            logger.debug(f"Reporters: {rapidswarm.reporters}")


if __name__ == "__main__":
    main()
