import time
from abc import abstractmethod
from typing import Dict, Any
from loguru import logger
from communex.module import Module, endpoint

class BaseMiner(Module):

    @endpoint
    def generate(self, prompt: str) -> Dict[str, Any]:
        start_time = time.time()
        logger.info(f"Generating resume... ")

        logger.info(f"Job Description: {prompt}")

        resume = self.generate_response(prompt)

        logger.info(f"Generated Resume: {resume}")

        end_time = time.time()
        execution_time = end_time - start_time
        logger.info(f"Responded in {execution_time} seconds")

        return {"answer": resume}

    @abstractmethod
    def generate_response(self, prompt: str):
        pass
