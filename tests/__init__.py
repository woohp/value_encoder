import unittest

import numpy as np

from value_encoder import ValueEncoder


class ValueEncoderTestCases(unittest.TestCase):
    def test_basic(self):
        encoder = ValueEncoder().fit("abced")
        self.assertEqual(encoder.classes_, "abcde")

        encoded = encoder.transform("aabec")
        self.assertEqual(encoded.dtype, np.int16)
        np.testing.assert_array_equal(encoded, [0, 0, 1, 4, 2])

        decoded = encoder.inverse_transform(encoded)
        self.assertEqual(decoded, "aabec")

    def test_batch(self):
        encoder = ValueEncoder().fit("abced")
        strings = ["aabec", "abcd", "ad"]
        encoded = encoder.transform(strings)
        np.testing.assert_array_equal(encoded, [[0, 0, 1, 4, 2], [0, 1, 2, 3, -1], [0, 3, -1, -1, -1]])

    def test_cap(self):
        encoder = ValueEncoder().fit("abced")
        encoded = encoder.transform("aabec", cap=True)
        np.testing.assert_array_equal(encoded, [0, 0, 1, 4, 2, 5])

    def test_batch_cap(self):
        encoder = ValueEncoder().fit("abced")
        strings = ["aabec", "abcd", "ad"]
        encoded = encoder.transform(strings, cap=True)
        np.testing.assert_array_equal(encoded, [[0, 0, 1, 4, 2, 5], [0, 1, 2, 3, 5, -1], [0, 3, 5, -1, -1, -1]])

    def test_batch_different_missing_value(self):
        encoder = ValueEncoder().fit("abced")
        strings = ["aabec", "abcd", "ad"]
        encoded = encoder.transform(strings, missing_value=100)
        np.testing.assert_array_equal(encoded, [[0, 0, 1, 4, 2], [0, 1, 2, 3, 100], [0, 3, 100, 100, 100]])

    def test_error(self):
        encoder = ValueEncoder()
        encoder.fit("abcde")
        with self.assertRaisesRegex(ValueError, 'invalid character: "abcf"'):
            encoder.transform("abcf")
        with self.assertRaisesRegex(ValueError, 'invalid character: "abc\t"'):
            encoder.transform("abc\t")

        with self.assertRaisesRegex(ValueError, "invalid character: 5"):
            encoder.inverse_transform(np.array([0, 0, 5]))

    def test_fit_duplicates(self):
        encoder = ValueEncoder()
        encoder.fit("abceda")
        self.assertEqual(encoder.classes_, "abcde")
        encoded = encoder.transform("aabec")
        np.testing.assert_array_equal(encoded, [0, 0, 1, 4, 2])
