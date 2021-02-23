from ezimon.core.protocols.base import BaseProtocol


class BaseBinaryProtocol(BaseProtocol):
    """A base protocol which (de)serialises an object to/from bytes."""

    def serialise(self, obj) -> bytes:
        """Serialise the given object into a byte string."""

        raise NotImplementedError

    def deserialise(self, data: bytes):
        """Deserialise the given byte string to an object."""

        raise NotImplementedError


class StringBinaryProtocol(BaseBinaryProtocol):
    """Protocol which encodes Python strings to byte strings during
    serialisation and decodes during deserialisation.

    :param encoding: encoding to use when (de)serialising. See
        https://docs.python.org/3/library/codecs.html#standard-encodings for
        available encodings. Defaults to 'utf-8'
    :param encode_errors: error action to perform on encoding. See
        https://docs.python.org/3/library/codecs.html#error-handlers for
        available error actions. Defaults to 'strict'
    :param decode_errors: error action to perform on decoding. See
        https://docs.python.org/3/library/codecs.html#error-handlers for
        available error actions. Defaults to 'strict'
    """

    def __init__(self, encoding: str = 'utf-8', encode_errors: str = 'strict',
                 decode_errors: str = 'strict'):

        self.encoding = encoding
        self.encode_errors = encode_errors
        self.decode_errors = decode_errors

    def serialise(self, obj: str) -> bytes:
        """Serialise the given Python string to a byte string.

        :param obj: string to serialise
        """

        return obj.encode(encoding=self.encoding, errors=self.encode_errors)

    def deserialise(self, data: bytes) -> str:
        """Deserialise the given byte string to a Python string.

        :param data: data to deserialise
        """

        return data.decode(encoding=self.encoding, errors=self.decode_errors)
