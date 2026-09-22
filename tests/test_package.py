"""Smoke tests for the project package."""

from pathlib import Path

from bay_area_traffic_sim.toy_corridor import repository_root


def test_package_imports() -> None:
    import bay_area_traffic_sim

    assert bay_area_traffic_sim.__doc__


def test_repository_root_finds_the_project_from_a_nested_folder() -> None:
    root = repository_root(Path("src/bay_area_traffic_sim"))

    assert (root / "pyproject.toml").is_file()
    assert (root / "network").is_dir()
