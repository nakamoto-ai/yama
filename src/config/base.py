import os
from dotenv import load_dotenv

ENV_KEY_NAME = "KEY_NAME"
ENV_TESTNET = "TESTNET"

class BaseConfig:
    def __init__(self, env_path='.env', ignore_config_file=False):
        if ignore_config_file == False:
            load_dotenv(dotenv_path=env_path)

    def _get(self, key, default=None):
        return os.getenv(key, default)
    
    def get_key_name(self) -> str:
        key = self._get(ENV_KEY_NAME)
        
        if not key:
            raise ValueError(f"The environment variable '{ENV_KEY_NAME}' is required but not set or is empty.")

        return str(key)
    
    def get_testnet(self) -> bool:
        value = self._get(ENV_TESTNET, '0')
        return value == '1'