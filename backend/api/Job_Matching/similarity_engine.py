from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class SimilarityEngine:
    @staticmethod
    def calculate_similarity(job_requirements, applicant_skills):
        """
        Calculate similarity between job requirements and applicant skills
        Returns: Float between 0 and 1
        """
        # Convert to strings for TF-IDF
        job_text = ' '.join(job_requirements) if isinstance(job_requirements, list) else job_requirements
        applicant_text = ' '.join(applicant_skills) if isinstance(applicant_skills, list) else applicant_skills
        
        vectorizer = TfidfVectorizer()
        vectors = vectorizer.fit_transform([job_text, applicant_text])
        similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
        
        return float(similarity)