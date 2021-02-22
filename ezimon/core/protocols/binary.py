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
    """Protocol which converts from Python strings to byte strings and vice
    versa."""

    def __init__(self, **kwargs):
        """All keyword arguments are passed to str.encode() and bytes.decode().
        As of Python 3.9, the available arguments are `encoding` and `errors`.
        See https://docs.python.org/3/library/stdtypes.html#str.encode and
        https://docs.python.org/3/library/stdtypes.html#bytes.decode ."""

        self._kwargs = kwargs

    def serialise(self, obj: str) -> bytes:
        """Serialise the given Python string to a byte string."""

        return obj.encode(**self._kwargs)

    def deserialise(self, data: bytes) -> str:
        """Deserialise the given byte string to a Python string."""

        return data.decode(**self._kwargs)
