from pydantic import BaseModel


class BaseScanner(BaseModel):
    def scan(self):
        raise NotImplementedError("Subclasses must implement the 'scan' method.")

    def validate(self):
        raise NotImplementedError("Subclasses must implement the 'validate' method.")
