import json
from pathlib import Path

from bay_area_traffic_sim.osm_import import OVERPASS_ENDPOINTS, load_corridor_config, road_query


def test_load_corridor_config_uses_the_saved_osm_source_path() -> None:
    config = load_corridor_config(Path("configs/us101_corridor.json"))

    assert config.name == "US-101 northbound: SR-237 to Page Mill Road"
    assert config.osm_source_path.name == "us101_corridor.osm.xml"


def test_corridor_config_preserves_a_bounding_box() -> None:
    raw = json.loads(Path("configs/us101_corridor.json").read_text())

    assert raw["bounding_box"] == {"north": 37.45, "south": 37.36, "west": -122.1, "east": -122.0}


def test_road_query_uses_the_configured_bounds_and_only_road_types() -> None:
    query = road_query({"north": 2.0, "south": 1.0, "west": 3.0, "east": 4.0})

    assert "(1.0,3.0,2.0,4.0)" in query
    assert 'way["highway"' in query


def test_downloader_has_a_fallback_endpoint() -> None:
    assert len(OVERPASS_ENDPOINTS) >= 2
