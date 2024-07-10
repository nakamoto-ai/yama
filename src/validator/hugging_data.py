
from typing import Dict, List

from datasets import load_dataset


def get_certifications_dataset():
    dataset = load_dataset("nakamoto-yama/certifications", split="train")
    return dataset


def get_job_title_mappings() -> Dict[str, str]:
    dataset = load_dataset("nakamoto-yama/jt-mappings", split="train")
    return dataset


def get_degree_type_mappings() -> Dict[str, str]:
    dataset = load_dataset("nakamoto-yama/dt-mappings", split="train")
    return dataset


def get_degree_majors() -> List[str]:
    dataset = load_dataset("nakamoto-yama/majors", split="train")
    return dataset


def get_keyword_matrix(self) -> Dict[str, Dict[str, int]]:
    dataset = load_dataset("nakamoto-yama/keywords", split="train")
    return dataset
