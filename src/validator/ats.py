import json
from datetime import datetime
from collections import defaultdict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from sentence_transformers import SentenceTransformer, util
from resume_extract import ResumeExtractor, sample_resume_data
import pandas as pd
from typing import Dict, Any, List
from torch import Tensor
from hugging_data import get_degree_level_mappings, get_degree_type_mappings
from normalize import DataNormalize


sample_job_description = {
    "education": "Bachelor",
    "min_years_experience": 2,
    "skills": [
        "Data Analysis",
        "Python",
        "Machine Learning"
    ],
    "certifications": [
        "Certified ScrumMaster (CSM)",
        "AWS Certified Solutions Architect"
    ]
}


class ATS:
    def __init__(
        self,
        skills_df: pd.DataFrame,
        universal_skills_weights: Dict[str, Any],
        preferred_skills_weights: Dict[str, Any]
    ):
        self.resume_data = None
        self.resume_extractor = None
        self.skills_df = skills_df
        self.universal_skills_weights = universal_skills_weights
        self.preferred_skills_weights = preferred_skills_weights
        self.model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
        self.vectorizer = TfidfVectorizer()

    def store_resume(self, resume_data: Dict[str, Any]):
        self.resume_data = resume_data
        self.resume_extractor = ResumeExtractor(resume_data=self.resume_data)

    def score_education(self, job_education: List[str], resume_education: List[Dict[str, Any]]) -> float:
        dl_mappings = get_degree_level_mappings()
        highest_job_index = 0
        relevant_score = 0
        education_levels = ["High School", "Associate", "Bachelor", "Master", "Doctorate"]
        dn = DataNormalize()
        for job_edu in [dl_mappings[j] for j in job_education]:
            score = 0
            job_index = education_levels.index(job_edu)
            for edu in resume_education:
                degree_type = dl_mappings[dn.get_normalized_degree_type(edu['degree'])]
                edu_index = education_levels.index(degree_type)
                if edu_index == job_index:
                    score += 1
                elif edu_index == job_index + 1:
                    score += 1.25
                elif edu_index == job_index - 1 or edu_index == job_index + 2:
                    score += 0.25
            if job_index > highest_job_index:
                relevant_score = score
                highest_job_index = job_index
        return relevant_score

    def score_experience(self, min_years_experience: int, resume_experience: List[Dict[str, Any]]) -> float:
        score = 0
        for work in resume_experience:
            years_of_experience = self.calculate_years(work["start_date"], work["end_date"])

            if min_years_experience >= 8:
                if years_of_experience >= min_years_experience:
                    score += 1
                elif years_of_experience >= min_years_experience - 1:
                    score += 0.75
            else:
                if years_of_experience == min_years_experience:
                    score += 1
                elif years_of_experience == min_years_experience + 1:
                    score += 1.25
                elif min_years_experience < years_of_experience < min_years_experience + 3:
                    score += 1
                elif years_of_experience < min_years_experience:
                    score += 0.75
                elif years_of_experience > min_years_experience + 3:
                    score += 0.25

        return score

    def score_skills(self, jd_skills: List[str], resume_skills: List[str]) -> float:
        skills_df = self.skills_df
        universal_skills_weights = self.universal_skills_weights
        preferred_skills_weights = self.preferred_skills_weights
        universal_skills = defaultdict(int)
        universal_skills = self.resume_extractor.process_skills(jd_skills, universal_skills)

        max_jd_score = sum(universal_skills.values())

        resume_skill_counts = defaultdict(int)
        resume_skill_counts = self.resume_extractor.process_skills(resume_skills, resume_skill_counts)
        print(f"Resume Skill Counts: {resume_skill_counts}")
        resume_score = sum(resume_skill_counts.values())

        if max_jd_score > 0:
            score_percentage = resume_score / max_jd_score
            skill_score = score_percentage * resume_score
        else:
            skill_score = 0

        additional_score = 0
        if skills_df is not None and universal_skills_weights is not None and preferred_skills_weights is not None:
            # Calculate additional score based on weights
            for skill, weight in universal_skills_weights.items():
                print(f"Skill - {skill}, Weight - {weight}")
                if skill in resume_skill_counts:
                    additional_score += resume_skill_counts[skill] * weight

            for skill, weight in preferred_skills_weights.items():
                print(f"Skill - {skill}, Weight - {weight}")
                if skill in resume_skill_counts:
                    additional_score += resume_skill_counts[skill] * weight * 0.5

        print(f"Additional Score: {additional_score}")
        total_skills_score = skill_score + additional_score
        print(f"Total Skills Score: {total_skills_score}")

        return total_skills_score

    def score_projects(self, projects: List[Dict[str, Any]]) -> float:
        score = 0
        for project in projects:
            project_duration = self.calculate_years(project["start_date"], project["end_date"])
            score += project_duration * 0.3
        return score

    def score_certifications(self, job_certifications: Dict[str, Any], resume_certifications: List[str]) -> float:
        score = 0
        if "certifications" in job_certifications:
            for cert in resume_certifications:
                if cert in job_certifications["certifications"]:
                    score += 1
        return score

    def calculate_years(self, start_date: str, end_date: str) -> float:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        return (end - start).days / 365.25

    def get_sentence_embeddings(self, text: str) -> Tensor:
        return self.model.encode(text, convert_to_tensor=True)

    def check_semantic_sense(self, text: str) -> float:
        sentences = nltk.sent_tokenize(text)
        embeddings = self.get_sentence_embeddings(sentences)

        coherence_score = 0
        for i in range(1, len(embeddings)):
            coherence_score += util.pytorch_cos_sim(embeddings[i], embeddings[i-1]).item()

        average_coherence = coherence_score / (len(embeddings) - 1)
        return average_coherence

    def score_semantics(self, resume_text: str) -> int:
        semantic_score = self.check_semantic_sense(resume_text)
        if semantic_score < 0.5:
            return semantic_score
        elif 0.5 <= semantic_score < 0.75:
            return 1
        else:
            return 2

    def check_similarity(self, resume_text: str, job_description_text: str, threshold: float = 0.7) -> bool:
        self.vectorizer.fit([job_description_text, resume_text])
        jd_vector = self.vectorizer.transform([job_description_text])
        resume_vector = self.vectorizer.transform([resume_text])

        similarity = cosine_similarity(jd_vector, resume_vector)[0][0]

        if similarity >= threshold:
            return True
        return False

    def score_similarity(self, resume_text: str, job_description_text: str) -> int:
        return 1 if self.check_similarity(resume_text, job_description_text) else 0

    def reformat_job_description(self, job_description: Dict[str, Any]) -> Dict[str, Any]:
        reformatted_job_description = {}
        for k, v in job_description['ner_keywords'].items():
            reformatted_job_description[k] = v
        reformatted_job_description['skills'] += job_description['tfidf_keywords']
        return reformatted_job_description

    def calculate_ats_score(self, job_description: Dict[str, Any]) -> Dict[str, Any]:
        resume_data = None
        resume_data_list = [r for r in self.resume_data.values()]
        if len(resume_data_list) > 0:
            resume_data = resume_data_list[0]

        min_education_score = 1
        min_skills_score = 1
        min_projects_score = 0.3
        min_semantics_score = 1
        min_overall_score = 5.5
        min_similarity_score = 1

        if not resume_data or resume_data is None:
            education_score = 0
            skills_score = 0
            projects_score = 0
            semantics_score = 0
            similarity_score = 1
        else:
            reformatted_job_description = self.reformat_job_description(job_description)
            job_description = reformatted_job_description

            if 'education' in resume_data:
                education_score = self.score_education(job_description["education"], resume_data["education"])
            else:
                education_score = min_education_score

            if 'skills' in resume_data:
                skills_score = self.score_skills(job_description["skills"], resume_data["skills"])
            else:
                skills_score = min_skills_score

            if 'projects' in resume_data:
                projects_score = self.score_projects(resume_data["projects"])
            else:
                projects_score = min_projects_score

            if 'work_experience' in resume_data and 'skills' in resume_data:
                resume_text = ' '.join([work["title"] for work in resume_data["work_experience"]])
                semantics_score = self.score_semantics(resume_text)
                similarity_score = self.score_similarity(resume_text, ' '.join(job_description["skills"]))
            else:
                semantics_score = min_semantics_score
                similarity_score = min_similarity_score

        total_score = (education_score + skills_score + projects_score + semantics_score + similarity_score)

        # If similarity score is high, set total_score to 0
        if similarity_score == 1:
            total_score = 0

        if (education_score >= min_education_score and
                skills_score >= min_skills_score and
                projects_score >= min_projects_score and
                semantics_score >= min_semantics_score and
                similarity_score >= min_similarity_score and
                total_score >= min_overall_score):
            result = "Yay, you're in!"
        else:
            result = "Sorry, you're out."

        return {
            "total_score": total_score,
            "education_score": education_score,
            "skills_score": skills_score,
            "projects_score": projects_score,
            "semantics_score": semantics_score,
            "similarity_score": similarity_score,
            "result": result
        }


if __name__ == '__main__':
    ats = ATS(resume_data=sample_resume_data)
    result = ats.calculate_ats_score(sample_job_description)
    print(json.dumps)
