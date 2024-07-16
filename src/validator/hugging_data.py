
from typing import Dict, List, Any

from datasets import load_dataset


def get_certifications_dataset() -> Dict[str, str]:
    dataset = load_dataset("nakamoto-yama/certifications", split="train").to_dict()
    ids = dataset['id']
    classes = dataset['Class']
    skills_gained = dataset['Skills Gained']
    new_dataset = []
    for i in range(len(ids)):
        new_record = {
            'id': ids[i],
            'Class': classes[i],
            'Skills Gained': skills_gained[i]
        }
        new_dataset.append(new_record)
    return dataset


def get_job_title_mappings() -> Dict[str, str]:
    dataset = load_dataset("nakamoto-yama/jt-mappings", split="train").to_dict()
    return dataset


def get_degree_type_mappings() -> Dict[str, str]:
    dataset = load_dataset("nakamoto-yama/dt-mappings", split="train").to_dict()
    return dataset


def get_degree_majors() -> List[str]:
    dataset = load_dataset("nakamoto-yama/majors", split="train").to_dict()
    return dataset


def get_keyword_matrix() -> Dict[str, Dict[str, int]]:
    dataset = load_dataset("nakamoto-yama/keywords", split="train").to_dict()
    return dataset


def get_colleges() -> List[Dict[str, Any]]:
    dataset = load_dataset("nakamoto-yama/us-colleges-universities", split="train").to_dict()
    return dataset
