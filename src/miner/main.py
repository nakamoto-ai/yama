import argparse
from config.miner import MinerConfig

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="yama miner")
    parser.add_argument("--env", type=str, default=".env", help="config file path")
    parser.add_argument('--ignore-env-file', action='store_true', help='If set, ignore .env file')
    args = parser.parse_args()
    
    config = MinerConfig(ignore_config_file=False)

    try:
        print(f"KEY_NAME: {config.get_key_name()}")
        print(f"TESTNET: {config.get_testnet()}")
        print(f"MINER_URL: {config.get_miner_url()}")
    except ValueError as e:
        print(e)

    if args.miner == "spacy":
        from spacy_miner.py import SpacyMiner
        miner = SpacyMiner(config=config)
        SpacyMiner.start_miner_server(miner=miner)
    else:
        print("Error: Unsupported Miner")
