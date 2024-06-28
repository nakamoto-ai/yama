import pandas as pd
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
import spacy
from datasets import load_dataset

# Load spaCy transformer model
nlp = spacy.load('en_core_web_trf')

# Download NLTK resources (if not already downloaded)
nltk.download('punkt')

# Function to extract keywords using TF-IDF and spaCy NER
def extract_keywords_advanced(job_description, tfidf_vectorizer, feature_names):
    # TF-IDF
    tfidf_matrix = tfidf_vectorizer.transform([job_description])
    tfidf_scores = tfidf_matrix.toarray()[0]
    tfidf_keywords = [feature_names[i] for i in tfidf_scores.argsort()[-10:][::-1]]

    # NER
    doc = nlp(job_description)
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

# Load the dataset
dataset = load_dataset('naganakamoto/jobdescriptionsraw')
train_data = dataset['train']

# Convert to DataFrame
df_train = pd.DataFrame(train_data)

# Process only the first 5 job descriptions
df_sample = df_train.head(5).copy()

# Prepare TF-IDF Vectorizer
tfidf_vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
tfidf_vectorizer.fit(df_train['description'])
feature_names = tfidf_vectorizer.get_feature_names_out()

# Apply advanced keyword extraction function to each job description in the sample
df_sample['keywords'] = df_sample['description'].apply(lambda x: extract_keywords_advanced(x, tfidf_vectorizer, feature_names))

# Print the updated DataFrame with extracted keywords
print(df_sample)

# Print the keywords for each job description
for index, row in df_sample.iterrows():
    print(f"Job Description {index + 1}:")
    print(f"TF-IDF Keywords: {row['keywords']['tfidf_keywords']}")
    print(f"NER Education Keywords: {row['keywords']['ner_keywords']['education']}")
    print(f"NER Skills Keywords: {row['keywords']['ner_keywords']['skills']}")
    print(f"NER Experience Keywords: {row['keywords']['ner_keywords']['experience']}")
    print(f"NER Responsibilities Keywords: {row['keywords']['ner_keywords']['responsibilities']}")
    print(f"NER Preferred Skills Keywords: {row['keywords']['ner_keywords']['preferred_skills']}")
    print("\n")
