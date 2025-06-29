from .similarity_engine import SimilarityEngine
from api.models import Job, Applicant, ApplicantJob

class MatchingService:
    @staticmethod
    def match_applicant_to_jobs(applicant_id):
        """
        Match one applicant to all active jobs
        """
        applicant = Applicant.objects.get(id=applicant_id)
        
        if not applicant.resumes.exists():
            return # No resumes to match

        latest_resume = applicant.resumes.latest('uploaded_at')
        applicant_skills = latest_resume.analysis.skills
        
        active_jobs = Job.objects.filter(is_active=True)
        
        for job in active_jobs:
            score = SimilarityEngine.calculate_similarity(
                job.requirements, 
                applicant_skills
            )
            
            ApplicantJob.objects.update_or_create(
                applicant=applicant,
                job=job,
                defaults={'similarity_score': score}
            )

    @staticmethod
    def match_job_to_applicants(job_id):
        """
        Match one job to all applicants
        """
        job = Job.objects.get(id=job_id)
        
        applicants_with_resumes = Applicant.objects.filter(resumes__isnull=False).distinct()

        for applicant in applicants_with_resumes:
            latest_resume = applicant.resumes.latest('uploaded_at')
            score = SimilarityEngine.calculate_similarity(
                job.requirements,
                latest_resume.analysis.skills
            )
            
            ApplicantJob.objects.update_or_create(
                applicant=applicant,
                job=job,
                defaults={'similarity_score': score}
            )