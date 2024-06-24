from .base import BaseConfig

ENV_VALIDATOR_INTERVAL = "VALIDATOR_INTERVAL"

class ValidatorConfig(BaseConfig):
    def __init__(self, env_path='.env', ignore_config_file=False):
        super().__init__(env_path, ignore_config_file)

    def get_validator_interval(self) -> int:
        interval = self._get(ENV_VALIDATOR_INTERVAL, '10')

        if not interval.isdigit():
            raise ValueError(f"The environment variable '{ENV_VALIDATOR_INTERVAL}' should only contain digits.")
        
        return int(interval)