"""Smoke tests for the project package."""


def test_package_imports() -> None:
    import bay_area_traffic_sim

    assert bay_area_traffic_sim.__doc__
