from pydantic import BaseModel


class BaseReporter(BaseModel):
    def report(self, data):
        raise NotImplementedError("Subclasses must implement the 'report' method.")
