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

from .Resume_Analysis.resume_analysis import ResumeAnalysis


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

        # 3. If applicant exists/validated, create resume analysis using ResumeAnalysis Class
        # === Custom Analysis Logic ===
        # Dummy analysis logic: You can replace this with real resume parsing & scoring logic
        resume_score = 85  # e.g., parsed from content
        page_no = 2  # Simulated number of pages
        predicted_field = "Software Engineering"
        reco_field = "Data Science"
        skills = ["Python", "Django"]
        recommended_skills = ["Machine Learning", "REST APIs"]

        
        resume_analyzer = ResumeAnalysis()
        resume_analysis = resume_analyzer.get_resume_analysis(pdf_file)


        # 4. Create Analysis object
        analysis = Analysis.objects.create(
            resume_score=resume_score,
            page_no=page_no,
            predicted_field=predicted_field,
            reco_field=reco_field,
            skills=skills,
            recommended_skills=recommended_skills,
        )

        # 5. Create Resume object
        resume = Resume.objects.create(
            applicant=applicant,
            analysis=analysis,
            name=name,
            pdf_file=pdf_file,
        )

        resume_serializer = ResumeSerializer(resume)
        return Response(resume_serializer.data, status=status.HTTP_201_CREATED)


class ResumeAnalysisByApplicant(APIView):
    def get(self, request, applicant_id):
        try:
            applicant = Applicant.objects.get(id=applicant_id)
            latest_resume = applicant.resumes.latest('uploaded_at')
            serializer = ResumeSerializer(latest_resume)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Applicant.DoesNotExist:
            return Response({"error": "Applicant not found."}, status=status.HTTP_404_NOT_FOUND)
        except Resume.DoesNotExist:
            return Response({"error": "No resumes found for this applicant."}, status=status.HTTP_404_NOT_FOUND)
         