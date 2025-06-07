from PyPDF2 import PdfReader
import re
import pickle
import os
from pyresparser import ResumeParser


# -------------------------------LOAD Trained Models------------------------------------
# Get the directory of the current file (Resume_Analysis/)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Paths to model and vectorizer inside models/
RF_MODEL_PATH = os.path.join(BASE_DIR, 'models', 'rf_classifier_categorization.pkl')
TFIDF_PATH = os.path.join(BASE_DIR, 'models', 'tfidf_vectorizer_categorization.pkl')

RF_MODEL_PATH_2 = os.path.join(BASE_DIR, 'models', 'rf_classifier_job_recommendation.pkl')
TFIDF_PATH_2 = os.path.join(BASE_DIR, 'models', 'tfidf_vectorizer_job_recommendation.pkl')

# JOB FIELD CATEGORIZATION: Load the classifier and vectorizer
with open(RF_MODEL_PATH, 'rb') as rf_file:
    rf_classifier_categorization = pickle.load(rf_file)

with open(TFIDF_PATH, 'rb') as tfidf_file:
    tfidf_vectorizer_categorization = pickle.load(tfidf_file)

#JOB FIELD RECOMENDATION
with open(RF_MODEL_PATH_2, 'rb') as rf_file:
    rf_classifier_job_recommendation = pickle.load(rf_file)

with open(TFIDF_PATH_2, 'rb') as tfidf_file:
    tfidf_vectorizer_job_recommendation  = pickle.load(tfidf_file)


    
#--------------------------------RESUME ANALYSIS-------------------------------------------
class ResumeAnalysis:

    def clean_resume(self, text):
        # Remove URLs starting with http (e.g., http://example.com)
        cleanText = re.sub(r'http/S+\s', ' ', text)

        # Remove common retweet and copy-paste tags (often seen in social media text)
        cleanText = re.sub(r'RT|cc', ' ', cleanText)

        # Remove hashtags and the word following them (e.g., #Python)
        cleanText = re.sub(r'#\S+\s', ' ', cleanText)

        # Remove mentions like @username
        cleanText = re.sub(r'@\S+', ' ', cleanText)

        # Remove punctuation and special characters using escaped characters
        cleanText = re.sub('[%s]' % re.escape(r"""!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"""), ' ', cleanText)

        # Remove non-ASCII characters (e.g., emojis, foreign scripts)
        cleanText = re.sub(r'[^\x00-\x7f]', ' ', cleanText)

        # Replace multiple spaces, tabs, and newlines with a single space
        cleanText = re.sub(r'\s+', ' ', cleanText)

        # Return the cleaned text
        return cleanText



    def pdf_to_text(self, pdf_file):
        reader = PdfReader(pdf_file)
        text = ''
        for page in range(len(reader.pages)):
            text += reader.pages[page].extract_text()
        return text
    

    def predict_field_category(self, cleaned_resume_text):
        resume_tfidf = tfidf_vectorizer_categorization.transform([cleaned_resume_text])
        predicted_field_category = rf_classifier_categorization.predict(resume_tfidf)[0]

        return predicted_field_category
    

    def recommend_job(self, cleaned_resume_text):
        resume_tfidf = tfidf_vectorizer_job_recommendation.transform([cleaned_resume_text])
        recommended_job = rf_classifier_job_recommendation.predict(resume_tfidf)[0]
        
        return recommended_job


    def get_resume_analysis(self, pdf_file):
        if(pdf_file):
            # 1. Convert resume pdf_file to text
            resume_text = self.pdf_to_text(pdf_file)

            # 2. Preprocess text; Remove unecessary patterns (punctuations, hashtags, urls/links, etc); Use REs
            cleaned_resume_text = self.clean_resume(resume_text)

            # 3. Predict Category/Field
            predicted_field_category = self.predict_field_category(cleaned_resume_text)

            # 4. Recommend Job Category/Field
            recommended_job = self.recommend_job(cleaned_resume_text)



    
