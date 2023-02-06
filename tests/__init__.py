import unittest

import numpy as np

from value_encoder import ValueEncoder


class ValueEncoderTestCases(unittest.TestCase):
    def test_basic(self):
        encoder = ValueEncoder().fit("abced")
        self.assertEqual(encoder.classes_, list(map(ord, "abcde")))

        encoded = encoder.transform("aabec")
        self.assertEqual(encoded.dtype, np.int16)
        np.testing.assert_array_equal(encoded, [0, 0, 1, 4, 2])

        decoded = encoder.inverse_transform(encoded)
        self.assertEqual(decoded, "aabec")

    def test_transform_multiple(self):
        encoder = ValueEncoder().fit("abced")
        strings = ["aabec", "abcd", "ad"]
        encoded = encoder.transform(strings)
        np.testing.assert_array_equal(encoded, [[0, 0, 1, 4, 2], [0, 1, 2, 3, -1], [0, 3, -1, -1, -1]])
        self.assertEqual(encoder.classes_, list(map(ord, "abcde")))

    def test_fit_from_iterable(self):
        encoder = ValueEncoder()
        strings = ["aabec", "abcd", "ad"]
        encoder.fit(value for value in strings)
        encoded = encoder.transform(strings)
        np.testing.assert_array_equal(encoded, [[0, 0, 1, 4, 2], [0, 1, 2, 3, -1], [0, 3, -1, -1, -1]])
        self.assertEqual(encoder.classes_, list(map(ord, "abcde")))

    def test_fit_from_iterable_invalid_types(self):
        encoder = ValueEncoder()
        values = ["aabec", 123]
        with self.assertRaises(ValueError):
            encoder.fit(values)  # type: ignore

    def test_cap(self):
        encoder = ValueEncoder().fit("abced")
        encoded = encoder.transform("aabec", cap=True)
        np.testing.assert_array_equal(encoded, [0, 0, 1, 4, 2, 5])

    def test_transform_multiple_cap(self):
        encoder = ValueEncoder().fit("abced")
        strings = ["aabec", "abcd", "ad"]
        encoded = encoder.transform(strings, cap=True)
        np.testing.assert_array_equal(encoded, [[0, 0, 1, 4, 2, 5], [0, 1, 2, 3, 5, -1], [0, 3, 5, -1, -1, -1]])

    def test_transform_multiple_different_padding_value(self):
        encoder = ValueEncoder().fit("abced")
        strings = ["aabec", "abcd", "ad"]
        encoded = encoder.transform(strings, padding_value=100)
        np.testing.assert_array_equal(encoded, [[0, 0, 1, 4, 2], [0, 1, 2, 3, 100], [0, 3, 100, 100, 100]])

    def test_error(self):
        """transform and inverse_transform should raise exceptions when encountering invalid input"""
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
        self.assertEqual(encoder.classes_, list(map(ord, "abcde")))
        encoded = encoder.transform("aabec")
        np.testing.assert_array_equal(encoded, [0, 0, 1, 4, 2])

    def test_utf8(self):
        encoder = ValueEncoder()
        value = "一二三".encode("utf-8")
        encoder.fit(value)
        self.assertEqual(encoder.classes_, sorted(set(value)))

    def test_utf8_batch(self):
        encoder = ValueEncoder()
        values = ["一二三".encode("utf-8"), "四五六".encode("utf-8")]
        encoder.fit(values)
        self.assertEqual(encoder.classes_, sorted(set(values[0]) | set(values[1])))

    def test_utf8_complex(self):
        value = "c'est en apprenant par livres hebdo que les émissions dans quelle étagère ? sur france 2 et livres et vous sur public sénat vont disparaître, que j'ai décidé de lancer cette pétition. comme émission littéraire conséquente, il ne reste plus semble-t-il que la grande librairie sur france 5. quant à un livre, un jour, elle n'est programmée et diffusée depuis le début que quelques minutes par jour sur france 3 . il reste pour les écrivains la tribune d'onpc. non non non ! l'émission on n'est pas couché sur france 2 n'est pas une émission littéraire mais un talk-show de divertissement !\nil faut absolument mettre une émission littéraire d'au moins 60 minutes ou 90 minutes sur france 2 ou france 3 et sur public sénat. il en va du sérieux du service public. la culture ne se brade pas au prix d'un soi-disant rajeunissement des grilles des chaînes tv et d'une volonté libérale d'être à tout prix bankable !\neric dubois\necrivain, poète, passeur, responsable de l'association et blog littéraire le capital des mots.\non peut retrouver le texte de la pétition sur mon blog in mediapart : link\nl'article dans livres hebdo : link\nphoto : on n'est pas couché © capture france 2".encode(  # noqa
            "utf-8"
        )
        encoder = ValueEncoder()
        encoder.fit(value)
        out = encoder.transform(value)
        assert out.max() < 256
