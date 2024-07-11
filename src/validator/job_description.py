import pandas as pd
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
import spacy
from hugging_data import insert_name_of_jd_api_getter_here
from typing import Dict, Any, List


class JobDescriptionParser:
    def __init__(self):
        self.job_description = insert_name_of_jd_api_getter_here()
        self.nlp = spacy.load('en_core_web_trf')
        self.train_data = [{'description': self.job_description}]
        self.df = pd.DataFrame(self.train_data)
        self.vectorizer = self.load_vectorizer()

    def load_vectorizer(self) -> TfidfVectorizer:
        tfidf_vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
        return tfidf_vectorizer

    def extract_keywords_advanced(
        self,
        job_description: str,
        feature_names: List[str]
    ) -> Dict[str, Any]:
        # TF-IDF
        tfidf_matrix = self.vectorizer.transform([job_description])
        tfidf_scores = tfidf_matrix.toarray()[0]
        tfidf_keywords = [feature_names[i] for i in tfidf_scores.argsort()[-10:][::-1]]

        # NER
        doc = self.nlp(job_description)
        ner_keywords = {
            'education': [ent.text for ent in doc.ents if ent.label_ in ['EDUCATION', 'ORG']],
            'skills': [ent.text for ent in doc.ents if ent.label_ in ['SKILL', 'LANGUAGE']],
            'experience': [ent.text for ent in doc.ents if ent.label_ in ['DATE', 'TIME']],
            'responsibilities': [ent.text for ent in doc.ents if ent.label_ in ['WORK_OF_ART', 'TASK']],
            'preferred_skills': [ent.text for ent in doc.ents if ent.label_ in ['FAC']]
        }

        return {
            'tfidf_keywords': tfidf_keywords,
            'ner_keywords': ner_keywords
        }

    def get_skills_dataframe(self) -> pd.DataFrame:
        self.vectorizer.fit(self.df['description'])
        feature_names = self.vectorizer.get_feature_names_out()
        self.df['keywords'] = self.df['description'].apply(
            lambda x: self.extract_keywords_advanced(x, feature_names))
        return self.df

    def get_formatted_jd(self) -> Dict[str, Any]:
        skills_df = self.get_skills_dataframe()
        formatted_jd = skills_df['keywords'].iloc[0]
        return formatted_jd

    def __str__(self) -> str:
        skills_dict = self.get_skills_dataframe().to_dict(orient='records')
        return str(skills_dict)


if __name__ == '__main__':
    jd = JobDescriptionParser()
    print(f"Skills: {jd.get_formatted_jd()}")
