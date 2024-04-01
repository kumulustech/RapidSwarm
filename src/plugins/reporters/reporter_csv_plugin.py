import csv
from datetime import datetime
from typing import List, Union

from pydantic import BaseModel

from rapidswarm.models.reporters import BaseReporter

__module_name__ = "reporter_csv_plugin"


class CSVReporter(BaseReporter):
    output_file: str = "report.csv"

    class Config:
        arbitrary_types_allowed = True

    def report(self, data: Union[BaseModel, List[BaseModel]]):
        if issubclass(type(data), BaseModel):
            data_list = [data]
        elif isinstance(data, list) and all(
            issubclass(type(item), BaseModel) for item in data
        ):
            data_list = data
        else:
            raise ValueError(
                "Unsupported data format. Expected a Pydantic model or a list of Pydantic models."
            )

        fieldnames = ["timestamp"] + list(data_list[0].__fields__.keys())

        try:
            with open(self.output_file, "w", newline="") as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()

                for item in data_list:
                    row = {"timestamp": datetime.now().isoformat()}
                    row.update(item.dict())
                    writer.writerow(row)
        except IOError as e:
            raise IOError(f"Error writing CSV report: {e}")
