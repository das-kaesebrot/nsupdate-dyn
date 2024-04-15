from dataclasses import dataclass, asdict, field
from os.path import isfile
from os import makedirs
from pathlib import Path
import json


@dataclass
class Config:
    key_file: str = "/absolute/path/to/key/file"
    domains_to_update: list[str] = field(default_factory=list)
    zone: str = "example.com"
    server: str = "ns1.example.com"
    ip_resolver: str = "http://ifconfig.co/ip"

    @staticmethod
    def from_json(config_file: str):
        if not isfile(config_file):
            Config.generate_json(config_file)

        config_dict_ = {}

        with open(config_file, "r") as f:
            config_dict_ = json.load(f)

        return Config(**config_dict_)

    @staticmethod
    def generate_json(config_file: str):
        config_file_path = Path(config_file)
        
        if not config_file_path.parent.exists():
            makedirs(config_file_path.parent.as_posix())
        
        with open(config_file, "x") as f:
            json.dump(Config().as_dict(), fp=f, indent=4)

    def get_dnskey_dict(self) -> dict:
        with open(self.key_file, "r") as f:
            return json.load(f)

    def as_dict(self) -> dict:
        return asdict(self)
