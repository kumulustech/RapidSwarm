from typing import Any, Dict, List, Optional

from loguru import logger
from pydantic import BaseModel

from .probes import BaseProbe


class BaseManager(BaseModel):
    config: Optional[Dict[str, Any]] = None

    def run(self):
        raise NotImplementedError("Subclasses must implement the 'run' method.")


class SequentialManager(BaseManager):
    """
    Manages the execution of probes in a sequential manner. There is nothing
    special or amazing about this manager. It doesn't run anything in parallel
    or do anything fancy. It just runs the probes one after the other.

    This manager takes a list of probes and runs them one after the other,
    logging the start and end of each probe's execution, along with any results
    or errors encountered. The probes are expected to be instances of classes
    that inherit from BaseProbe and implement the run method.

    Attributes:
        probes (List[BaseProbe]): A list of probe instances to be managed.
    """

    probes: List[BaseProbe]

    def run(self):
        results = []
        for probe in self.probes:
            logger.info(f"Running probe: {type(probe).__name__}")
            try:
                probe_results = probe.run()
                logger.info(f"Results: {probe_results}")
                results.append(probe_results)
            except Exception as e:
                logger.error(f"Error running probe {type(probe).__name__}: {e}")
        return results

    probes: List[BaseProbe]
