from unittest import TestCase

from ezimon.core import logger
from ezimon.core.protocols import BaseBinaryProtocol, StringBinaryProtocol


class TestBaseBinaryProtocol(TestCase):
    def test_serialised_empty(self):
        p = BaseBinaryProtocol()
        self.assertIsNone(p.get_next_serialised())

    def test_serialised_one_value(self):
        p = BaseBinaryProtocol()
        p.submit_serialised(b'hello')
        self.assertEqual(p.get_next_serialised(), b'hello')
        self.assertIsNone(p.get_next_serialised())

    def test_deserialised_empty(self):
        p = BaseBinaryProtocol()
        self.assertIsNone(p.get_next_deserialised())

    def test_deserialised_one_value(self):
        p = BaseBinaryProtocol()
        p.submit_deserialised((1, 2, 3))
        self.assertEqual(p.get_next_deserialised(), (1, 2, 3))
        self.assertIsNone(p.get_next_deserialised())


class TestStringBinaryProtocol(TestCase):
    def test_serialise_hello(self):
        p = StringBinaryProtocol()
        p.process_values(('hello',))
        self.assertEqual(p.get_next_serialised(), b'hello')

    def test_deserialise_hello(self):
        p = StringBinaryProtocol()
        p.process_data(b'hello')
        self.assertEqual(p.get_next_deserialised(), ('hello',))

    def test_serialise_ss(self):
        p = StringBinaryProtocol()
        p.process_values(('ß',))
        self.assertEqual(p.get_next_serialised(), b'\xc3\x9f')

    def test_deserialise_ss(self):
        p = StringBinaryProtocol()
        p.process_data(b'\xc3\x9f')
        self.assertEqual(p.get_next_deserialised(), ('ß',))

    def test_serialise_invalid_ascii_character(self):
        p = StringBinaryProtocol(encoding='ascii')
        with self.assertLogs(logger, 'ERROR'):
            p.process_values(('ß',))
        self.assertIsNone(p.get_next_serialised())

    def test_serialise_invalid_ascii_character_with_replacement(self):
        p = StringBinaryProtocol(encoding='ascii', encode_errors='replace')
        p.process_values(('ß',))
        self.assertEqual(p.get_next_serialised(), b'?')

    def test_deserialise_invalid_utf8_code(self):
        p = StringBinaryProtocol()
        with self.assertLogs(logger, 'ERROR'):
            p.process_data(b'\x80')
        self.assertIsNone(p.get_next_deserialised())

    def test_deserialise_invalid_utf8_code_with_replacement(self):
        p = StringBinaryProtocol(decode_errors='replace')
        p.process_data(b'\x80')
        self.assertEqual(p.get_next_deserialised(),
                         ('\N{REPLACEMENT CHARACTER}',))
