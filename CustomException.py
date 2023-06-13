class MissingDataException(Exception):
    pass


class IntegrityException(Exception):
    pass


class CRCException(IntegrityException):
    pass
