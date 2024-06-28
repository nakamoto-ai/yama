"""
Author: Eddie
"""

from comx.interface import ComxInterface

from communex.client import CommuneClient
from communex.types import SubnetParamsWithEmission, ModuleInfoWithOptionalBalance
from communex.misc import get_map_modules, get_map_subnets_params

class ComxClient(ComxInterface):

    def __init__(self, client: CommuneClient):
        self.client = client

    def get_map_modules(
        self, 
        netuid: int = 0, 
        include_balances: bool = False) -> dict[str, ModuleInfoWithOptionalBalance]:

        return get_map_modules(self.client, netuid, include_balances)
    
    def get_subnet_params(
        self, 
        block_hash: str | None = None, 
        key: int = 0) -> SubnetParamsWithEmission | None:

        subnets = get_map_subnets_params(self.client, block_hash)
        subnet = subnets.get(key, None)
        return subnet

    def get_current_block(self) -> int:

        current_block = self.client.get_block()["header"]["number"]
        return int(current_block)
