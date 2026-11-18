import unittest

from verify_rate_bins import certified_bin, nonstationary_polynomial, roots_inside_radius


class RateCertificateTests(unittest.TestCase):
    def test_strict_boundary_for_complex_conjugate_roots(self):
        # z * (z² + 4) has maximum root modulus exactly 2.
        coeffs = [1, 0, 4, 0]
        self.assertFalse(roots_inside_radius(coeffs, 1999, 1000))
        self.assertFalse(roots_inside_radius(coeffs, 2, 1))
        self.assertTrue(roots_inside_radius(coeffs, 2001, 1000))

    def test_exact_rate_on_a_bin_boundary_with_inaccurate_guess(self):
        # The four-bit field inverse has nonstationary spectral radius 3/8.
        inverse = (0, 1, 9, 14, 13, 11, 7, 6, 15, 2, 12, 5, 10, 4, 3, 8)
        coeffs = nonstationary_polynomial(inverse)
        self.assertEqual(certified_bin(coeffs, guess=373, scale=1000), 375)
