from enum import StrEnum, auto


class DNSQueryType(StrEnum):
    UDP = auto()
    TCP = auto()
    TLS = auto()
    HTTPS = auto()

    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))