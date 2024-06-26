import os

from loguru import logger

from .interface import IOInterface
from comx.miner.registry import MinerRegistry
from comx.miner.module import ScoredMinerModule

class WeightIO:
    def __init__(self, io: IOInterface, dir_path: str, file_name: str):
        self.io = io
        self.dir_path: str = dir_path
        self.file_name: str = file_name
        self.file_path: str = os.path.join(self.dir_path, self.file_name)

    def validate_weights_file(self):
        if not self.io.path_exists(self.dir_path):
            self.io.make_dir(self.dir_path)
            logger.info(f"Created directory: {self.dir_path}")

        if not self.io.path_exists(self.file_path):
            self.io.write_json_file(self.file_name, {})
            logger.info(f"Created file: {self.file_path}")

    def write_weights(self, miner_registry: MinerRegistry):
        self.io.write_json_file(self.file_path, miner_registry.to_uid_dict())

    def read_weights(self) -> MinerRegistry | None:
        if not self.io.path_exists(self.file_path):
            return None 
        
        json_data = self.io.read_json_file(self.file_path)
        if json_data is None:
            return None 
        
        miner_registry = MinerRegistry()
        for _, miner_data in json_data.items():
            miner_registry.set(ScoredMinerModule(
                uid=miner_data["uid"],
                ss58=miner_data["ss58"],
                address=miner_data["address"],
                score=miner_data["score"]
            ))
        return miner_registry

if __name__ == "__main__":

    miners = MinerRegistry()
    miners.set(ScoredMinerModule(1, "ss1d", "asdf", 99))
    miners.set(ScoredMinerModule(2, "ss2", "asdf", 991))
    miners.set(ScoredMinerModule(3, "ss3", "asdf", 992))
    miners.set(ScoredMinerModule(4, "ss4", "asdf", 993))

    home_dir = os.path.expanduser("~")
    commune_dir = os.path.join(home_dir, ".commune")
    yama_dir = os.path.join(commune_dir, "yama")
    weights_file = os.path.join(yama_dir, "weights.json")
    
    from .io import IO
    wio = WeightIO(io=IO(), dir_path=yama_dir, file_name=weights_file)
    wio.validate_weights_file()
    wio.write_weights(miners)

    w = wio.read_weights()
    wd = w.to_ss58_dict()
    for k, v in wd.items():
        print(k)
        print(isinstance(k, str))

    if isinstance(w, MinerRegistry):
        print("YESSS")