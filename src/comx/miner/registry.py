from typing import List

from .module import ScoredMinerModule

class MinerRegistry:
    def __init__(self) -> None:
        self._uid_dict: dict[int, ScoredMinerModule] = {}
        self._ss58_dict: dict[str, ScoredMinerModule] = {}

    def set(self, miner: ScoredMinerModule):
        self._uid_dict[miner.uid] = miner 
        self._ss58_dict[miner.ss58] = miner

    def get_by_uid(self, uid: int) -> ScoredMinerModule | None:
        if uid not in self._uid_dict:
            return None 
        
        return self._uid_dict[uid]
    
    def get_by_ss58(self, ss58: str) -> ScoredMinerModule | None:
        if ss58 not in self._ss58_dict:
            return None 
        
        return self._ss58_dict[ss58]
    
    def delete_by_uid(self, uid: int):
        self._delete(self.get_by_uid(uid))
    
    def delete_by_ss58(self, ss58: str):
        self._delete(self.get_by_ss58(ss58))

    def _delete(self, miner: ScoredMinerModule):
        if miner is None:
            return 
        
        del self._uid_dict[miner.uid]
        del self._ss58_dict[miner.ss58]

    def get_all_by_uid(self) -> dict[int, ScoredMinerModule]:
        return self._uid_dict.copy()
    
    def get_all_by_ss58(self) -> dict[str, ScoredMinerModule]:
        return self._ss58_dict.copy()