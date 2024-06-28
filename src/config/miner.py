"""
Author: Eddie
"""

from .base import BaseConfig

ENV_MINER_URL = "MINER_URL"

class MinerConfig(BaseConfig):
    def __init__(self, env_path='.env', ignore_config_file=False):
        super().__init__(env_path, ignore_config_file)

    def get_miner_url(self) -> str:
        return str(self._get(ENV_MINER_URL, "http://0.0.0.0:5000"))