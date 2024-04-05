from typing import Any, Dict, Optional

from pydantic import BaseModel


class BaseManager(BaseModel):
    config: Optional[Dict[str, Any]] = None

    def run(self):
        raise NotImplementedError("Subclasses must implement the 'run' method.")
