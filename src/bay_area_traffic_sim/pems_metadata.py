"""Select PeMS detector stations that belong to the US-101 study corridor."""

from __future__ import annotations

import csv
from collections.abc import Iterable, Mapping
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class MetadataStation:
    """The location and road attributes needed to identify a detector station."""

    station_id: int
    freeway: int
    direction: str
    district: int
    latitude: float
    longitude: float
    lane_type: str
    lanes: int | None
    name: str
    source_file: str


@dataclass(frozen=True)
class StationSelection:
    """The detector records and unique IDs selected for one study corridor."""

    source_files: list[str]
    station_ids: list[int]
    stations: list[MetadataStation]

    def as_dict(self) -> dict[str, object]:
        """Return a JSON-ready, traceable representation of the selection."""

        return asdict(self)


def select_corridor_stations(
    source_files: Iterable[Path], bounding_box: Mapping[str, float]
) -> StationSelection:
    """Keep northbound US-101 mainline stations inside a configured map boundary."""

    files = list(source_files)
    if not files:
        raise ValueError("No Station Metadata files matched the requested input pattern.")

    stations = [
        station
        for source in files
        for station in _read_metadata_file(source)
        if _belongs_to_corridor(station, bounding_box)
    ]
    return StationSelection(
        source_files=[str(source) for source in files],
        station_ids=sorted({station.station_id for station in stations}),
        stations=stations,
    )


def _read_metadata_file(source: Path) -> list[MetadataStation]:
    with source.open(newline="") as raw_file:
        reader = csv.DictReader(raw_file)
        if reader.fieldnames is None:
            raise ValueError(f"Station Metadata file has no header: {source}")
        missing = {"ID", "Fwy", "Dir", "District", "Latitude", "Longitude", "Type"} - set(
            reader.fieldnames
        )
        if missing:
            raise ValueError(
                f"Station Metadata file is missing columns {sorted(missing)}: {source}"
            )
        return [_parse_metadata_row(row, source) for row in reader]


def _parse_metadata_row(row: dict[str, str | None], source: Path) -> MetadataStation:
    try:
        lanes = _int_or_none(row.get("Lanes"))
        return MetadataStation(
            station_id=int(_required(row, "ID")),
            freeway=int(float(_required(row, "Fwy"))),
            direction=_required(row, "Dir"),
            district=int(_required(row, "District")),
            latitude=float(_required(row, "Latitude")),
            longitude=float(_required(row, "Longitude")),
            lane_type=_required(row, "Type"),
            lanes=lanes,
            name=row.get("Name") or "",
            source_file=str(source),
        )
    except ValueError as error:
        raise ValueError(f"Could not parse a Station Metadata row in {source}.") from error


def _required(row: Mapping[str, str | None], field: str) -> str:
    value = row.get(field)
    if not value:
        raise ValueError(f"Missing {field}.")
    return value


def _int_or_none(value: str | None) -> int | None:
    return int(value) if value else None


def _belongs_to_corridor(station: MetadataStation, bounding_box: Mapping[str, float]) -> bool:
    return (
        station.freeway == 101
        and station.direction == "N"
        and station.district == 4
        and station.lane_type == "ML"
        and bounding_box["south"] <= station.latitude <= bounding_box["north"]
        and bounding_box["west"] <= station.longitude <= bounding_box["east"]
    )
