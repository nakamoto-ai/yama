from unittest import TestCase
from unittest.mock import create_autospec

from communex.types import ModuleInfoWithOptionalBalance, SubnetParamsWithEmission

from comx.interface import ComxInterface

from validator.main import Validator

class TestValidator(TestCase):

    def setUp(self):
        self.mock_comx = create_autospec(ComxInterface, instance=True)

    def test_get_miner_modules(self):
        """
        Unit tests the Validator get_miner_modules method using table testing.
        """
        test_cases = [
            {
                "name": "Test 1",
                "max_weight_age": 100,
                "current_block": 1099,
                "modules": {
                    "a": ModuleInfoWithOptionalBalance(uid=1, key="a", address="1.1.1.1:0", last_update=1, regblock=1),
                    "b": ModuleInfoWithOptionalBalance(uid=2, key="b", address="1.1.1.1:1", last_update=2, regblock=1),
                    "c": ModuleInfoWithOptionalBalance(uid=3, key="c", address="1.1.1.1:2", last_update=10, regblock=1),
                    "d": ModuleInfoWithOptionalBalance(uid=4, key="d", address="0.0.0.0:3", last_update=90, regblock=10),
                    "e": ModuleInfoWithOptionalBalance(uid=5, key="e", address="1.1.1.1:4", last_update=15, regblock=1),
                    "f": ModuleInfoWithOptionalBalance(uid=6, key="f", address="1.1.1.1:5", last_update=999, regblock=100)},
                "expected_miners": {"a": True, "b": True, "c": True, "d": True, "e": True, "f": False}
            },
            {
                "name": "Test 2",
                "max_weight_age": 100,
                "current_block": 1050,
                "modules": {
                    "a": ModuleInfoWithOptionalBalance(uid=1, key="a", address="1.1.1.1:0", last_update=1, regblock=1),
                    "b": ModuleInfoWithOptionalBalance(uid=2, key="b", address="1.1.1.1:1", last_update=2, regblock=1),
                    "c": ModuleInfoWithOptionalBalance(uid=3, key="c", address="1.1.1.1:2", last_update=10, regblock=1),
                    "d": ModuleInfoWithOptionalBalance(uid=4, key="d", address="0.0.0.0:3", last_update=90, regblock=10),
                    "e": ModuleInfoWithOptionalBalance(uid=5, key="e", address="1.1.1.1:4", last_update=15, regblock=1),
                    "f": ModuleInfoWithOptionalBalance(uid=6, key="f", address="1.1.1.1:5", last_update=999, regblock=100)},
                "expected_miners": {"a": True, "b": True, "c": True, "d": True, "e": True, "f": False}
            },
            {
                "name": "Test 3",
                "max_weight_age": 100,
                "current_block": 103,
                "modules": {
                    "a": ModuleInfoWithOptionalBalance(uid=1, key="a", address="1.1.1.1:0", last_update=1, regblock=1),
                    "b": ModuleInfoWithOptionalBalance(uid=2, key="b", address="1.1.1.1:1", last_update=2, regblock=1),
                    "c": ModuleInfoWithOptionalBalance(uid=3, key="c", address="1.1.1.1:2", last_update=10, regblock=1),
                    "d": ModuleInfoWithOptionalBalance(uid=4, key="d", address="0.0.0.0:3", last_update=90, regblock=10),
                    "e": ModuleInfoWithOptionalBalance(uid=5, key="e", address="1.1.1.1:4", last_update=15, regblock=1)},
                "expected_miners": {"a": True, "b": True, "c": False, "d": False, "e": False}
            },
            {
                "name": "Test 4",
                "max_weight_age": 20,
                "current_block": 30,
                "modules": {
                    "a": ModuleInfoWithOptionalBalance(uid=1, key="a", address="1.1.1.1:0", last_update=1, regblock=1),
                    "b": ModuleInfoWithOptionalBalance(uid=2, key="b", address="1.1.1.1:1", last_update=2, regblock=1),
                    "c": ModuleInfoWithOptionalBalance(uid=3, key="c", address="1.1.1.1:2", last_update=10, regblock=1),
                    "e": ModuleInfoWithOptionalBalance(uid=5, key="e", address="1.1.1.1:4", last_update=15, regblock=1),},
                "expected_miners": {"a": True, "b": True, "c": False, "e": False}
            }
        ]

        for tc in test_cases:
            test_name: str = tc["name"]
            max_weight_age: int = tc["max_weight_age"]
            current_block: int = tc["current_block"]
            expected_miners: dict[str, bool] = tc["expected_miners"]
            modules: dict[str, ModuleInfoWithOptionalBalance] = tc["modules"]

            def mock_get_map_modules(self, netuid: int = 0, include_balances: bool = False):
                nonlocal modules
                return modules
        
            self.mock_comx.get_map_modules.side_effect = mock_get_map_modules
            self.mock_comx.get_subnet_params.return_value = SubnetParamsWithEmission(max_weight_age=max_weight_age)
            self.mock_comx.get_current_block.return_value = current_block

            validator = Validator(key=None, netuid=0, client=self.mock_comx, weight_io=None, interval=20)
            miners = validator.get_miner_modules()

            # Loop through all returned miners and check to see if it was expected
            # to be returned as a miner.
            for m in miners:
                if m.ss58 not in expected_miners:
                    raise ValueError(f"Testing Logic Error: {m.ss58} not defined in expected_miners")
                
                expected_result = expected_miners[m.ss58]
                assert(expected_result), f"{test_name} Expected {m.ss58} to not be a miner"

                del expected_miners[m.ss58]

            # All remaining modules should be false which specifies that it is not
            # an expected miner.
            for k, v in expected_miners.items():
                assert(not v), f"{test_name} Expected miner {k} to be removed"



            

