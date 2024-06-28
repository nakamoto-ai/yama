"""
Author: Eddie
"""

import os
from dotenv import load_dotenv

ENV_KEY_NAME = "KEY_NAME"
ENV_TESTNET = "TESTNET"
ENV_NETUID = "NETUID"

class BaseConfig:
    def __init__(self, env_path='.env', ignore_config_file=False):
        if ignore_config_file == False:
            load_dotenv(dotenv_path=env_path, override=True)

    def _get(self, key, default=None):
        value = os.getenv(key, default)
        
        if value is None or value == "":
            value = default 

        return value
    
    def get_key_name(self) -> str:
        key = self._get(ENV_KEY_NAME)
        
        if not key:
            raise ValueError(f"The environment variable '{ENV_KEY_NAME}' is required but not set or is empty.")

        return str(key)
    
    def get_testnet(self) -> bool:
        value = self._get(ENV_TESTNET, '0')
        return value == '1'
    
    def get_netuid(self) -> int:
        netuid = self._get(ENV_NETUID, None)

        if not netuid:
            raise ValueError(f"The environment variable '{ENV_NETUID}' is required but not set or is empty.")

        if not netuid.isdigit():
            raise ValueError(f"The environment variable '{ENV_NETUID}' should only contain digits.")
        
        return int(netuid)