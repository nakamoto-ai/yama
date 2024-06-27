from unittest import TestCase
from unittest.mock import create_autospec

from communex.types import ModuleInfoWithOptionalBalance, SubnetParamsWithEmission

from comx.interface import ComxInterface
from comx.miner.module import MinerModule, ScoredMinerModule
from comx.miner.registry import MinerRegistry

from validator.main import Validator
from validator.io.weights import WeightIOInterface

class TestValidator(TestCase):

    def setUp(self):
        self.mock_comx = create_autospec(ComxInterface, instance=True)
        self.mock_weights_io = create_autospec(WeightIOInterface, instance=True)

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
                assert(m.ss58 in expected_miners), f"{test_name}: Did not expect miner {m.ss58} to be returned"
                
                expected_result = expected_miners[m.ss58]
                assert(expected_result), f"{test_name} Expected {m.ss58} to not be a miner"

                if expected_result:
                    uid = modules[m.ss58]["uid"]
                    ss58 = modules[m.ss58]["key"]
                    address = modules[m.ss58]["address"]

                    assert(m.uid == uid), f"{test_name} Miner {ss58}: Expected uid {uid}, got {m.uid}"
                    assert(m.ss58 == ss58), f"{test_name} Miner {ss58}: Expected ss58 {ss58}, got {m.ss58}"
                    assert(m.address == address), f"{test_name} Miner {ss58}: Expected address {address}, got {m.address}"

                del expected_miners[m.ss58]

            # All remaining modules should be false which specifies that it is not
            # an expected miner.
            for k, v in expected_miners.items():
                assert(not v), f"{test_name} Expected miner {k} to be removed"

    def test_sync_miners(self):
        """
        Unit tests the Validator sync_miners method using table testing.
        """
        test_cases = [
            {
                "name": "Test 1: Network and local miners match",
                "network_miners": [
                    MinerModule(uid=1, ss58="a", address="0.0.0.0:0"),
                    MinerModule(uid=2, ss58="b", address="0.0.0.0:1")
                ],
                "file_miners": [
                    ScoredMinerModule(uid=1, ss58="a", address="0.0.0.0:0", score=900),
                    ScoredMinerModule(uid=2, ss58="b", address="0.0.0.0:1", score=500)
                ],
                "expected": {
                    "a": ScoredMinerModule(uid=1, ss58="a", address="0.0.0.0:0", score=900),
                    "b": ScoredMinerModule(uid=2, ss58="b", address="0.0.0.0:1", score=500)
                }
            },
            {
                "name": "Test 2: Miner deregistered",
                "network_miners": [
                    MinerModule(uid=1, ss58="a", address="0.0.0.0:0"),
                    MinerModule(uid=2, ss58="b", address="0.0.0.0:1")
                ],
                "file_miners": [
                    ScoredMinerModule(uid=1, ss58="a", address="0.0.0.0:0", score=900),
                    ScoredMinerModule(uid=2, ss58="b", address="0.0.0.0:1", score=500),
                    ScoredMinerModule(uid=3, ss58="c", address="0.0.0.0:2", score=1000)
                ],
                "expected": {
                    "a": ScoredMinerModule(uid=1, ss58="a", address="0.0.0.0:0", score=900),
                    "b": ScoredMinerModule(uid=2, ss58="b", address="0.0.0.0:1", score=500)
                }
            },
            {
                "name": "Test 3: New miner registers",
                "network_miners": [
                    MinerModule(uid=1, ss58="a", address="0.0.0.0:0"),
                    MinerModule(uid=2, ss58="b", address="0.0.0.0:1"),
                    MinerModule(uid=3, ss58="c", address="0.0.0.0:2")
                ],
                "file_miners": [
                    ScoredMinerModule(uid=1, ss58="a", address="0.0.0.0:0", score=900),
                    ScoredMinerModule(uid=2, ss58="b", address="0.0.0.0:1", score=500)
                ],
                "expected": {
                    "a": ScoredMinerModule(uid=1, ss58="a", address="0.0.0.0:0", score=900),
                    "b": ScoredMinerModule(uid=2, ss58="b", address="0.0.0.0:1", score=500),
                    "c": ScoredMinerModule(uid=3, ss58="c", address="0.0.0.0:2", score=0)
                }
            },
            {
                "name": "Test 4: Miner address changes",
                "network_miners": [
                    MinerModule(uid=1, ss58="a", address="0.0.0.0:0"),
                    MinerModule(uid=2, ss58="b", address="0.0.0.0:5000")
                ],
                "file_miners": [
                    ScoredMinerModule(uid=1, ss58="a", address="0.0.0.0:0", score=900),
                    ScoredMinerModule(uid=2, ss58="b", address="0.0.0.0:1", score=500)
                ],
                "expected": {
                    "a": ScoredMinerModule(uid=1, ss58="a", address="0.0.0.0:0", score=900),
                    "b": ScoredMinerModule(uid=2, ss58="b", address="0.0.0.0:5000", score=500)
                }
            },
            {
                "name": "Test 5: Miner uid changes",
                "network_miners": [
                    MinerModule(uid=4, ss58="a", address="0.0.0.0:0"),
                    MinerModule(uid=1, ss58="b", address="0.0.0.0:1"),
                    MinerModule(uid=3, ss58="c", address="0.0.0.0:2"),
                    MinerModule(uid=2, ss58="d", address="0.0.0.0:3")
                ],
                "file_miners": [
                    ScoredMinerModule(uid=1, ss58="a", address="0.0.0.0:0", score=900),
                    ScoredMinerModule(uid=2, ss58="b", address="0.0.0.0:1", score=500),
                    ScoredMinerModule(uid=3, ss58="c", address="0.0.0.0:2", score=700),
                    ScoredMinerModule(uid=4, ss58="d", address="0.0.0.0:3", score=350)
                ],
                "expected": {
                    "a": ScoredMinerModule(uid=4, ss58="a", address="0.0.0.0:0", score=900),
                    "b": ScoredMinerModule(uid=1, ss58="b", address="0.0.0.0:1", score=500),
                    "c": ScoredMinerModule(uid=3, ss58="c", address="0.0.0.0:2", score=700),
                    "d": ScoredMinerModule(uid=2, ss58="d", address="0.0.0.0:3", score=350)
                }
            }
        ]

        for tc in test_cases:
            name: str = tc["name"]
            network_miners: list[MinerModule] = tc["network_miners"]
            file_miners: list[ScoredMinerModule] = tc["file_miners"]
            expected: dict[str, ScoredMinerModule] = tc["expected"]

            file_registry = MinerRegistry()
            for m in file_miners:
                file_registry.set(m)

            def mock_read_weights():
                nonlocal file_registry
                return file_registry
            
            self.mock_weights_io.read_weights.side_effect = mock_read_weights

            validator = Validator(key=None, netuid=0, client=None, weight_io=self.mock_weights_io, interval=20)

            result_registry = validator.sync_miners(miners=network_miners)
            result = result_registry.get_all_by_ss58()

            # Loop through the result of sync_miners and ensure the data updated correctly.
            for k, v in result.items():
                assert(k in expected), f"{name} Expected miner '{k}' to be in result registry"

                uid = expected[k].uid
                ss58 = expected[k].ss58
                score = expected[k].score
                address = expected[k].address

                assert(v.uid == uid), f"{name}: Miner {k}: Expected uid {uid}, got {v.uid}"
                assert(v.ss58 == ss58), f"{name}: Miner {k}: Expected ss58 {ss58}, got {v.ss58}"
                assert(v.score == score), f"{name}: Miner {k}: Expected score {score}, got {v.score}"
                assert(v.address == address), f"{name}: Miner {k}: Expected address {address}, got {v.address}"

                del expected[k]

            assert(len(expected) == 0), f"{name}: Expected these miners to be in result: {expected}"
            




            

