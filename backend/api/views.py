from django.shortcuts import render
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView

from django.db.models import Q
from datetime import datetime

from api.models import Applicant, Resume, Analysis, Employer, Job, Applicant_Job
from api.serializers import ApplicantSerializer, ResumeSerializer, AnalysisSerializer, EmployerSerializer, JobSerializer, ApplicantJobSerializer, LoginSerializer
from django.contrib.auth.hashers import make_password, check_password # Import check_password
from django.contrib.auth import authenticate # For more robust authentication if using Django's auth system

# For token authentication (simple example, consider DRF's built-in or a library like Simple JWT for production)
from rest_framework_simplejwt.tokens import RefreshToken # Using Simple JWT as an example

# RESUME INFORMATION EXTRACTOR
from .Resume_Analysis.resume_info_extraction import ResumeInformationExtraction

#RESUME JOB CATEGORY PREDICTIONS AND RECOMMENDATIONS
from .Resume_Analysis.resume_classifier import ResumeClassifier

#RESUME ANALYSIS
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

# --- Job List with Filtering/Search ---
class JobListView(ListAPIView):
    serializer_class = JobSerializer

    def get_queryset(self):
        queryset = Job.objects.filter(is_active=True)
        search = self.request.query_params.get('search')
        location = self.request.query_params.get('location')
        job_type = self.request.query_params.get('job_type')
        company = self.request.query_params.get('company')
        if search:
            queryset = queryset.filter(Q(job_title__icontains=search) | Q(job_description__icontains=search) | Q(employer__company_name__icontains=search))
        if location:
            queryset = queryset.filter(location__icontains=location)
        if job_type:
            queryset = queryset.filter(work_type__iexact=job_type)
        if company:
            queryset = queryset.filter(employer__company_name__icontains=company)
        return queryset

# --- Job Detail ---
class JobDetailView(RetrieveAPIView):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    lookup_field = 'id'

# --- Job/Company/Support Counts ---
class JobStatsView(APIView):
    def get(self, request):
        jobs_count = Job.objects.filter(is_active=True).count()
        companies_count = Employer.objects.count()
        support = '24/7'
        return Response({
            'jobs_available': jobs_count,
            'companies_hiring': companies_count,
            'support_available': support
        })

# --- Apply to Job (with Resume Upload) ---
class ApplyToJobView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    def post(self, request, job_id):
        # Required fields
        name = request.data.get('name')
        email = request.data.get('email')
        phone_number = request.data.get('phone_number')
        start_date = request.data.get('start_date')
        resume_file = request.data.get('resume_file')
        years_of_experience = request.data.get('years_of_experience')
        expected_salary = request.data.get('expected_salary')
        cover_letter = request.data.get('cover_letter')
        # Find job
        try:
            job = Job.objects.get(id=job_id)
        except Job.DoesNotExist:
            return Response({'error': 'Job not found.'}, status=404)
        # Create applicant (or get by email)
        applicant, _ = Applicant.objects.get_or_create(email=email, defaults={
            'name': name,
            'phone_number': phone_number,
            'password': 'default',  # Set a default or random password
        })
        # Create resume
        resume = Resume.objects.create(
            applicant=applicant,
            name=name,
            pdf_file=resume_file,
        )
        # Optionally: Run analysis/scoring here
        # Link applicant to job
        Applicant_Job.objects.create(applicant=applicant, job=job, is_applied=True)
        return Response({'success': True, 'message': 'Application submitted successfully.'})


class ApplicantRegistrationView(CreateAPIView):
    queryset = Applicant.objects.all()
    serializer_class = ApplicantSerializer

    def perform_create(self, serializer):
        # Hash the password before saving the applicant
        password = self.request.data.get('password')
        if password:
            serializer.save(password=make_password(password))
        else:
            # Handle cases where password might not be provided, though serializer should enforce it
            serializer.save()

class EmployerRegistrationView(CreateAPIView):
    queryset = Employer.objects.all()
    serializer_class = EmployerSerializer

    def perform_create(self, serializer):
        # Hash the password before saving the employer
        password = self.request.data.get('password')
        if password:
            serializer.save(password=make_password(password))
        else:
            serializer.save()

class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']

            # Try to authenticate as Applicant
            user = Applicant.objects.filter(email=email).first()
            if user and user.check_password(password):
                user_type = 'applicant'
            else:
                # Try to authenticate as Employer
                user = Employer.objects.filter(email=email).first()
                if user and user.check_password(password):
                    user_type = 'employer'
                else:
                    return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

            # Generate token (using Simple JWT as an example)
            # You would need to install djangorestframework-simplejwt and configure it
            # pip install djangorestframework-simplejwt
            # In settings.py:
            # REST_FRAMEWORK = {
            #     'DEFAULT_AUTHENTICATION_CLASSES': (
            #         'rest_framework_simplejwt.authentication.JWTAuthentication',
            #     )
            # }
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user_id': user.id,
                'user_type': user_type,
                'email': user.email,
                'name': user.name
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
