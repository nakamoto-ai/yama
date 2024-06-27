import argparse

from communex.client import CommuneClient
from communex.compat.key import classic_load_key
from communex._common import get_node_url

from config.miner import MinerConfig
from nltk_miner import NltkMiner

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="yama miner")
    parser.add_argument("--env", type=str, default=".env", help="config file path")
    parser.add_argument('--ignore-env-file', action='store_true', help='If set, ignore .env file')
    args = parser.parse_args()
    
    config = MinerConfig(env_path=args.env, ignore_config_file=False)

    try:
        keypair = classic_load_key(config.get_key_name())
        client = CommuneClient(get_node_url(use_testnet=config.get_testnet()))

        miner = NltkMiner(config=config)
        NltkMiner.start_miner_server(miner=miner)
    except ValueError as e:
        print(e)
