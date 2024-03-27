import json
from datetime import datetime

from pydantic import BaseModel

from .reporters import BaseReporter


class JSONReporter(BaseReporter):
    output_file: str = "report.json"

    class Config:
        arbitrary_types_allowed = True

    def report(self, data: BaseModel):
        report = {
            "timestamp": datetime.now().isoformat(),
            "data": data.dict(),
        }

        try:
            with open(self.output_file, "w") as file:
                json.dump(report, file, indent=2)
        except IOError as e:
            raise IOError(f"Error writing JSON report: {e}")
