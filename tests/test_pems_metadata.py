import csv
from pathlib import Path

from bay_area_traffic_sim.pems_metadata import load_station_ids, select_corridor_stations


def _write_metadata(source: Path) -> None:
    rows = [
        ["ID", "Fwy", "Dir", "District", "Latitude", "Longitude", "Type", "Lanes", "Name"],
        ["400001", "101", "N", "4", "37.40", "-122.05", "ML", "4", "US-101 NB"],
        ["400002", "101", "N", "4", "37.46", "-122.05", "ML", "4", "Outside north"],
        ["400003", "101", "S", "4", "37.40", "-122.05", "ML", "4", "Southbound"],
        ["400004", "101", "N", "4", "37.40", "-122.05", "OR", "1", "On-ramp"],
    ]
    with source.open("w", newline="") as destination:
        csv.writer(destination, delimiter="\t").writerows(rows)


def test_select_corridor_stations_uses_location_and_mainline_direction(tmp_path: Path) -> None:
    source = tmp_path / "d04_text_meta_2025_08_27.txt"
    _write_metadata(source)

    selection = select_corridor_stations(
        [source],
        {"south": 37.36, "north": 37.45, "west": -122.10, "east": -122.00},
    )

    assert selection.station_ids == [400001]
    assert selection.stations[0].name == "US-101 NB"
    assert selection.stations[0].lanes == 4


def test_select_corridor_stations_requires_a_metadata_file() -> None:
    try:
        select_corridor_stations([], {"south": 1, "north": 2, "west": 3, "east": 4})
    except ValueError as error:
        assert "No Station Metadata" in str(error)
    else:
        raise AssertionError("Expected a helpful error for empty metadata input.")


def test_load_station_ids_accepts_a_committed_selection_config(tmp_path: Path) -> None:
    selection = tmp_path / "station_ids.json"
    selection.write_text('{"station_ids": [400001, 400002]}')

    assert load_station_ids(selection) == {400001, 400002}
