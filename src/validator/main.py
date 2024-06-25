import argparse
import asyncio
import time

from communex.module.module import Module
from communex.client import CommuneClient
from communex.compat.key import classic_load_key
from communex._common import get_node_url

from substrateinterface import Keypair

from loguru import logger

from config.validator import ValidatorConfig
from comx.interface import ComxInterface
from comx.client import ComxClient

class MinerModule:
    def __init__(self, uid: int, ss58: str, address: str):
        self.uid = uid
        self.ss58 = ss58
        self.address = address

    def __repr__(self):
        return f"MinerModule(UID={self.uid}, SS58={self.ss58}, Address={self.address})"

class Validator(Module):

    def __init__(
        self,
        key: Keypair,
        netuid: int,
        client: ComxInterface,
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
        self.queried_miners: dict[int, MinerModule] = []

    def get_validator_uid(self) -> int:
        modules = self.client.get_map_modules(self.netuid, False)
        if self.key.ss58_address not in modules:
            return -1
        return modules[self.key.ss58_address]['uid']

    async def validate_step(self):
        modules = self.get_miner_addresses()

        # TODO: Ensure weights file matches modules uid-ss58 mapping.

        # TODO: Generate prompt/task.

        # TODO: Determine 8 miners that will be queried.

        # TODO: Query each of the miners.

        # TODO: Score each of the miners.

        # TODO: Write updates to weights file.

        # TODO: 
        #   If all miners are queried, vote and clear the miner cache.
        #   Else add the miners to the miner cache.

        print(f"modules: {modules}")

    def get_miner_addresses(self) -> list[MinerModule]:
        # Get all modules registered on subnet
        modules = self.client.get_map_modules(self.netuid, False)

        # Get subnet hyperparameters
        subnet = self.client.get_subnet_params(key=self.netuid)

        # Get maximum weight age for the subnet
        max_weight_age = subnet['max_weight_age']

        # Get the current block
        current_block = self.client.get_current_block()
        
        miners: list[MinerModule] = []

        # Loop through the modules and append miners to the miner list
        for m in modules.values():
            uid = m['uid']
            ss58 = m['key']
            address = m['address']
            
            # Always ignore yourself
            if uid == self.uid:
                continue 

            last_update = m['last_update']
            reg_block = m['regblock']

            if self.is_miner(last_update, reg_block, max_weight_age, current_block):
                miners.append(MinerModule(uid=uid, ss58=ss58, address=address))

        return miners
    
    def is_miner(self, last_update: int, reg_block: int, max_weight_age: int, current_block: int) -> bool:
        if last_update == reg_block:
            # Its possible a validator just registered and hasn't scored miners yet.
            # This is ok because it will soon begin scoring while in its immunity period
            # resulting in this condition no longer being true.
            return True
        else:
            # Its possible a validators last_update + max_weight_age is less than current_block
            # but that means the validator is sleeping. Validator will begin to score 0's as a
            # miner unless it wakes up and starts validating again.
            if last_update + max_weight_age < current_block:
                return True 
            
            return False

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
        client = ComxClient(client=CommuneClient(get_node_url(use_testnet=config.get_testnet())))

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

