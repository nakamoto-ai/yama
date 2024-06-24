import argparse
from config.validator import ValidatorConfig

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="yama validator")
    parser.add_argument("--env", type=str, default=".env", help="config file path")
    parser.add_argument('--ignore-env-file', action='store_true', help='If set, ignore .env file')
    args = parser.parse_args()

    config = ValidatorConfig(env_path=args.env, ignore_config_file=args.ignore_env_file)

    try:
        print(f"KEY_NAME: {config.get_key_name()}")
        print(f"TESTNET: {config.get_testnet()}")
        print(f"VALIDATOR_INTERVAL: {config.get_validator_interval()}")
    except ValueError as e:
        print(e)

