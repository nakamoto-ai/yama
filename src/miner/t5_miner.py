"""
Author: Miller
"""
import torch
from loguru import logger
from transformers import T5Tokenizer, T5ForConditionalGeneration
from miner.base_miner import BaseMiner

class T5Miner(BaseMiner):
    """
    T5Miner class for generating resume JSON from job descriptions using a fine-tuned T5 model.
    
    This class inherits from BaseMiner and implements the generate_response method
    using a T5 model fine-tuned for resume generation.
    """
    def __init__(self):
        super().__init__()
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = T5Tokenizer.from_pretrained("google-t5/t5-base")
        self.model = T5ForConditionalGeneration.from_pretrained(
            "nakamoto-yama/t5-resume-generation", 
            device_map=self.device
        )

    def generate_response(self, prompt: str):
        try:
            input_text = f"generate resume JSON for the following job: {prompt}"
            input_ids = self.tokenizer(input_text, return_tensors="pt").input_ids.to(self.device)
            outputs = self.model.generate(input_ids, max_length=512, num_return_sequences=1)
            result = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            result = result.replace("LB>", "{").replace("RB>", "}")
            return result
        except RuntimeError as e:
            if "CUDA out of memory" in str(e):
                logger.error("CUDA out of memory. Consider reducing batch size or model size.")
            else:
                logger.error(f"Runtime error during generation: {str(e)}")
            return f"Error: {str(e)}"
        except ValueError as e:
            logger.error(f"Value error during generation: {str(e)}")
            return f"Error: Invalid input - {str(e)}"
