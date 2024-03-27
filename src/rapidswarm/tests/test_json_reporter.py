import json
import os
from datetime import datetime

import pytest
from pydantic import BaseModel

from rapidswarm.models.json_reporter import JSONReporter


class DummyData(BaseModel):
    name: str
    value: int


def test_json_reporter(tmpdir):
    # Create a temporary directory for the test
    output_file = str(tmpdir.join("test_report.json"))

    # Create an instance of JSONReporter with the temporary output file
    reporter = JSONReporter(output_file=output_file)

    # Create some dummy data to report
    data = DummyData(name="test", value=42)

    # Call the report method with the dummy data
    reporter.report(data)

    # Assert that the output file exists
    assert os.path.exists(output_file)

    # Read the contents of the output file
    with open(output_file, "r") as file:
        report = json.load(file)

    # Assert the structure and contents of the report
    assert "timestamp" in report
    assert "data" in report
    assert report["data"]["name"] == "test"
    assert report["data"]["value"] == 42

    # Assert that the timestamp is in ISO format
    assert datetime.fromisoformat(report["timestamp"])


def test_json_reporter_io_error(tmpdir):
    # Create a directory instead of a file to simulate an IO error
    output_dir = str(tmpdir.mkdir("test_dir"))

    # Create an instance of JSONReporter with the directory as the output file
    reporter = JSONReporter(output_file=output_dir)

    # Create some dummy data to report
    data = DummyData(name="test", value=42)

    # Assert that an IOError is raised when attempting to write to a directory
    with pytest.raises(IOError):
        reporter.report(data)
