import random
import json
import re
from datetime import datetime, timedelta
from collections import Counter
from math import log
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from datasets import load_dataset
from miner.base_miner import BaseMiner

class DataLoader:
    """
    A class for loading and managing various datasets related to schools, majors,
    skills, and job titles.

    This class provides methods to load data from JSON files and external datasets,
    and stores the loaded data in a dictionary for use in Resume().

    Attributes:
        data (dict): A dictionary containing the loaded datasets:
            - 'schools': List of school names
            - 'majors': List of major names
            - 'skills': List of skills
            - 'job_title_data': Dataset containing job title information

    Methods:
        load_json_data(file_path): Load data from a JSON file
        load_school_names(file_path): Load school names from a JSON file
        load_majors(file_path): Load major names from a JSON file
        load_skills(): Load skills from an external dataset
        load_job_title_data(): Load job title data from an external dataset
    """
    def __init__(self):
        self.data = {
            'schools': self.load_school_names('src/miner/data/schools.json'),
            'majors': self.load_majors('src/miner/data/majors.json'),
            'skills': self.load_skills(),
            'job_title_data': self.load_job_title_data()
        }

    def load_json_data(self, file_path):
        """
        Load data from a JSON file

        Args:
            file_path (str): The path to the JSON file to be loaded.

        Returns:
            dict: The parsed JSON data as a Python dictionary.

        Raises:
            FileNotFoundError: If the specified file is not found.
            json.JSONDecodeError: If the file contains invalid JSON.
        """
        with open(file_path, 'r', encoding="utf-8") as file:
            return json.load(file)

    def load_school_names(self, file_path):
        """
        Load school names from a JSON file

        Args:
            file_path (str): The path to a JSON file with a school name
        """
        data = self.load_json_data(file_path)
        return [school["name"] for school in data["results"]]

    def load_majors(self, file_path):
        data = self.load_json_data(file_path)
        return [major["name"] for major in data["majors"]]

    def load_skills(self):
        skills_data = load_dataset("DrDominikDellermann/SkillsDataset")["train"]["skills"]
        return [item['skill'] for sublist in skills_data for item in sublist]

    def load_job_title_data(self):
        job_title_data = load_dataset("jacob-hugging-face/job-descriptions")
        return job_title_data

class RelevanceScorer:
    def __init__(self, data):
        self.stop_words = set(stopwords.words('english'))
        self.stemmer = PorterStemmer()
        self.data = data
        self.all_documents = (
            data['job_title_data']['train']['position_title'] +
            data['skills'] +
            data['majors']
        )
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
        job_title_scores = self.calculate_relevance(
            job_description,
            self.data['job_title_data']['train']['position_title']
        )
        skill_scores = self.calculate_relevance(
            job_description,
            self.data['skills']
        )
        major_scores = self.calculate_relevance(
            job_description,
            self.data['majors']
        )

        def normalize_scores(scores):
            max_score = max(scores.values()) if scores else 1
            if max_score == 0:
                return {k: 0 for k in scores}
            return {k: v / max_score for k, v in scores.items()}

        job_title_scores = normalize_scores(job_title_scores)
        skill_scores = normalize_scores(skill_scores)
        major_scores = normalize_scores(major_scores)

        top_job_titles = sorted(
            job_title_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )[:num_jobs]
        top_skills = sorted(
            skill_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )[:num_skills]
        top_major = sorted(major_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )[:num_majors]

        return {
            'job_titles': [(
                    self.data['job_title_data']['train']['position_title'].index(title),
                    title
                )
                for title, score in top_job_titles
            ],
            'skills': [skill for skill, score in top_skills],
            'major': [major for major, score in top_major]
        }

class Resume:
    def __init__(self, data):
        self.scorer = RelevanceScorer(data)
        self.data = data

    def get_scaled_periods(self, num_jobs, scale_factor):
        job_periods = [random.random() for _ in range(num_jobs)]
        sum_periods = sum(job_periods)
        return [x / sum_periods * scale_factor for x in job_periods]

    def get_job_info(self, job_index, data):
        company_name = data['job_title_data']['train']['company_name'][job_index]
        model_response = json.loads(data['job_title_data']['train']['model_response'][job_index])
        core_responsibilities = model_response.get(
            "Core Responsibilities",
            "No core responsibilities found"
        )
        return company_name, core_responsibilities

    def get_work_experience(self, relevant_job_titles, graduation_year):
        work_experience = []
        total_days = 365 * random.randint(5, datetime.now().year - graduation_year)

        normalized_periods = self.get_scaled_periods(
            len(relevant_job_titles),
            random.uniform(0.7, 1.0)
        )
        time_not_working = 1 - sum(normalized_periods)
        work_experience_coefficients = normalized_periods + [time_not_working]

        start_date = datetime.now() - timedelta(days=total_days)

        for index, (job_index, title) in enumerate(relevant_job_titles):
            job = {}
            job["title"] = title
            job["company_name"], job["summary"] = self.get_job_info(job_index, self.data)
            job["start_date"] = start_date.strftime('%m-%Y')
            job_duration_days = int(work_experience_coefficients[index] * total_days)
            job["end_date"] = (start_date + timedelta(days=job_duration_days)).strftime('%m-%Y')
            
            work_experience.append(job)

            gap_days = random.randint(0, int(work_experience_coefficients[-1] * total_days / 3))
            start_date = start_date + timedelta(days=job_duration_days) + timedelta(days=gap_days)

        return work_experience

    def get_education(self, major, graduation_year):
        education = []
        degree_type = "Bachelor's"
        school_name = random.choice(self.data["schools"])
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
    def __init__(self):
        super().__init__()
        self.data_loader = DataLoader()
        self.resume = Resume(self.data_loader.data)

    def generate_response(self, prompt: str):
        return self.resume.generate_resume(prompt)
