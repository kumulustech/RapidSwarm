# tests/test_rapidswarm.py

import pytest
from rapidswarm.rapidswarm import RapidSwarm


def test_rapidswarm_placeholder():
    # Get a measure of coverage, however meagre.
    rs = RapidSwarm("nonesuch.yaml", verbose=True)
    assert rs.config_file == "nonesuch.yaml"
    assert rs.config is None
    assert rs.scanners == []
    assert rs.managers == []
    assert rs.reporters == []
    assert rs.scanned_nodes == []
    assert rs.verbose == True
