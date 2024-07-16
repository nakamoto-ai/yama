import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import spacy
from typing import Dict, Any, List


class JobDescriptionParser:
    def __init__(self):
        self.nlp = spacy.load('en_core_web_trf')
        self.load_vectorizer()

    def load_vectorizer(self):
        self.vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)

    def extract_keywords_advanced(
        self,
        job_description: Dict[str, Any],
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

    def get_skills_dataframe(self, job_description: Dict[str, Any]) -> pd.DataFrame:
        train_data = [{'description': job_description}]
        df = pd.DataFrame(train_data)

        self.vectorizer.fit(df['description'])

        feature_names = self.vectorizer.get_feature_names_out()

        df['keywords'] = df['description'].apply(
            lambda x: self.extract_keywords_advanced(x, feature_names))

        return df

    def get_formatted_jd(self, df: pd.DataFrame) -> Dict[str, Any]:
        skills_df = df
        formatted_jd = skills_df['keywords'].iloc[0]
        return formatted_jd

    def __str__(self) -> str:
        skills_dict = self.get_skills_dataframe().to_dict(orient='records')
        return str(skills_dict)


if __name__ == '__main__':
    jd = JobDescriptionParser()
    print(f"Skills: {jd.get_formatted_jd()}")
