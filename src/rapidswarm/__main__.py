import argparse
import sys
from pathlib import Path

from loguru import logger
from pydantic import ValidationError

from rapidswarm.rapidswarm import RapidSwarm

logger.remove()
logger.add(sys.stderr, level="DEBUG")


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
