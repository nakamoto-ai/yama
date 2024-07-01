import json
from datetime import datetime
from collections import defaultdict
from datasets import load_dataset
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
from fuzzywuzzy import fuzz

job_description = {
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

resume_data = {
    "skills": [
        "Data Analysis",
        "Data Visualization",
        "Java"
    ],
    "certifications": [
        "Programming Fundamentals | Coursera",
        "Microsoft Certified: Azure Data Scientist Associate",
        "Certified ScrumMaster (CSM)"
    ],
    "work_experience": [
        {
            "job_title": "Theme park manager",
            "company": "Future Solutions",
            "start_date": "2021-02-28",
            "end_date": "2021-07-30",
            "roles": "Managed cloud infrastructure and optimized costs using AWS services."
        }
    ],
    "education": [
        {
            "school": "Harvard University",
            "major": "Computer Science",
            "degree": "Doctorate in Computer Science",
            "degree_type": "Doctorate",
            "start_date": "2010-11-30",
            "graduation_date": "2014-11-29"
        },
        {
            "school": "Nonexistent University",
            "major": "Physics",
            "degree": "Bachelor of Science",
            "degree_type": "Bachelor",
            "start_date": "2005-09-01",
            "graduation_date": "2009-06-30"
        }
    ],
    "projects": [
        {
            "name": "Face-to-face methodical archive",
            "roles": "Developed a machine learning model to predict customer churn, resulting in a 10% increase in retention.",
            "start_date": "2021-07-03",
            "end_date": "2023-11-13"
        },
        {
            "name": "Down-sized composite installation",
            "roles": "Created a real-time data visualization dashboard for tracking key business metrics.",
            "start_date": "2021-12-01",
            "end_date": "2023-02-05"
        }
    ]
}

dataset = load_dataset("naganakamoto/certifications", split="train")

def load_universities(json_file):
    with open(json_file, 'r', encoding='utf-8') as f:
        universities = json.load(f)
    return universities

def check_university_exists(university_name, universities):
    for uni in universities:
        if uni['name'].lower() == university_name.lower():
            return 1
    return 0

def process_skills(skills, universal_skills):
    for skill in skills:
        universal_skills[skill] += 1

vectorizer = TfidfVectorizer()

certifications = [cert["Class"] for cert in dataset]
X = vectorizer.fit_transform(certifications)

knn = NearestNeighbors(metric='cosine', algorithm='brute')
knn.fit(X)

universities_json_file = "C:/Users/naga/Downloads/us-colleges-and-universities.json"
universities = load_universities(universities_json_file)

def find_nearest_certifications(query, knn_model, vectorizer, certifications, threshold=0.5):
    query_vec = vectorizer.transform([query])
    distances, indices = knn_model.kneighbors(query_vec, n_neighbors=len(certifications))
    nearest_certs = [(certifications[idx], distances[0][i]) for i, idx in enumerate(indices[0])]
    nearest_certs = [(cert, dist) for cert, dist in nearest_certs if dist < threshold]

    if not nearest_certs:
        best_cert = max(certifications, key=lambda cert: fuzz.ratio(query, cert))
        return [(best_cert, 0.0)]

    return nearest_certs

def calculate_years(start_date, end_date):
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    return (end - start).days / 365.25

def score_education(job_education, resume_education):
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


def score_experience(min_years_experience, resume_experience):
    score = 0
    for work in resume_experience:
        years_of_experience = calculate_years(work["start_date"], work["end_date"])

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


def score_skills(jd_skills, resume_skills):
    universal_skills = defaultdict(int)
    process_skills(jd_skills, universal_skills)

    max_jd_score = sum(universal_skills.values())

    resume_skill_counts = defaultdict(int)
    process_skills(resume_skills, resume_skill_counts)
    resume_score = sum(resume_skill_counts.values())

    if max_jd_score > 0:
        score_percentage = resume_score / max_jd_score
        if score_percentage >= 0.5:
            return resume_score
        else:
            return 0
    else:
        return 0

def score_projects(projects):
    score = 0
    for project in projects:
        project_duration = calculate_years(project["start_date"], project["end_date"])
        score += project_duration * 0.3
    return score

def score_certifications(job_certifications, resume_certifications):
    score = 0
    if "certifications" in job_certifications:
        for cert in resume_certifications:
            if cert in job_certifications["certifications"]:
                score += 1
    return score


def calculate_ats_score(job_description, resume_data):
    education_score = score_education(job_description["education"], resume_data["education"])
    experience_score = score_experience(job_description["min_years_experience"], resume_data["work_experience"])
    skills_score = score_skills(job_description["skills"], resume_data["skills"])
    projects_score = score_projects(resume_data["projects"])
    certifications_score = score_certifications(job_description["certifications"], resume_data["certifications"])

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

result = calculate_ats_score(job_description, resume_data)
print(json.dumps(result, indent=4))
