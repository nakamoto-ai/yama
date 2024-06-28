"""
Author: Eddie
"""

from abc import ABC, abstractmethod

from communex.types import SubnetParamsWithEmission, ModuleInfoWithOptionalBalance

class ComxInterface(ABC):
    
    @abstractmethod
    def get_map_modules(
        self, netuid: int = 0, include_balances: bool = False) -> dict[str, ModuleInfoWithOptionalBalance]:
        pass
    
    @abstractmethod
    def get_subnet_params(
        self, block_hash: str | None = None, key: int = 0) -> SubnetParamsWithEmission | None:
        pass 

    @abstractmethod
    def get_current_block(self) -> int:
        pass