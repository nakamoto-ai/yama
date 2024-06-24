import argparse
import asyncio
import time

from communex.module.module import Module
from communex.client import CommuneClient
from communex.compat.key import classic_load_key
from communex._common import get_node_url
from communex.misc import get_map_modules

from substrateinterface import Keypair

from loguru import logger

from config.validator import ValidatorConfig

class MinerModule:
    def __init__(self, uid: int, ss58: str, address: str):
        self.UID = uid
        self.SS58 = ss58
        self.Address = address

    def __repr__(self):
        return f"MinerModule(UID={self.UID}, SS58={self.SS58}, Address={self.Address})"

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

    def get_validator_uid(self) -> int:
        modules = get_map_modules(self.client, netuid=self.netuid, include_balances=False)
        if self.key.ss58_address not in modules:
            return -1
        return modules[self.key.ss58_address]['uid']

    async def validate_step(self):
        modules = self.get_miner_addresses()
        print(f"modules: {modules}")

    def get_miner_addresses(self):
        modules = get_map_modules(self.client, netuid=self.netuid, include_balances=False)
        miners: list[MinerModule] = []

        for m in modules.values():
            uid = m['uid']
            ss58 = m['key']
            address = m['address']
            incentive = m['incentive']
            dividends = m['dividends']
            
            if uid == self.uid:
                continue 

            if incentive == dividends == 0 or incentive > dividends:
                miners.append(MinerModule(uid=uid, ss58=ss58, address=address))

        return miners

    def set_weights(self):
        pass

    def validation_loop(self) -> None:
        while True:
            uid = self.get_validator_uid()
            self.uid = uid 

            if self.uid != -1:
                logger.info("Begin validator step... ")
                asyncio.run(self.validate_step())
            else:
                logger.info("Validator not registered, skipping step...")
    
            logger.info(f"Sleeping for {self.interval} seconds... ")
            time.sleep(self.interval)

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

        validator.validation_loop()
    except ValueError as e:
        print(e)

