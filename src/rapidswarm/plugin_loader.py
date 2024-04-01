import importlib
import inspect
import os
import sys

from loguru import logger

from .models.manager import BaseManager
from .models.probes import BaseProbe
from .models.reporters import BaseReporter
from .models.scanners import BaseScanner

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

PLUGIN_DIRECTORY = os.path.join(project_root, "plugins")


def discover_plugins(plugin_type, base_class):
    # TODO: This is the broken part
    logger.info(f"Discovering {plugin_type} plugins in directory: {PLUGIN_DIRECTORY}")
    plugins = {}
    plugin_dir = os.path.join(PLUGIN_DIRECTORY, plugin_type)
    logger.info(f"Plugin directory: {plugin_dir}")
    logger.info(f"Discovering {plugin_type} plugins in directory: {plugin_dir}")
    logger.info(f"Directory contains: {os.listdir(plugin_dir)}")

    for file in os.listdir(plugin_dir):
        if file.endswith("_plugin.py"):
            logger.info(f"Found plugin file: {file}")
            module_name = file[:-10]  # Remove the "_plugin.py" suffix
            module_path = f"src.plugins.{plugin_type}.{module_name}"
            module = importlib.import_module(module_path)
            import_as = getattr(module, "__import_as__", None)
            if module_name is None:
                logger.error(
                    f"Module {file} does not have a __module_name__ attribute."
                )
                continue
            plugins[import_as or module_name] = getattr(
                module, import_as or module_name
            )

    logger.info(
        f"Finished discovering {plugin_type} plugins. Found {len(plugins)} plugins."
    )
    return plugins


def load_plugins():
    reporters = discover_plugins("reporters", BaseReporter)
    logger.debug(f"Loaded reporters: {reporters}")
    scanners = discover_plugins("scanners", BaseScanner)
    logger.debug(f"Loaded scanners: {scanners}")
    probes = discover_plugins("probes", BaseProbe)
    logger.debug(f"Loaded probes: {probes}")
    managers = discover_plugins("managers", BaseManager)
    logger.debug(f"Loaded managers: {managers}")
    return {
        "managers": managers,
        "reporters": reporters,
        "scanners": scanners,
        "probes": probes,
    }
