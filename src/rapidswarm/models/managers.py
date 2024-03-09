from pydantic import BaseModel


class BaseManager(BaseModel):
    def run(self):
        raise NotImplementedError("Subclasses must implement the 'run' method.")
