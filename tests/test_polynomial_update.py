import unittest

from power_mixing import multiply
from research.spectral_certificate import certify, power15


class PolynomialUpdateTests(unittest.TestCase):
    def test_finite_bounds(self):
        for width, modulus, expected in [
            (16, (1 << 112) | 0x39, [33, 49, 97]),
            (12, (1 << 116) | 0x17, [23, 45, 89]),
        ]:
            result = certify(128, width, 4, modulus, [32, 64, 128], control="power15")
            self.assertEqual(list(result["sufficient_cipher_rounds"].values()), expected)
        with self.assertRaisesRegex(ValueError, "orders 2 through 4"):
            certify(128, 16, 5, (1 << 112) | 0x39, [128], control="power15")

    def test_nonpermuting_control_still_defines_a_permutation(self):
        # In GF(16) every nonzero 15th power is 1. The full six-bit round is invertible.
        modulus = 0x13
        control_values = [int(z != 0) for z in range(16)]
        self.assertEqual([power15(z, modulus) for z in range(16)], control_values)
        table = [((low ^ control_values[z]) << 4) | z for z in range(16) for low in range(4)]
        self.assertEqual(len(set(table)), 64)
        self.assertEqual(certify(6, 2, 4, modulus, [32], table, control="power15")["mismatches"], 0)
        table[0], table[1] = table[1], table[0]
        self.assertEqual(certify(6, 2, 4, modulus, [32], table, control="power15")["mismatches"], 2)

    def test_power_against_repeated_multiplication(self):
        for z in range(32):
            acc = 1
            for _ in range(15):
                acc = multiply(acc, z, 0x25)
            self.assertEqual(power15(z, 0x25), acc)

    def test_general_polynomial_in_compact_and_table_modes(self):
        # p(z) = 2*z^15 + 3*z^2 + 1. On GF(16), z^15 is the nonzero indicator.
        coefficients = [1, 0, 3] + [0] * 12 + [2]
        result = certify(128, 12, 4, (1 << 116) | 0x17, [128],
                         control="polynomial15", coefficients=coefficients)
        self.assertEqual(result["sufficient_cipher_rounds"], {"2^-128": 89})
        self.assertEqual(result["coefficients"], coefficients)
        values = [(2 if z else 0) ^ multiply(3, multiply(z, z, 0x13), 0x13) ^ 1 for z in range(16)]
        table = [((low ^ (values[z] & 3)) << 4) | z for z in range(16) for low in range(4)]
        for mismatches in (0, 2):
            result = certify(6, 2, 4, 0x13, [32], table, control="polynomial15", coefficients=coefficients)
            self.assertEqual(result["mismatches"], mismatches)
            if mismatches == 0:
                table[0], table[1] = table[1], table[0]

    def test_coefficient_validation(self):
        for coefficients, message in [(None, "exactly 16"), ([1] * 15, "exactly 16"),
                                      ([-1] + [1] * 15, "control-field integer"),
                                      ([0] * 15 + [16], "control-field integer"),
                                      ([1] * 15 + [0], "leading coefficient")]:
            with self.subTest(coefficients=coefficients), self.assertRaisesRegex(ValueError, message):
                certify(6, 2, 4, 0x13, [32], control="polynomial15", coefficients=coefficients)
        with self.assertRaisesRegex(ValueError, "only for the polynomial15"):
            certify(6, 2, 4, 0x13, [32], control="power15", coefficients=[1] * 16)
