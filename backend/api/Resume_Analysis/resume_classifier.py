from PyPDF2 import PdfReader
from pdfminer.high_level import extract_text
import re
import pickle
import os


# -------------------------------LOAD Trained Models------------------------------------
# Get the directory of the current file (Resume_Analysis/)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Paths to model classifier and vectorizer
RF_MODEL_PATH = os.path.join(BASE_DIR, 'models', 'rf_classifier_categorization.pkl')
TFIDF_PATH = os.path.join(BASE_DIR, 'models', 'tfidf_vectorizer_categorization.pkl')

RF_MODEL_PATH_2 = os.path.join(BASE_DIR, 'models', 'rf_classifier_job_recommendation.pkl')
TFIDF_PATH_2 = os.path.join(BASE_DIR, 'models', 'tfidf_vectorizer_job_recommendation.pkl')

#-------------JOB FIELD CATEGORIZATION: Load the classifier and vectorizer-----------------
with open(RF_MODEL_PATH, 'rb') as rf_file:
    rf_classifier_categorization = pickle.load(rf_file)

with open(TFIDF_PATH, 'rb') as tfidf_file:
    tfidf_vectorizer_categorization = pickle.load(tfidf_file)

#----------------JOB FIELD RECOMENDATION--------------------------------------------------
with open(RF_MODEL_PATH_2, 'rb') as rf_file:
    rf_classifier_job_recommendation = pickle.load(rf_file)

with open(TFIDF_PATH_2, 'rb') as tfidf_file:
    tfidf_vectorizer_job_recommendation  = pickle.load(tfidf_file)


    
#--------------------------------RESUME ANALYSIS-------------------------------------------
class ResumeClassifier:
    # 1. EXTRACT TEXT FROM RESUME
    def pdf_to_text(self, pdf_file):
        # reader = PdfReader(pdf_file)
        # text = ''
        # for page in range(len(reader.pages)):
        #     text += reader.pages[page].extract_text()
        # return text
        try:
            return extract_text(pdf_file)
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
            return ""
        
    # 2. PREPROCESS RESUME
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


    # 3. GET JOB CATEGORY/FIELD PREDICTION
    def predict_field_category(self, cleaned_resume_text):
        resume_tfidf = tfidf_vectorizer_categorization.transform([cleaned_resume_text])
        predicted_field_category = rf_classifier_categorization.predict(resume_tfidf)[0]

        return predicted_field_category
    
    # 4. GET JOB RECOMMENDATION
    def recommend_job(self, cleaned_resume_text):
        resume_tfidf = tfidf_vectorizer_job_recommendation.transform([cleaned_resume_text])
        recommended_job = rf_classifier_job_recommendation.predict(resume_tfidf)[0]
        
        return recommended_job

    # ---------------MAIN METHOD------------------------------------------
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

            return predicted_field_category, recommended_job
        

#---------------TOP 3 PREDICTIONS FROM CLASSIFICATION -----------------
    # 3. GET TOP 3 JOB CATEGORY/FIELD PREDICTIONS
    def predict_top3_field_categories(self, cleaned_resume_text):
        resume_tfidf = tfidf_vectorizer_categorization.transform([cleaned_resume_text])
        
        # Get probability scores for all classes
        probabilities = rf_classifier_categorization.predict_proba(resume_tfidf)[0]
        
        # Get class labels
        class_labels = rf_classifier_categorization.classes_
        
        # Create list of (category, probability) tuples
        category_probs = list(zip(class_labels, probabilities))
        
        # Sort by probability in descending order and get top 3
        top3_categories = sorted(category_probs, key=lambda x: x[1], reverse=True)[:3]
        
        return top3_categories

    # 4. GET TOP 3 JOB RECOMMENDATIONS
    def recommend_top3_jobs(self, cleaned_resume_text):
        resume_tfidf = tfidf_vectorizer_job_recommendation.transform([cleaned_resume_text])
        
        # Get probability scores for all classes
        probabilities = rf_classifier_job_recommendation.predict_proba(resume_tfidf)[0]
        
        # Get class labels
        class_labels = rf_classifier_job_recommendation.classes_
        
        # Create list of (job, probability) tuples
        job_probs = list(zip(class_labels, probabilities)) 
        
        # Sort by probability in descending order and get top 3
        top3_jobs = sorted(job_probs, key=lambda x: x[1], reverse=True)[:3]
        
        return top3_jobs
    
    # 5. MAIN METHOD TO GET TOP 3 PREDICTIONS
    def get_top3_job_prediction_and_recommendation(self, pdf_file):
        if(pdf_file):
            # 1. Convert resume pdf_file to text
            resume_text = self.pdf_to_text(pdf_file)

            # 2. Preprocess text; Remove unnecessary patterns
            cleaned_resume_text = self.clean_resume(resume_text)

            # 3. Get Top 3 Category/Field Predictions
            top3_field_categories = self.predict_top3_field_categories(cleaned_resume_text)

            # 4. Get Top 3 Job Recommendations
            top3_job_recommendations = self.recommend_top3_jobs(cleaned_resume_text)

            return top3_field_categories, top3_job_recommendations

        
# # PDF Resume
# resume = r'C:\Users\rochefym\Documents\Finals_NLPforJobApp\backend\media\pdfs\android-developer-1559034496.pdf'
# resume_classifier = ResumeClassifier()


# # Get top 3 results
# top3_categories, top3_jobs = resume_classifier.get_resume_analysis_top3(resume)
# print("TOP 3 JOB CATEGORIES:")
# for i, (category, probability) in enumerate(top3_categories, 1):
#     print(f"{i}. {category}: {probability:.4f} ({probability*100:.2f}%)")
# print("\nTOP 3 JOB RECOMMENDATIONS:")
# for i, (job, probability) in enumerate(top3_jobs, 1):
#     print(f"{i}. {job}: {probability:.4f} ({probability*100:.2f}%)")



# # Original single prediction (for comparison)
# predicted_field_category, recommended_job =  resume_classifier.get_resume_analysis(resume)
# print(f"""
# PREDICTED JOB CATEGORY: {predicted_field_category}
# JOB RECOMMENDATION: {recommended_job}
# """)



    
