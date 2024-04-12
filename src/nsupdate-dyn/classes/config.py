from dataclasses import dataclass, asdict
import json


@dataclass
class Config:
    ip_resolver: str = "http://ifconfig.co/ip"
    key_file: str
    domains_to_update: list[str] = []
    zone: str
    server: str

    @staticmethod
    def from_json(config_file: str):
        if not config_file:
            config_file = "/etc/nsupdate-dyn/config.json"

        config_dict_ = {}

        with open(config_file, "r") as f:
            config_dict_ = json.load(f)

        return Config(**config_dict_)

    def as_dict(self) -> dict:
        return asdict(self)