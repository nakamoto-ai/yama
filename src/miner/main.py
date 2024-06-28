import argparse
from urllib.parse import urlparse
import uvicorn
from keylimiter import TokenBucketLimiter
from communex.module.server import ModuleServer
from communex.compat.key import classic_load_key
from config.miner import MinerConfig
from miner.nltk_miner import NltkMiner

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="yama miner")
    parser.add_argument("--env", type=str, default=".env", help="config file path")
    parser.add_argument('--ignore-env-file', action='store_true', help='If set, ignore .env file')
    args = parser.parse_args()

    config = MinerConfig(env_path=args.env, ignore_config_file=False)

    try:
        keypair = classic_load_key(config.get_key_name())
        bucket = TokenBucketLimiter(1000, 1 / 100)

        server = ModuleServer(
             NltkMiner(),
             keypair,
             limiter=bucket,
             subnets_whitelist=[23],
             use_testnet=config.get_testnet()
        )

        parsed_url = urlparse(config.get_miner_url())

        app = server.get_fastapi_app()
        uvicorn.run(app, host=parsed_url.hostname, port=parsed_url.port)
    except ValueError as e:
        print(e)
