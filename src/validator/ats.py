import json
from datetime import datetime
from collections import defaultdict
from datasets import load_dataset
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
from fuzzywuzzy import fuzz
from resume_extract import ResumeExtractor, sample_resume_data

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
    def __init__(self, resume_data):
        self.resume_data = resume_data
        self.resume_extractor = ResumeExtractor(resume_data=self.resume_data)

    def score_education(self, job_education, resume_education):
        education_levels = ["High School", "Associate", "Bachelor", "Master", "Doctorate"]
        job_index = education_levels.index(job_education)
        score = 0
        for edu in resume_education:
            edu_index = education_levels.index(edu["degree_type"])
            if edu_index == job_index:
                score += 1
            elif edu_index == job_index + 1:
                score += 1.25
            elif edu_index == job_index - 1 or edu_index == job_index + 2:
                score += 0.25
        return score


    def score_experience(self, min_years_experience, resume_experience):
        score = 0
        for work in resume_experience:
            years_of_experience = self.resume_extractor.calculate_years(work["start_date"], work["end_date"])

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


    def score_skills(self, jd_skills, resume_skills):
        universal_skills = defaultdict(int)
        self.resume_extractor.process_skills(jd_skills, universal_skills)

        max_jd_score = sum(universal_skills.values())

        resume_skill_counts = defaultdict(int)
        self.resume_extractor.process_skills(resume_skills, resume_skill_counts)
        resume_score = sum(resume_skill_counts.values())

        if max_jd_score > 0:
            score_percentage = resume_score / max_jd_score
            if score_percentage >= 0.5:
                return resume_score
            else:
                return 0
        else:
            return 0

    def score_projects(self, projects):
        score = 0
        for project in projects:
            project_duration = self.resume_extractor.calculate_years(project["start_date"], project["end_date"])
            score += project_duration * 0.3
        return score

    def score_certifications(self, job_certifications, resume_certifications):
        score = 0
        if "certifications" in job_certifications:
            for cert in resume_certifications:
                if cert in job_certifications["certifications"]:
                    score += 1
        return score


    def calculate_ats_score(self, job_description):
        resume_data = self.resume_data
        education_score = self.score_education(job_description["education"], resume_data["education"])
        experience_score = self.score_experience(job_description["min_years_experience"], resume_data["work_experience"])
        skills_score = self.score_skills(job_description["skills"], resume_data["skills"])
        projects_score = self.score_projects(resume_data["projects"])
        certifications_score = self.score_certifications(job_description["certifications"], resume_data["certifications"])

        total_score = (education_score + experience_score + skills_score + projects_score + certifications_score)

        min_education_score = 1
        min_experience_score = 1
        min_skills_score = 1
        min_projects_score = 0.3
        min_certifications_score = 1
        min_overall_score = 3.5

        if (education_score >= min_education_score and
            experience_score >= min_experience_score and
            skills_score >= min_skills_score and
            projects_score >= min_projects_score and
            certifications_score >= min_certifications_score and
            total_score >= min_overall_score):
            result = "Yay, you're in!"
        else:
            result = "Sorry, you're out."

        return {
            "total_score": total_score,
            "education_score": education_score,
            "experience_score": experience_score,
            "skills_score": skills_score,
            "projects_score": projects_score,
            "certifications_score": certifications_score,
            "result": result
        }


if __name__ == '__main__':
    ats = ATS(resume_data=sample_resume_data)
    result = ats.calculate_ats_score(sample_job_description)
    print(json.dumps(result, indent=4))
