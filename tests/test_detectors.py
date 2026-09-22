from pathlib import Path
from xml.etree import ElementTree

import pytest

from bay_area_traffic_sim.detectors import (
    VirtualDetectorSpec,
    summarize_virtual_detector_output,
    write_virtual_detector_file,
)


def test_virtual_detector_file_writes_one_loop_per_lane(tmp_path: Path) -> None:
    destination = tmp_path / "detectors.add.xml"
    output = tmp_path / "detectors.out.xml"
    spec = VirtualDetectorSpec(400001, "Test", "edge", ["edge_1", "edge_2"], 50.0)

    write_virtual_detector_file(destination, output, [spec])

    loops = ElementTree.parse(destination).getroot().findall("inductionLoop")
    assert [loop.attrib["id"] for loop in loops] == [
        "pems_400001_lane_0",
        "pems_400001_lane_1",
    ]
    assert all(loop.attrib["period"] == "300" for loop in loops)
    assert all(loop.attrib["file"] == str(output) for loop in loops)


def test_detector_summary_aggregates_lanes_with_vehicle_weighted_speed(
    tmp_path: Path,
) -> None:
    output = tmp_path / "detectors.out.xml"
    output.write_text(
        """<?xml version="1.0"?>
<detector>
    <interval begin="900" end="1200" id="pems_400001_lane_0"
              nVehContrib="10" flow="120" occupancy="5" speed="20"/>
    <interval begin="900" end="1200" id="pems_400001_lane_1"
              nVehContrib="30" flow="360" occupancy="7" speed="30"/>
</detector>
"""
    )

    summary = summarize_virtual_detector_output(output)

    assert len(summary) == 1
    assert summary[0].station_id == 400001
    assert summary[0].contributing_vehicles == 40
    assert summary[0].flow_vehicles_per_hour == 480
    assert summary[0].speed_mph == pytest.approx(27.5 * 2.2369362921)
    assert summary[0].mean_lane_occupancy_percent == 6
