from django.shortcuts import render
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser

from django.db.models import Q
from datetime import datetime

from api.models import Applicant, Resume, Analysis
from api.serializers import ApplicantSerializer, ResumeSerializer, AnalysisSerializer

# RESUME INFORMATION EXTRACTOR
from .Resume_Analysis.resume_info_extraction import ResumeInformationExtraction

#RESUME JOB CATEGORY PREDICTIONS AND RECOMMENDATIONS
from .Resume_Analysis.resume_classifier import ResumeClassifier

#RESUME ANALYSIS
from .Resume_Analysis.resume_analysis import ResumeAnalysis

from .Job_Matching.matching_service import MatchingService


class ApplicantList(APIView):

    def get(self, request):
        applicants = Applicant.objects.all()
        serializer = ApplicantSerializer(applicants, many=True)
        return Response(serializer.data)


class ResumeUpload(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, format=None):
        #1. Extract data
        applicant_id = request.data.get('applicant')
        name = request.data.get('name')
        pdf_file = request.data.get('pdf_file')

        # 2. Check if applicant exists then get Aplicant object; Validate applicant
        try:
            applicant = Applicant.objects.get(id=applicant_id)
        except Applicant.DoesNotExist:
            return Response({"error": "Applicant not found."}, status=status.HTTP_404_NOT_FOUND)

       
        # 3. Create Resume object without analysis
        resume = Resume.objects.create(
            applicant=applicant,
            name=name,
            pdf_file=pdf_file,
        )

        # 4. Resume Information Extractioh and Resume Classifier
        resume_info_extractor = ResumeInformationExtraction()
        resume_classifier = ResumeClassifier()
        resume_path = resume.pdf_file.path

        extracted_from_resume = resume_info_extractor.parse_resume(resume_path)
        top3_predicted_job_categories, top3_job_recommendations = resume_classifier.get_top3_job_prediction_and_recommendation(resume_path)


        # 5. Create Analysis object
        analysis = Analysis.objects.create(
            name = extracted_from_resume['name'] ,
            email = extracted_from_resume['email'],
            mobile_number = extracted_from_resume['mobile_number'],
            years_of_experience = extracted_from_resume['total_experience'],
            experience_level = extracted_from_resume['experience_level'],
            experience_description = extracted_from_resume['experience_description'],
            experience_range = extracted_from_resume['experience_range'],
            skills = extracted_from_resume['skills'],
            educational_institutions = extracted_from_resume['educational_institutions'],
            educational_attainment = extracted_from_resume['educational_attainment'],
            no_of_pages = extracted_from_resume['no_of_pages'],
            predicted_job_categories = top3_predicted_job_categories,
            recommended_jobs = top3_job_recommendations,
        )

        # 6. Update resume with the newly created analysis
        resume.analysis = analysis
        resume.save()

        # 7. Serialize and return
        resume_serializer = ResumeSerializer(resume)
        return Response(resume_serializer.data, status=status.HTTP_201_CREATED)


class ResumeAnalysisByApplicant(APIView):
    def get(self, request, applicant_id):
        try:
            applicant = Applicant.objects.get(id=applicant_id)
            latest_resume = applicant.resumes.latest('uploaded_at')
            resume_pdf = latest_resume.pdf_file.path

            resume_analyzer = ResumeAnalysis()
            analysis = resume_analyzer.analyze_resume(resume_pdf)

            return Response(analysis, status=status.HTTP_200_OK)
        except Applicant.DoesNotExist:
            return Response({"error": "Applicant not found."}, status=status.HTTP_404_NOT_FOUND)
        except Resume.DoesNotExist:
            return Response({"error": "No resumes found for this applicant."}, status=status.HTTP_404_NOT_FOUND)
         
         
### maria's code ###

class ApplicantJobMatches(APIView):
    """
    Get all jobs matched to an applicant with scores
    """
    def get(self, request, applicant_id):
        matches = ApplicantJob.objects.filter(applicant_id=applicant_id)\
                     .order_by('-similarity_score')
        serializer = ApplicantJobSerializer(matches, many=True)
        return Response(serializer.data)

class JobApplicantMatches(APIView):
    """
    Get all applicants matched to a job with scores
    """
    def get(self, request, job_id):
        matches = ApplicantJob.objects.filter(job_id=job_id)\
                     .order_by('-similarity_score')
        serializer = ApplicantJobSerializer(matches, many=True)
        return Response(serializer.data)

class UpdateMatchesForJob(APIView):
    """
    Recalculate matches for a single job
    """
    def post(self, request, job_id):
        MatchingService.match_job_to_applicants(job_id)
        return Response({"status": "success"}, status=200)