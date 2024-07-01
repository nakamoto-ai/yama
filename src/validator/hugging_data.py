
import pandas as pd
from typing import Dict, List

from datasets import load_dataset


def get_validator_dataset():
    # TODO: API call to get this dataset
    dataset = load_dataset('naganakamoto/jobdescriptionsraw')
    train_data = dataset['train']
    return train_data

def get_certifications_dataset():
    # TODO: API call to get this dataset
    dataset = load_dataset("naganakamoto/certifications", split="train")
    return dataset

def get_job_title_mappings() -> Dict[str, str]:
    # TODO: API Call that returns job_title mappings stored on huggingface
    return {'job_title': 'mapping'}

def get_degree_type_mappings() -> Dict[str, str]:
    # TODO: API Call that returns degree_type mappings stored on huggingface
    return {'degree_type': 'mapping'}

def get_degree_majors() -> List[str]:
    # TODO: API Call that returns list of majors stored on huggingface
    return ['test_major_1', 'test_major_2']

def get_keyword_matrix(self) -> Dict[str, Dict[str, int]]:
    # TODO: API call to get keyword matrix from huggingface, also will combine all api calls into one class
    keyword_matrix: Dict[str, Dict[str, int]] = {}
    return keyword_matrix
