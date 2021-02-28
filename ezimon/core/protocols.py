from collections import deque
from struct import Struct
from typing import List, Tuple, Optional

from ezimon.core import logger


# Maximum lengths of the queues used to hold (de)serialised data.
_MAX_QUEUE_LEN = 100


class BaseBinaryProtocol:
    """A base protocol which (de)serialises an object to/from bytes."""

    def __init__(self):
        # Double-ended queues to store (de)serialised data.
        # We use the "left" side to put items, and "right" side to pop.
        self._ser_q = deque(maxlen=100)
        self._deser_q = deque(maxlen=100)

    def process_data(self, data: bytes):
        """Process a chunk of data, which may result in one or more sets of
        values being placed on the deserialised queue.

        Subclasses should implement this and call ``submit_deserialised()`` if
        deserialisation is completed.
        """

        raise NotImplementedError

    def process_values(self, values: tuple):
        """Process a tuple of values, which should result in a chunk of data
        being placed on the serialised queue.

        Subclasses should implement this and call ``submit_serialised()`` if
        serialisation is complete.
        """

        raise NotImplementedError

    def submit_serialised(self, data: bytes):
        """Submit processed serialised data.

        :param data: serialised ``bytes`` object to submit.
        """

        self._ser_q.appendleft(data)

    def submit_deserialised(self, values: tuple):
        """Submit processed deserialised values.

        :param values: tuple of deserialised values.
        """

        self._deser_q.appendleft(values)

    def get_next_serialised(self) -> Optional[bytes]:
        """Retrieves the next (oldest) serialised data item in the queue and
        returns it. Returns None if there is no data in the queue.
        """

        try:
            return self._ser_q.pop()
        except IndexError:
            return None

    def get_next_deserialised(self) -> Optional[tuple]:
        """Retrieves the next (oldest) tuple of deserialised values in the queue
        and returns it. Returns None if there is no items in the queue."""

        try:
            return self._deser_q.pop()
        except IndexError:
            return None


class StringBinaryProtocol(BaseBinaryProtocol):
    """Protocol which encodes Python strings to byte strings during
    serialisation and decodes during deserialisation.

    :param encoding: encoding to use when (de)serialising. See
        https://docs.python.org/3/library/codecs.html#standard-encodings for
        available encodings. Defaults to 'utf-8'
    """

    def __init__(self, encoding: str = 'utf-8'):

        super().__init__()

        self.encoding = encoding

        # Stores data which needs to be processed along with the next data.
        self._pending_data = None

    def process_data(self, data: bytes):
        # Ignore empty data.
        if not data:
            return

        # Append any pending data.
        if self._pending_data is not None:
            data = self._pending_data + data
            self._pending_data = None

        try:
            s = data.decode(encoding=self.encoding, errors='strict')
        except UnicodeDecodeError as e:
            assert e.object == data

            # Process any data before the start of the error.
            self.process_data(data[:e.start])

            # If the error occurred at the end of the data, it could be that
            # more data still needs to arrive to decode, so set it to pending.
            if e.end == len(data):
                self._pending_data = data[e.start:e.end]

            # Otherwise, log an error for the part which specifically caused an
            # error, and try and process data after.
            else:
                logger.error('failed to decode %s: %s',
                             data[e.start:e.end], str(e))
                self.process_data(data[e.end:])
        else:
            self.submit_deserialised((s,))

    def process_values(self, values: tuple):
        if len(values) != 1:
            raise ValueError('values must be of length 1')

        s = values[0]
        try:
            b = s.encode(encoding=self.encoding, errors='strict')
        except UnicodeError as e:
            logger.error('failed to encode %s: %s', s, str(e))
        else:
            self.submit_serialised(b)


class FixedLengthBinaryProtocol(BaseBinaryProtocol):
    """Protocol which (de)serialises a fixed number of fixed length fields.

    :param field_definitions: a list of field definitions. See below for details

    Each field definition is a 2-tuple defining the format of each field with
    the format ``(type, length)``. ``type`` should be a string of one of the
    following formats. `length` should be the length of the field in bytes.
    Some types have restrictions on the ``length`` parameter.

    .. list-table:: Available field types
        :header-rows: 1

        * - ``type``
          - Description
          - ``length`` restrictions
        * - ``'int'``
          - Signed integer; returns a Python ``int``
          - > 0
        * - ``'uint'``
          - Unsigned integer; returns a Python ``int``
          - > 0
        * - ``'bool'``
          - Boolean; returns a Python ``bool``: ``True`` or ``False``
          - Only ``1``
        * - ``'float'``
          - Single or double precision floating point number; returns a Python
            ``float``
          - ``4`` (for single precision) or ``8`` (for double precision)
        * - ``'bytes'``
          - A sequence of bytes returned unaltered
          - > 0

    """

    def __init__(self, field_definitions: List[Tuple[str, int]]):
        super().__init__()

        _struct_lookup = {
            ('int', 1): 'b',
            ('int', 2): 'h',
            ('int', 4): 'i',
            ('int', 8): 'q',
            ('uint', 1): 'B',
            ('uint', 2): 'H',
            ('uint', 4): 'I',
            ('uint', 8): 'Q',
            ('bool', 1): '?',
            ('float', 4): 'f',
            ('float', 8): 'd'
        }

        fmt_parts = ['>']
        for type_, length in field_definitions:
            try:
                fmt_parts.append(_struct_lookup[(type_, length)])
            except KeyError:
                fmt_parts.append(f'{length}s')

        self._struct = Struct(''.join(fmt_parts))
