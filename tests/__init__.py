import unittest
import numpy as np
from value_encoder import ValueEncoder


class ValueEncoderTestCases(unittest.TestCase):
    def test_basic(self):
        encoder = ValueEncoder()
        encoder.fit('abced')
        self.assertEqual(encoder.classes_, 'abcde')

        encoded = encoder.transform('aabec')
        self.assertEqual(encoded.dtype, np.uint8)
        np.testing.assert_array_equal(encoded, [0, 0, 1, 4, 2])

        decoded = encoder.inverse_transform(encoded)
        self.assertEqual(decoded, 'aabec')

    def test_fit_transform(self):
        encoder = ValueEncoder()
        encoded = encoder.fit_transform('ced')
        np.testing.assert_array_equal(encoded, [0, 2, 1])

    def test_error(self):
        encoder = ValueEncoder()
        encoder.fit('abcde')
        with self.assertRaisesRegexp(ValueError, 'invalid character: "abcf"'):
            encoder.transform('abcf')
        with self.assertRaisesRegexp(ValueError, 'invalid character: "abc\t"'):
            encoder.transform('abc\t')

        with self.assertRaisesRegexp(ValueError, 'invalid character: 5'):
            encoder.inverse_transform([0, 0, 5])

    def test_fit_duplicates(self):
        encoder = ValueEncoder()
        encoder.fit('abceda')
        self.assertEqual(encoder.classes_, 'abcde')
        encoded = encoder.transform('aabec')
        np.testing.assert_array_equal(encoded, [0, 0, 1, 4, 2])
