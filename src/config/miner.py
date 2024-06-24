from .base import BaseConfig

ENV_MINER_URL = "MINER_URL"

class MinerConfig(BaseConfig):
    def __init__(self, env_path='.env', ignore_config_file=False):
        super().__init__(env_path, ignore_config_file)

    def get_miner_url(self) -> str:
        url = self._get(ENV_MINER_URL, None)

        if url is None or url == "":
            url = "http://0.0.0.0:5000"

        return str(url)