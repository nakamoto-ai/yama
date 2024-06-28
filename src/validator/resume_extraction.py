import json
from datetime import datetime
from collections import defaultdict
from datasets import load_dataset
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
from fuzzywuzzy import fuzz

# Example resume data
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

# Load the certifications dataset from Hugging Face
dataset = load_dataset("naganakamoto/certifications", split="train")

# Load the universities dataset from a JSON file
def load_universities(json_file):
    with open(json_file, 'r', encoding='utf-8') as f:
        universities = json.load(f)
    return universities

# Check if a university exists in the loaded dataset
def check_university_exists(university_name, universities):
    for uni in universities:
        if uni['name'].lower() == university_name.lower():
            return 1
    return 0

# Function to process skills
def process_skills(skills, universal_skills):
    for skill in skills:
        universal_skills[skill] += 1

# Initialize TF-IDF vectorizer
vectorizer = TfidfVectorizer()

# Fit and transform the dataset for vectorization
certifications = [cert["Class"] for cert in dataset]
X = vectorizer.fit_transform(certifications)

# Initialize KNN model
knn = NearestNeighbors(metric='cosine', algorithm='brute')
knn.fit(X)

# Load universities dataset
universities_json_file = "C:/Users/naga/Downloads/us-colleges-and-universities.json"
universities = load_universities(universities_json_file)

# Function to find nearest certifications with a distance threshold
def find_nearest_certifications(query, knn_model, vectorizer, certifications, threshold=0.5):
    query_vec = vectorizer.transform([query])
    distances, indices = knn_model.kneighbors(query_vec, n_neighbors=len(certifications))
    nearest_certs = [(certifications[idx], distances[0][i]) for i, idx in enumerate(indices[0])]
    nearest_certs = [(cert, dist) for cert, dist in nearest_certs if dist < threshold]

    # If no nearest certs within threshold, try fuzzy matching
    if not nearest_certs:
        best_cert = max(certifications, key=lambda cert: fuzz.ratio(query, cert))
        return [(best_cert, 0.0)]  # Assuming perfect match with ratio 100

    return nearest_certs

# Helper function to calculate the difference in years between two dates
def calculate_years(start_date, end_date):
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    return (end - start).days / 365.25

# Initialize dictionaries
universal_skills = defaultdict(int)
education_dict = defaultdict(lambda: {"exists": 0, "major": ""})
work_experience_dict = defaultdict(float)
workskills_dict = defaultdict(float)
certification_dict = {}
project_timelines = []

# Process skills
process_skills(resume_data["skills"], universal_skills)

# Process certifications
for cert in resume_data["certifications"]:
    nearest_certs = find_nearest_certifications(cert, knn, vectorizer, certifications, threshold=0.3)
    if nearest_certs:
        best_cert, _ = nearest_certs[0]
        matching_cert = dataset.filter(lambda x: x['Class'] == best_cert)
        if len(matching_cert) > 0:
            cert_info = matching_cert[0]
            skills_gained = cert_info['Skills Gained'].split(", ")
            certification_dict[best_cert] = skills_gained
            for skill in skills_gained:
                if skill:
                    universal_skills[skill] += 1
        else:
            certification_dict[best_cert] = []
            for skill in best_cert.split():
                universal_skills[skill] += 1
    else:
        certification_dict[cert] = []
        for skill in cert.split():
            universal_skills[skill] += 1

# Process education
for edu in resume_data["education"]:
    university_name = edu["school"]  # Fetch university name directly from the dict
    major = edu["major"]
    if check_university_exists(university_name, universities):
        education_dict[major]["exists"] = 1  # University exists
        education_dict[major]["major"] = major
    else:
        education_dict[major]["exists"] = 0  # University doesn't exist
        education_dict[major]["major"] = major


# Process work experience
for work in resume_data["work_experience"]:
    job_title = work["job_title"]
    years_of_experience = calculate_years(work["start_date"], work["end_date"])
    work_experience_dict[job_title] += years_of_experience

    # Extract skills from roles
    roles_skills = work["roles"].split()
    for skill in roles_skills:
        universal_skills[skill] += 1
        workskills_dict[skill] += years_of_experience

# Process projects
for project in resume_data["projects"]:
    project_duration = calculate_years(project["start_date"], project["end_date"])
    project_timelines.append(project_duration)

# Output the results
result = {
    "universal_skills": dict(universal_skills),
    "education_dict": dict(education_dict),
    "work_experience_dict": dict(work_experience_dict),
    "workskills_dict": dict(workskills_dict),
    "project_timelines": project_timelines,
    "Certification Dictionary": certification_dict
}

# Print the final result
print("\nResult:")
print(json.dumps(result, indent=4))
