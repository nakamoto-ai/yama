import pandas as pd
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from typing import Dict, Any
import numpy as np


class JobDescriptionExtractor:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
        self.nlp = spacy.load('en_core_web_trf')

    def extract_keywords(self, job_description: Dict[str, Any]) -> Dict[str, Any]:
        doc = self.nlp(job_description)

        ner_keywords = {
            'education': [ent.text for ent in doc.ents if ent.label_ in ['EDUCATION', 'ORG']],
            'skills': [ent.text for ent in doc.ents if ent.label_ in ['SKILL', 'LANGUAGE']],
            'experience': [ent.text for ent in doc.ents if ent.label_ in ['DATE', 'TIME']],
            'responsibilities': [ent.text for ent in doc.ents if ent.label_ in ['WORK_OF_ART', 'TASK']],
            'preferred_skills': [ent.text for ent in doc.ents if ent.label_ in ['FAC']]
        }

        return ner_keywords

    def extract_keywords_tfidf(self, job_description: Dict[str, Any]) -> list:
        tfidf_matrix = self.vectorizer.fit_transform([job_description])
        feature_names = self.vectorizer.get_feature_names_out()
        tfidf_scores = tfidf_matrix.toarray()[0]
        tfidf_keywords = [feature_names[i] for i in tfidf_scores.argsort()[-10:][::-1]]

        return tfidf_keywords

    def process_job_description(self, job_description):
        tfidf_keywords = self.extract_keywords_tfidf(job_description)
        ner_keywords = self.extract_keywords(job_description)

        return {
            'tfidf_keywords': tfidf_keywords,
            'ner_keywords': ner_keywords
        }


if __name__ == '__main__':
    job_description = """
    We are looking for a skilled Data Scientist who has a strong background in Python, machine learning, and data analysis. The ideal candidate should have a Bachelor's degree in Computer Science or a related field and at least 3 years of experience in a similar role. Responsibilities include analyzing large datasets, creating machine learning models, and presenting insights to stakeholders.
    """

    jd_extractor = JobDescriptionExtractor()
    processed_jd = jd_extractor.process_job_description(job_description)
    print("Processed Job Description:")
    print(processed_jd)
