import unittest

import numpy as np

from src.doa_intro.ula import array_response, steering_vector, ula_positions, wavelength


class UlaMathTests(unittest.TestCase):
    def test_wavelength_matches_basic_physics(self) -> None:
        self.assertAlmostEqual(wavelength(1.0e9), 0.3)

    def test_ula_positions_are_evenly_spaced(self) -> None:
        positions = ula_positions(num_sensors=4, spacing_m=0.5)
        np.testing.assert_allclose(positions, np.array([0.0, 0.5, 1.0, 1.5]))

    def test_steering_vector_has_unit_magnitude(self) -> None:
        vector = steering_vector(angle_deg=30.0, num_sensors=8, spacing_m=0.15, carrier_hz=1.0e9)
        np.testing.assert_allclose(np.abs(vector), np.ones(8))

    def test_array_response_peaks_near_source_angle(self) -> None:
        scan = np.linspace(-90.0, 90.0, 721)
        response = array_response(
            scan_angles_deg=scan,
            source_angle_deg=25.0,
            num_sensors=8,
            spacing_m=0.15,
            carrier_hz=1.0e9,
        )
        peak_angle = scan[int(np.argmax(response))]
        self.assertAlmostEqual(peak_angle, 25.0, places=1)


if __name__ == "__main__":
    unittest.main()
