"""Typed outcomes shared by transports, drivers, and contracts."""


class DriverForgeError(Exception):
    """Base supported-operation error."""


class ParseError(DriverForgeError):
    pass


class DeadlineExceeded(DriverForgeError):
    pass


class UnknownWriteOutcome(DriverForgeError):
    pass


class DeviceError(DriverForgeError):
    pass


class IllegalAddress(DeviceError):
    pass


class UnsupportedOperation(DriverForgeError):
    pass


class Cancelled(DriverForgeError):
    pass


class Closed(DriverForgeError):
    pass


class InvalidInput(DriverForgeError):
    pass


class ResourceLimit(InvalidInput):
    pass
