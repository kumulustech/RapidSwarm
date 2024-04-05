import json
from datetime import datetime

from pydantic import BaseModel, ConfigDict
from rapidswarm.models.reporters import BaseReporter

__module_name__ = "reporter_json_plugin"
__import_as__ = "JSONReporter"


class JSONReporter(BaseReporter):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    output_file: str = "report.json"

    def report(self, data: BaseModel):
        report = {
            "timestamp": datetime.now().isoformat(),
            "data": data.model_dump(),
        }

        try:
            with open(self.output_file, "w") as file:
                json.dump(report, file, indent=2)
        except IOError as e:
            raise IOError(f"Error writing JSON report: {e}")
