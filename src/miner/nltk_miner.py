import random
import json
from base_miner import BaseMiner
from datetime import datetime, timedelta
from collections import Counter
from math import log

from substrateinterface import Keypair

from communex.client import CommuneClient

from faker import Faker
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from datasets import load_dataset

class DataLoader:
    def __init__(self):
        self.schools = self.load_school_names('data/schools.json')
        self.majors = [major["name"] for major in self.load_json_data('data/majors.json')["majors"]]
        self.skills = self.load_skills_data()
        self.job_titles = self.load_job_title_data()

    def load_json_data(self, file_path):
        with open(file_path, 'r') as file:
            return json.load(file)

    def load_school_names(self, file_path):
        data = self.load_json_data(file_path)
        return [school["name"] for school in data["results"]]

    def load_skills_data(self):
        skills_data = load_dataset("DrDominikDellermann/SkillsDataset")["train"]["skills"]
        return [item['skill'] for sublist in skills_data for item in sublist]

    def load_job_title_data(self):
        job_title_data = load_dataset("jacob-hugging-face/job-descriptions")
        return job_title_data["train"]["position_title"]

class RelevanceScorer:
    def __init__(self, job_titles, skills, majors):
        self.stop_words = set(stopwords.words('english'))
        self.stemmer = PorterStemmer()
        self.job_titles = job_titles
        self.skills = skills
        self.majors = majors
        self.all_documents = job_titles + skills + majors
        self.idf = self._calculate_idf(self.all_documents)

    def preprocess(self, text):
        words = re.findall(r'\w+', text.lower())
        return [self.stemmer.stem(word) for word in words if word not in self.stop_words]
    
    def _calculate_idf(self, documents):
        num_docs = len(documents)
        word_in_docs = Counter()
        for doc in documents:
            word_in_docs.update(set(self.preprocess(doc)))
        return {word: log(num_docs / (count + 1)) for word, count in word_in_docs.items()}
    
    def calculate_relevance(self, text, documents):
        text_words = self.preprocess(text)
        text_word_count = Counter(text_words)
        scores = {}
        for doc in documents:
            doc_words = self.preprocess(doc)
            score = sum(text_word_count[word] * self.idf.get(word, 0) for word in doc_words)
            scores[doc] = score
        return scores

    def find_relevant_matches(self, job_description, num_jobs=3, num_skills=5, num_majors=1):
        job_title_scores = self.calculate_relevance(job_description, self.job_titles)
        skill_scores = self.calculate_relevance(job_description, self.skills)
        major_scores = self.calculate_relevance(job_description, self.majors)

        def normalize_scores(scores):
            max_score = max(scores.values()) if scores else 1
            return {k: v / max_score for k, v in scores.items()}

        job_title_scores = normalize_scores(job_title_scores)
        skill_scores = normalize_scores(skill_scores)
        major_scores = normalize_scores(major_scores)

        top_job_titles = sorted(job_title_scores.items(), key=lambda x: x[1], reverse=True)[:num_jobs]
        top_skills = sorted(skill_scores.items(), key=lambda x: x[1], reverse=True)[:num_skills]
        top_major = sorted(major_scores.items(), key=lambda x: x[1], reverse=True)[:num_majors]

        return {
            'job_titles': [(self.job_titles.index(title), title) for title, score in top_job_titles],
            'skills': [skill for skill, score in top_skills],
            'major': [major for major, score in top_major]
        }

class Resume:
    def __init__(self, job_titles, skills, majors):
        self.data_loader = DataLoader()
        self.scorer = RelevanceScorer(job_titles, skills, majors)
        self.faker = Faker()

    def get_work_experience(self, job_titles, graduation_year):
        work_experience = []
        current_year = datetime.now().year
        years_working = random.randint(5, current_year - graduation_year)
        total_days = 365 * years_working
        
        job_periods = [random.random() for _ in range(len(job_titles))]
        sum_periods = sum(job_periods)
        scale_factor = random.uniform(0.7, 1.0)
        normalized_periods = [x / sum_periods * scale_factor for x in job_periods]
        time_not_working = 1 - sum(normalized_periods)

        work_experience_coefficients = normalized_periods + [time_not_working]

        career_start = datetime.now() - timedelta(days=365 * years_working)
        start_date = career_start

        for index, (job_index, title) in enumerate(job_titles):
            company_name = self.job_title_data["train"]["company_name"][job_index]
            model_response = json.loads(self.job_title_data["train"]["model_response"][job_index])
            core_responsibilities = model_response.get("Core Responsibilities", "No core responsibilities found")

            job_duration_days = int(work_experience_coefficients[index] * total_days)

            end_date = start_date + timedelta(days=job_duration_days)
            job = {
                "job_title": title,
                "company": company_name,
                "start_date": start_date.strftime('%m-%Y'),
                "end_date": end_date.strftime('%m-%Y'),
                "summary": core_responsibilities
            }
            work_experience.append(job)
            gap_days = random.randint(0, int(work_experience_coefficients[-1] * total_days / 3))
            start_date = end_date + timedelta(days=gap_days)
        
        return work_experience

    def get_education(self, major, graduation_year):
        education = []
        degree_type = "Bachelor's"
        school_name = random.choice(self.schools)
        degree = {
            "school": school_name,
            "major": major,
            "degree": degree_type,
            "graduation_date": graduation_year
        }
        education.append(degree)
        return education

    def generate_resume(self, job_description):
        results = self.scorer.find_relevant_matches(job_description)
        relevant_job_titles = results['job_titles']
        relevant_skills = results['skills']
        relevant_major = results['major'][0] if results['major'] else "No major found"
        graduation_year = random.randint(2008, 2018)

        resume = {
            "skills": relevant_skills,
            "work_experience": self.get_work_experience(relevant_job_titles, graduation_year),
            "education": self.get_education(relevant_major, graduation_year),
            "certifications": [],
            "projects": []
        }
        return resume

class NltkMiner(BaseMiner):
    def __init__(self, key: Keypair, client: CommuneClient):
        super().__init__(key=key, client=client)

    def generate_response(self, prompt: str):
        self.resume_generator = Resume(job_title_data, skill_list, majors_data)
        return self.resume_generator.generate_resume(prompt)
