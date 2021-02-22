class BaseProtocol:
    def serialise(self, obj):
        """Serialise the given object into data."""

        raise NotImplementedError

    def deserialise(self, data):
        """Deserialise the given data into an object."""

        raise NotImplementedError
