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
    notes: list[str] | None = None,
    daily_flows: dict[tuple[str, str], float] | None = None,
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
        notes=notes or [],
        flow_by_date_time=daily_flows
        if daily_flows is not None
        else {("2025-10-01", time): flow for time, flow in flows.items()},
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


def test_audited_pems_cross_section_remains_usable_with_model_lane_gap() -> None:
    stations = [
        _station(1, 0.0, 4, {"07:00": 4000}, confirmed=True),
        _station(
            2,
            1000.0,
            4,
            {"07:00": 5000},
            confirmed=True,
            reported_lanes=5,
            notes=[
                "PeMS reports 5 lanes while the mapped SUMO edge represents 4; "
                "this is a simulation-geometry mismatch."
            ],
        ),
    ]

    segment = compare_adjacent_stations(stations)[0]

    assert segment["usable_for_missing_ramp_estimation"] is True
    assert segment["cautions"] == []
    assert any("simulation-geometry mismatch" in note for note in segment["notes"])


def test_adjacent_flow_balance_treats_same_edge_difference_as_detector_bias() -> None:
    upstream = _station(1, 0.0, 4, {"07:00": 4000}, confirmed=True)
    downstream = OrderedFlowStation(
        station_id=2,
        station_name="Station 2",
        edge_id=upstream.edge_id,
        route_distance_meters=100.0,
        represented_lanes=4,
        reported_lanes=4,
        mean_flow_vehicles_per_hour=3800,
        flow_by_time={"07:00": 3800},
        cautions=[],
        full_cross_section_confirmed=True,
    )

    segment = compare_adjacent_stations([upstream, downstream])[0]

    assert segment["topology_class"] == "same_edge_consistency_check"
    assert segment["usable_for_missing_ramp_estimation"] is False
    assert segment["time_profile"] == [{"time": "07:00", "net_flow_change_vehicles_per_hour": -200}]


def test_adjacent_flow_balance_preserves_station_cautions() -> None:
    stations = [
        _station(1, 0.0, 4, {"07:00": 4000}),
        _station(2, 1000.0, 4, {"07:00": 5000}, ["Collector road context."]),
    ]

    segment = compare_adjacent_stations(stations)[0]

    assert segment["usable_for_missing_ramp_estimation"] is False
    assert segment["cautions"] == ["Collector road context."]
    assert segment["mean_net_flow_change_vehicles_per_hour"] == pytest.approx(1000)


def test_pair_audit_can_block_residual_without_losing_observed_net_change() -> None:
    stations = [
        _station(401534, 0.0, 4, {"07:00": 4756}, confirmed=True),
        _station(401948, 1000.0, 5, {"07:00": 5086}, confirmed=True),
    ]

    segment = compare_adjacent_stations(
        stations,
        blocked_pairs={
            (401534, 401948): "Intervening ramp and detector mappings remain unresolved."
        },
    )[0]

    assert segment["mean_net_flow_change_vehicles_per_hour"] == 330
    assert segment["usable_for_missing_ramp_estimation"] is False
    assert segment["cautions"] == [
        "Intervening ramp and detector mappings remain unresolved."
    ]


def test_adjacent_flow_balance_matches_only_shared_observation_dates() -> None:
    upstream = _station(
        1,
        0.0,
        4,
        {"07:00": 5000},
        daily_flows={
            ("2025-10-01", "07:00"): 4000,
            ("2025-10-02", "07:00"): 6000,
        },
    )
    downstream = _station(
        2,
        1000.0,
        4,
        {"07:00": 3750},
        daily_flows={
            ("2025-10-02", "07:00"): 6500,
            ("2025-10-03", "07:00"): 1000,
        },
    )

    segment = compare_adjacent_stations([upstream, downstream])[0]

    assert segment["mean_net_flow_change_vehicles_per_hour"] == 500
    assert segment["matched_days"] == 1
    assert segment["matched_intervals"] == 1
    assert segment["time_profile"] == [
        {
            "time": "07:00",
            "observations": 1,
            "net_flow_change_vehicles_per_hour": 500,
        }
    ]
