import argparse
import asyncio
import time
import os
import random

from communex.module.module import Module
from communex.client import CommuneClient
from communex.compat.key import classic_load_key
from communex._common import get_node_url

from substrateinterface import Keypair

from loguru import logger

from config.validator import ValidatorConfig
from comx.interface import ComxInterface
from comx.client import ComxClient
from comx.miner.module import MinerModule, ScoredMinerModule
from comx.miner.registry import MinerRegistry
from validator.io.weights import WeightIO
from validator.io.io import IO

class Validator(Module):

    def __init__(
        self,
        key: Keypair,
        netuid: int,
        client: ComxInterface,
        weight_io: WeightIO,
        interval: int,
        call_timeout: int = 20,
        use_testnet: bool = False,
    ) -> None:
        super().__init__()
        self.client = client
        self.weight_io = weight_io
        self.key = key
        self.netuid = netuid
        self.interval = interval
        self.call_timeout = call_timeout
        self.use_testnet = use_testnet
        self.uid = None
        self.queried_miners: MinerRegistry = MinerRegistry()

    def get_validator_uid(self) -> int:
        modules = self.client.get_map_modules(self.netuid, False)
        if self.key.ss58_address not in modules:
            return -1
        return modules[self.key.ss58_address]['uid']

    async def validate_step(self):
        miners = self.get_miner_modules()
        new_registry = self.sync_miners(miners=miners)
        self.sync_cache(registry=new_registry)

        # TODO: Generate prompt/task.

        next_miners = self.next_miners(registry=new_registry)

        self.query(miners=next_miners)
        self.score(miners=next_miners)
        self.cache(miners=next_miners)

        self.weight_io.write_weights(new_registry)

        if len(self.queried_miners.get_all_by_ss58()) == len(new_registry.get_all_by_ss58()):
            # TODO: Call vote method.
            print("Time to vote!")
            self.queried_miners = MinerRegistry()

    def get_miner_modules(self) -> list[MinerModule]:
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
        
    def sync_miners(self, miners: list[MinerModule]) -> MinerRegistry:
        """
        Syncs the miners registered on the network with the persisted miners in the
        weights file. The result is returned as a MinerRegistry containing all the
        up-to-date UID-SS58 mappings. If a SS58 resulted in a changed UID, the scores
        are remembered upon updating.

        Args:
            miners: A list of MinerModules holding the current state of the network.

        Returns:
            A MinerRegistry containing the up-to-date UUID-SS58 mappings.
        """
        new_registry = MinerRegistry()
        old_registry = self.weight_io.read_weights() or MinerRegistry()

        for miner in miners:
            # Very important to get miner from the file using the ss58. This allows us
            # to remember the score of the miner incase the UID changed.
            old_miner = old_registry.get_by_ss58(miner.ss58)

            # If a miner with the same ss58 was already written to the miner stored in
            # weights file, transfer the score. Otherwise, this is a newly registered
            # miner and default to 0.
            score = 0
            if old_miner is not None:
                score = old_miner.score

            # Write the most up-to-date miner values to the new registry.
            new_registry.set(ScoredMinerModule(
                miner.uid,
                miner.ss58,
                miner.address,
                score
            ))

        return new_registry
    
    def sync_cache(self, registry: MinerRegistry):
        """
        Syncs the cached miners that already been queried with the contents of 
        registry. Cached miners are updated upon a UID-SS58 change, or if a miner
        deregistered and is no longer contained in the registry.

        This method should be called immediately following a call to sync_miners.

        Args:
            registry: A MinerRegistry holding the most up-to-date miners on the network.
        """
        # Ensure the registry that holds the already queried miners
        # is up to date with the network.
        cached_miners = self.queried_miners.get_all_by_ss58()
        for k, v in cached_miners.items():
            updated_miner = registry.get_by_ss58(k)

            # If the cached miner is no longer registered delete it
            # from the cached miners registry.
            if updated_miner is None:
                self.queried_miners.delete_by_ss58(k)
                continue

            # If the miners UID changes, delete it by UID so the
            # cached miner is not duplicated in the registry with
            # two different UIDs.
            if updated_miner.uid != v.uid:
                self.queried_miners.delete_by_uid(v.uid)

            # Write the up-to-date miner to the cached miner registry.
            self.queried_miners.set(ScoredMinerModule(
                uid=updated_miner.uid,
                ss58=updated_miner.ss58,
                address=updated_miner.address,
                score=updated_miner.score
            ))

    def next_miners(self, registry: MinerRegistry) -> MinerRegistry:
        """
        Determines and returns the next miners that should be queried. It chooses
        up to 8 miners that have not yet been queried for this voting cycle.

        Args:
            registry: The MinerRegistry representing the current state of the network.

        Returns:
            A MinerRegistry containing the miners that should be queried next.
        """
        counter = 0
        next_miners = MinerRegistry()
        new_registry_dict = registry.get_all_by_uid()
        for _, v in new_registry_dict.items():
            queried_miner = self.queried_miners.get_by_ss58(v.ss58)

            # If miner was already queried skip and go to the next.
            if queried_miner is not None:
                continue 

            next_miners.set(v)
            counter += 1

            if counter == 8:
                break
        
        return next_miners
    
    def query(self, miners: MinerRegistry):
        """
        Takes a list of miners that should be queried.

        TODO: This function is a placeholder - needs to be updated

        Args:
            miners: The MinerRegistry containing the miners that will be queried.
        """
        miners_dict = miners.get_all_by_uid()
        for k, v in miners_dict.items():
            print(f"UID: {k}, Values: {v}")

    def score(self, miners: MinerRegistry):
        """
        Takes a list of miners that will be scored.

        TODO: This function is a placeholder - needs to be updated

        Args:
            miners: The MinerRegistry containing the miners that will be scored.
        """
        miners_dict = miners.get_all_by_uid()
        for _, v in miners_dict.items():
            # TODO: Score each of the miners.
            random_number = random.randint(1, 1000)
            v.score = random_number
            miners.set(v)

    def cache(self, miners: MinerRegistry):
        """
        Takes a MinerRegistry containing the queried and scored miners for
        this voting cycle and caches the data in queried_miners.

        Args:
            miners: The MinerRegistry containing all the queried and scored miners.
        """
        miners_dict = miners.get_all_by_uid()
        for k, v in miners_dict.items():
            self.queried_miners.set(ScoredMinerModule(
                uid=k,
                ss58=v.ss58,
                address=v.address,
                score=v.score
            ))
    
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

    home_dir = os.path.expanduser("~")
    commune_dir = os.path.join(home_dir, ".commune")
    yama_dir = os.path.join(commune_dir, "yama")

    config = ValidatorConfig(env_path=args.env, ignore_config_file=args.ignore_env_file)

    try:
        keypair = classic_load_key(config.get_key_name())
        client = ComxClient(client=CommuneClient(get_node_url(use_testnet=config.get_testnet())))

        validator = Validator(
            key=keypair,
            netuid=config.get_netuid(),
            client=client,
            weight_io=WeightIO(io=IO(), dir_path=yama_dir, file_name="weights.json"),
            interval=config.get_validator_interval(),
            call_timeout=20,
            use_testnet=config.get_testnet()
        )

        validator.validation_loop()
    except ValueError as e:
        print(e)

