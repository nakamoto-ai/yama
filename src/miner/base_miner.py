import time
from communex.module import Module, endpoint
from keylimiter import TokenBucketLimiter
from communex.module.server import ModuleServer
import uvicorn
from communex.compat.key import classic_load_key
from loguru import logger
from urllib.parse import urlparse
from abc import abstractmethod

class BaseMiner(Module):

    @endpoint
    def generate(self, prompt: str) -> Dict[str, Any]:
        start_time = time.time()
        logger.info(f"Generating resume... ")

        logger.info(f"Job Description: {prompt}")

        resume = self.generate_resume(prompt)

        logger.info(f"Generated Resume: {resume}")

        end_time = time.time()
        execution_time = end_time - start_time
        logger.info(f"Responded in {execution_time} seconds")

        return {"answer": resume}

    @abstractmethod
    def generate_resume(self, prompt: str):
        parse_args
    
    @staticmethod
    def start_miner_server(miner):
        key = classic_load_key(miner.config.get_value("keyfile"))
        url = miner.config.get_value("url")
        parsed_url = urlparse(url)

        refill_rate = 1 / 100

        use_testnet = True if miner.config.get_value("isTestnet") == 1 else False
        if use_testnet:
            logger.info("Connecting to TEST network ...")
        else:
            logger.info("Connecting to main network ...")

        bucket = TokenBucketLimiter(1000, refill_rate)
        server = ModuleServer(miner, key, limiter=bucket, subnets_whitelist=[1], use_testnet=use_testnet)
        app = server.get_fastapi_app()

        uvicorn.run(app, host=parsed_url.hostname, port=parsed_url.port)