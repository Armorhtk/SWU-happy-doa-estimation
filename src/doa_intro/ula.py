"""Small ULA helpers used by the introductory DOA examples."""

from __future__ import annotations

import numpy as np


def wavelength(carrier_hz: float, propagation_speed: float = 3.0e8) -> float:
    """Return the wavelength in meters."""
    if carrier_hz <= 0:
        raise ValueError("carrier_hz must be positive")
    return propagation_speed / carrier_hz


def ula_positions(num_sensors: int, spacing_m: float) -> np.ndarray:
    """Return x-axis sensor positions for a uniform linear array."""
    if num_sensors < 2:
        raise ValueError("num_sensors must be at least 2")
    if spacing_m <= 0:
        raise ValueError("spacing_m must be positive")
    return np.arange(num_sensors, dtype=float) * spacing_m


def steering_vector(
    angle_deg: float,
    num_sensors: int,
    spacing_m: float,
    carrier_hz: float,
    propagation_speed: float = 3.0e8,
) -> np.ndarray:
    """Return the ULA steering vector for a plane wave from angle_deg."""
    lam = wavelength(carrier_hz, propagation_speed)
    sensor_positions = ula_positions(num_sensors, spacing_m)
    angle_rad = np.deg2rad(angle_deg)
    phase = -2j * np.pi * sensor_positions * np.sin(angle_rad) / lam
    return np.exp(phase)


def array_response(
    scan_angles_deg: np.ndarray,
    source_angle_deg: float,
    num_sensors: int,
    spacing_m: float,
    carrier_hz: float,
    propagation_speed: float = 3.0e8,
) -> np.ndarray:
    """Return normalized beam response magnitude over scan angles."""
    source_sv = steering_vector(
        source_angle_deg,
        num_sensors=num_sensors,
        spacing_m=spacing_m,
        carrier_hz=carrier_hz,
        propagation_speed=propagation_speed,
    )
    response = []
    for angle in scan_angles_deg:
        scan_sv = steering_vector(
            angle,
            num_sensors=num_sensors,
            spacing_m=spacing_m,
            carrier_hz=carrier_hz,
            propagation_speed=propagation_speed,
        )
        value = np.abs(np.vdot(scan_sv, source_sv)) / num_sensors
        response.append(value)
    return np.asarray(response, dtype=float)
