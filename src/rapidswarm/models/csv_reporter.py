import csv
from datetime import datetime

from pydantic import BaseModel

from .reporters import BaseReporter


class CSVReporter(BaseReporter):
    output_file: str = "report.csv"

    class Config:
        arbitrary_types_allowed = True

    def report(self, data: BaseModel):
        fieldnames = ["timestamp"] + list(data.__fields__.keys())

        try:
            with open(self.output_file, "w", newline="") as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()

                row = {"timestamp": datetime.now().isoformat()}
                row.update(data.dict())

                writer.writerow(row)
        except IOError as e:
            raise IOError(f"Error writing CSV report: {e}")
