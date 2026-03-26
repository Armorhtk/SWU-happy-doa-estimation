"""Generate an introductory ULA scan figure for the DOA course."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import matplotlib.pyplot as plt
import numpy as np

from src.doa_intro import array_response, wavelength


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the first DOA introduction experiment.")
    parser.add_argument("--angle", type=float, default=20.0, help="True source angle in degrees.")
    parser.add_argument("--num-sensors", type=int, default=8, help="Number of ULA sensors.")
    parser.add_argument(
        "--carrier-hz",
        type=float,
        default=1.0e9,
        help="Carrier frequency used to compute the wavelength.",
    )
    parser.add_argument(
        "--spacing-scale",
        type=float,
        default=0.5,
        help="Sensor spacing as a multiple of wavelength, e.g. 0.5 means lambda/2.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("artifacts/doa_intro_array_scan.png"),
        help="Path for the generated figure.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    lam = wavelength(args.carrier_hz)
    spacing = args.spacing_scale * lam
    scan_angles = np.linspace(-90.0, 90.0, 721)
    response = array_response(
        scan_angles_deg=scan_angles,
        source_angle_deg=args.angle,
        num_sensors=args.num_sensors,
        spacing_m=spacing,
        carrier_hz=args.carrier_hz,
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(9, 4.5))
    plt.plot(scan_angles, response, linewidth=2, color="#0f766e")
    plt.axvline(args.angle, color="#dc2626", linestyle="--", label=f"True angle = {args.angle:.1f}°")
    plt.title("Introductory ULA Spatial Response")
    plt.xlabel("Scan angle (degrees)")
    plt.ylabel("Normalized response")
    plt.ylim(0, 1.05)
    plt.grid(alpha=0.25)
    plt.legend()
    plt.tight_layout()
    plt.savefig(args.output, dpi=180)
    print(f"Saved figure to: {args.output.resolve()}")
    print("Try changing --angle, --num-sensors, or --spacing-scale and compare the curves.")


if __name__ == "__main__":
    main()