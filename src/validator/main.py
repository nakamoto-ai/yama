import argparse

from communex.module.module import Module
from communex.client import CommuneClient
from communex.compat.key import classic_load_key
from communex._common import get_node_url

from substrateinterface import Keypair

from config.validator import ValidatorConfig

class Validator(Module):

    def __init__(
        self,
        key: Keypair,
        netuid: int,
        client: CommuneClient,
        interval: int,
        call_timeout: int = 20,
        use_testnet: bool = False,
    ) -> None:
        super().__init__()
        self.client = client
        self.key = key
        self.netuid = netuid
        self.interval = interval
        self.call_timeout = call_timeout
        self.use_testnet = use_testnet
        self.uid = None

        print(f"KEY: {self.key}")
        print(f"INTERVAL: {self.interval}")
        print(f"TIMEOUT: {self.call_timeout}")
        print(f"TESTNET: {self.use_testnet}")

    def validate_step(self):
        pass 

    def set_weights(self):
        pass

    def validation_loop(self) -> None:
        pass

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="yama validator")
    parser.add_argument("--env", type=str, default=".env", help="config file path")
    parser.add_argument('--ignore-env-file', action='store_true', help='If set, ignore .env file')
    args = parser.parse_args()

    config = ValidatorConfig(env_path=args.env, ignore_config_file=args.ignore_env_file)

    try:
        keypair = classic_load_key(config.get_key_name())
        client = CommuneClient(get_node_url(use_testnet=config.get_testnet()))

        validator = Validator(
            key=keypair,
            netuid=config.get_netuid(),
            client=client,
            interval=config.get_validator_interval(),
            call_timeout=20,
            use_testnet=config.get_testnet()
        )
    except ValueError as e:
        print(e)

