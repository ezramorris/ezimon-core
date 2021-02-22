from unittest import TestCase

from ezimon.core.protocols.binary import StringBinaryProtocol


class TestStringBinaryProtocol(TestCase):
    def test_serialise_hello(self):
        p = StringBinaryProtocol()
        self.assertEqual(p.serialise('hello'), b'hello')

    def test_deserialise_hello(self):
        p = StringBinaryProtocol()
        self.assertEqual(p.deserialise(b'hello'), 'hello')

    def test_serialise_ss(self):
        p = StringBinaryProtocol()
        self.assertEqual(p.serialise('ß'), b'\xc3\x9f')

    def test_deserialise_ss(self):
        p = StringBinaryProtocol()
        self.assertEqual(p.deserialise(b'\xc3\x9f'), 'ß')

    def test_serialise_invalid_ascii_character(self):
        p = StringBinaryProtocol(encoding='ascii')
        with self.assertRaises(UnicodeEncodeError):
            p.serialise('ß')

    def test_serialise_invalid_ascii_character_with_replacement(self):
        p = StringBinaryProtocol(encoding='ascii', errors='replace')
        self.assertEqual(p.serialise('ß'), b'?')

    def test_deserialise_invalid_utf8_code(self):
        p = StringBinaryProtocol()
        with self.assertRaises(UnicodeDecodeError):
            p.deserialise(b'\x80')

    def test_deserialise_invalid_utf8_code_with_replacement(self):
        p = StringBinaryProtocol(errors='replace')
        self.assertEqual(p.deserialise(b'\x80'), '\N{REPLACEMENT CHARACTER}')
