import pytest

from bay_area_traffic_sim.flow_balance import (
    OrderedFlowStation,
    compare_adjacent_stations,
)


def _station(
    station_id: int,
    distance: float,
    lanes: int,
    flows: dict[str, float],
    cautions: list[str] | None = None,
    confirmed: bool = False,
    reported_lanes: int | None = None,
) -> OrderedFlowStation:
    return OrderedFlowStation(
        station_id=station_id,
        station_name=f"Station {station_id}",
        edge_id=f"edge_{station_id}",
        route_distance_meters=distance,
        represented_lanes=lanes,
        reported_lanes=reported_lanes or lanes,
        mean_flow_vehicles_per_hour=sum(flows.values()) / len(flows),
        flow_by_time=flows,
        cautions=cautions or [],
        full_cross_section_confirmed=confirmed,
    )


def test_adjacent_flow_balance_reports_net_inflow() -> None:
    stations = [
        _station(1, 0.0, 4, {"07:00": 4000, "07:05": 4200}),
        _station(2, 1000.0, 4, {"07:00": 4300, "07:05": 4600}),
    ]

    segment = compare_adjacent_stations(stations)[0]

    assert segment["mean_net_flow_change_vehicles_per_hour"] == 350
    assert segment["interpretation"] == "net_inflow"
    assert segment["usable_for_missing_ramp_estimation"] is True


def test_adjacent_flow_balance_flags_lane_coverage_change() -> None:
    stations = [
        _station(1, 0.0, 4, {"07:00": 4000}),
        _station(2, 1000.0, 5, {"07:00": 5000}),
    ]

    segment = compare_adjacent_stations(stations)[0]

    assert segment["usable_for_missing_ramp_estimation"] is False
    assert "lane count changes" in segment["cautions"][0]


def test_adjacent_flow_balance_accepts_audited_full_cross_sections() -> None:
    stations = [
        _station(1, 0.0, 4, {"07:00": 4000}, confirmed=True),
        _station(2, 1000.0, 6, {"07:00": 5000}, confirmed=True),
    ]

    segment = compare_adjacent_stations(stations)[0]

    assert segment["usable_for_missing_ramp_estimation"] is True


def test_adjacent_flow_balance_preserves_detector_mapping_mismatch() -> None:
    stations = [
        _station(1, 0.0, 4, {"07:00": 4000}, confirmed=True),
        _station(
            2,
            1000.0,
            4,
            {"07:00": 5000},
            ["PeMS reports 5 lanes but SUMO maps 4."],
            confirmed=True,
            reported_lanes=5,
        ),
    ]

    segment = compare_adjacent_stations(stations)[0]

    assert segment["usable_for_missing_ramp_estimation"] is False


def test_adjacent_flow_balance_preserves_station_cautions() -> None:
    stations = [
        _station(1, 0.0, 4, {"07:00": 4000}),
        _station(2, 1000.0, 4, {"07:00": 5000}, ["Collector road context."]),
    ]

    segment = compare_adjacent_stations(stations)[0]

    assert segment["usable_for_missing_ramp_estimation"] is False
    assert segment["cautions"] == ["Collector road context."]
    assert segment["mean_net_flow_change_vehicles_per_hour"] == pytest.approx(1000)
