"""
Created by Bobby Miller

Script to normalize Degree Types, Majors and Job Titles for easier processing

Requirements:

numpy
scikit-learn
"""


from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from typing import Dict, List, Tuple


def get_job_title_mappings() -> Dict[str, str]:
    # TODO: API call that returns job_title mappings stored on huggingface
    return {'job_title': 'test_mapping'}


def get_degree_type_mappings() -> Dict[str, str]:
    # TODO: API call that returns degree_type mappings stored on huggingface
    return {'degree_type': 'test_mapping'}


def get_degree_majors() -> List[str]:
    # TODO: API call that returns list of majors stored on huggingface
    return ['test_major_1', 'test_major_2']


def find_best_match(title: str, mappings: Dict[str, str]) -> str:
    titles = list([k for k in mappings.keys()])
    vectorizer = TfidfVectorizer(stop_words='english')
    title_vec = vectorizer.fit_transform([title] + titles)
    cosine_similarities = cosine_similarity(title_vec[0:1], title_vec[1:]).flatten()
    best_match_index = np.argmax(cosine_similarities)
    best_match = titles[best_match_index]
    return best_match


def find_closest_major(major: str, degree_majors: List[str]) -> str:
    vectorizer = TfidfVectorizer(stop_words='english')
    title_vec = vectorizer.fit_transform([major] + degree_majors)
    cosine_similarities = cosine_similarity(title_vec[0:1], title_vec[1:]).flatten()
    best_match_index = np.argmax(cosine_similarities)
    closest_major = degree_majors[best_match_index]
    return closest_major


def get_normalized_job_title(title: str) -> str:
    job_mappings = get_job_title_mappings()
    best_match = find_best_match(title, job_mappings)
    normalized_job_title = job_mappings[best_match]
    return normalized_job_title


def get_normalized_degree_type(degree_type: str) -> str:
    degree_mappings = get_degree_type_mappings()
    best_match = find_best_match(degree_type, degree_mappings)
    normalized_degree_type = degree_mappings[best_match]
    return normalized_degree_type


def get_normalized_degree_major(degree_major: str) -> str:
    degree_majors = get_degree_majors()
    normalized_degree_major = find_closest_major(degree_major, degree_majors)
    return normalized_degree_major


def normalize_titles(job_titles: List[str], degrees: List[Dict[str, str]]) -> Tuple[List[str], List[Dict[str, str]]]:
    normalized_job_titles = []
    normalized_degrees = []
    for job_title in job_titles:
        normalized_job_title = get_normalized_job_title(job_title)
        normalized_job_titles.append(normalized_job_title)
    for degree in degrees:
        degree_type = degree['type']
        degree_major = degree['major']
        normalized_degree_type = get_normalized_degree_type(degree_type)
        normalized_degree_major = get_normalized_degree_major(degree_major)
        normalized_degree = {
            'type': normalized_degree_type,
            'major': normalized_degree_major
        }
        normalized_degrees.append(normalized_degree)
    return normalized_job_titles, normalized_degrees


if __name__ == '__main__':
    example_job_titles = ['Junior Web Developer', 'Backend Developer II', 'Sr. Software Engineer']
    example_degrees = [
        {
            'type': 'MS',
            'major': 'Information Systems',
            'school': 'The University of Iowa',
            'grad_date': 'December 2020'
        },
        {
            'type': 'Bachelor of Science',
            'major': 'Computer Science',
            'school': 'Mississippi State University',
            'grad_date': 'August 2016'
        }
    ]
    normal_jobs, normal_degrees = normalize_titles(example_job_titles, example_degrees)
    print(f"Normalized Job Titles: {normal_jobs}")
    for normal_degree in normal_degrees:
        print(f"Normalized Degrees: {normal_degree['type']}, {normal_degree['major']}")
