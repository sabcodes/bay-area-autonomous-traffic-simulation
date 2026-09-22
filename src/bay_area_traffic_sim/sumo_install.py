"""Locate SUMO installed inside the active Python environment."""

from __future__ import annotations

from pathlib import Path


def binary(name: str) -> Path:
    """Return a SUMO executable supplied by the ``eclipse-sumo`` package."""

    import sumo

    candidate = Path(sumo.SUMO_HOME) / "bin" / name
    if not candidate.is_file():
        raise RuntimeError(f"SUMO executable not found in the virtual environment: {candidate}")
    return candidate
