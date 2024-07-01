
import pandas as pd

from collections import defaultdict
from hugging_data import get_keyword_matrix
from typing import List, Dict


class JDKeywordMatrix:
    def __init__(self):
        self.keyword_matrix = get_keyword_matrix()
        self.occurrence_threshold = 0.5

    def get_normalized_keyword_matrix(self):
        occurrence_threshold = self.occurrence_threshold
        normal_keyword_matrix = {}
        abnormal_keyword_matrix = get_keyword_matrix()
        for keyword, occurrences in abnormal_keyword_matrix.items():
            concurrent_keys = occurrences.keys()
            num_occurs = occurrences.values()
            normal_occurs = self.normalize_keyword_occurrences(num_occurs)
            new_occurrences = {}
            for i, occur in enumerate(normal_occurs):
                if occur >= occurrence_threshold:
                    new_occurrences[concurrent_keys[i]] = occur
            normal_keyword_matrix[keyword] = new_occurrences
        return normal_keyword_matrix

    def get_keyword_scores_for_skills(self, skills: List[str]) -> Dict[str, float]:
        occurrence_threshold = self.occurrence_threshold
        keyword_scores = defaultdict(float)
        keyword_matrix = self.get_normalized_keyword_matrix(occurrence_threshold)
        skills = [s.lower() for s in set(skills)]

        for skill in skills:
            keyword_scores[skill] += 1
            if skill in keyword_matrix:
                for concur_keyword, occur_score in keyword_matrix[skill]:
                    keyword_scores[concur_keyword] += occur_score
            # TODO: possibly use knn/similarity to get 'best match' to skill if not directly found in matrix

        return dict(keyword_scores)

    def normalize_keyword_occurrences(self, values):
        min_val = min(values)
        max_val = max(values)
        range_val = max_val - min_val
        if range_val == 0:
            return [0.5] * len(values)
        normalized = [(x - min_val) / range_val for x in values]
        return normalized
