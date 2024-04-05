import csv
import os
from datetime import datetime

import pytest
from plugins.reporters.reporter_csv_plugin import CSVReporter
from pydantic import BaseModel


class DummyData(BaseModel):
    name: str
    value: int


def test_csv_reporter(tmpdir):
    # Create a temporary directory for the test
    output_file = str(tmpdir.join("test_report.csv"))

    # Create an instance of CSVReporter with the temporary output file
    reporter = CSVReporter(output_file=output_file)

    # Create some dummy data to report
    data = DummyData(name="test", value=42)

    # Call the report method with the dummy data
    reporter.report(data)

    # Assert that the output file exists
    assert os.path.exists(output_file)

    # Read the contents of the output file
    with open(output_file, "r") as file:
        reader = csv.DictReader(file)
        rows = list(reader)

    # Assert the number of rows in the CSV file
    assert len(rows) == 1

    # Assert the fieldnames in the CSV file
    assert reader.fieldnames == ["timestamp", "name", "value"]

    # Assert the values in the CSV row
    assert rows[0]["name"] == "test"
    assert rows[0]["value"] == "42"

    # Assert that the timestamp is in ISO format
    assert datetime.fromisoformat(rows[0]["timestamp"])


def test_csv_reporter_io_error(tmpdir):
    # Create a directory instead of a file to simulate an IO error
    output_dir = str(tmpdir.mkdir("test_dir"))

    # Create an instance of CSVReporter with the directory as the output file
    reporter = CSVReporter(output_file=output_dir)

    # Create some dummy data to report
    data = DummyData(name="test", value=42)

    # Assert that an IOError is raised when attempting to write to a directory
    with pytest.raises(IOError):
        reporter.report(data)
