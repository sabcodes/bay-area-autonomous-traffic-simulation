from bay_area_traffic_sim.network_audit import _match_station_to_network, _unique_stations
from bay_area_traffic_sim.pems_metadata import MetadataStation


class _Edge:
    def __init__(self, edge_id: str, name: str, lanes: int) -> None:
        self.edge_id = edge_id
        self.name = name
        self.lanes = lanes

    def getID(self) -> str:
        return self.edge_id

    def getName(self) -> str:
        return self.name

    def getLaneNumber(self) -> int:
        return self.lanes


class _Network:
    def convertLonLat2XY(self, longitude: float, latitude: float) -> tuple[float, float]:
        return longitude, latitude

    def getNeighboringEdges(self, x: float, y: float, radius: int) -> list[tuple[_Edge, float]]:
        assert radius == 250
        return [
            (_Edge(":internal", "", 1), 1.0),
            (_Edge("mainline", "US 101", 4), 20.0),
            (_Edge("ramp", "Ramp", 1), 30.0),
        ]


def test_station_network_match_ignores_internal_edges() -> None:
    station = MetadataStation(
        station_id=400001,
        freeway=101,
        direction="N",
        district=4,
        latitude=37.4,
        longitude=-122.0,
        lane_type="ML",
        lanes=4,
        name="Test station",
        source_file="metadata.txt",
    )

    match = _match_station_to_network(station, _Network())

    assert match.nearest_edge_id == "mainline"
    assert match.nearest_edge_name == "US 101"
    assert match.nearest_edge_lanes == 4
    assert match.distance_meters == 20


def test_unique_stations_removes_duplicate_metadata_snapshots() -> None:
    station = MetadataStation(
        station_id=400001,
        freeway=101,
        direction="N",
        district=4,
        latitude=37.4,
        longitude=-122.0,
        lane_type="ML",
        lanes=4,
        name="Test station",
        source_file="first-metadata.txt",
    )
    duplicate = MetadataStation(
        **{**station.__dict__, "source_file": "second-metadata.txt"}
    )

    unique = _unique_stations([station, duplicate])

    assert unique == [station]
