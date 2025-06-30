from django.shortcuts import render
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated # Import IsAuthenticated

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
    permission_classes = [IsAuthenticated] # Require authentication

    def post(self, request, job_id):
        print(f"ApplyToJobView: Request user: {request.user}")
        print(f"ApplyToJobView: Request user ID: {getattr(request.user, 'id', 'N/A')}")
        print(f"ApplyToJobView: Is authenticated: {request.user.is_authenticated}")
        print(f"ApplyToJobView: Auth token: {request.auth}")

        # Get Applicant from the authenticated user
        # Assuming your JWT token's user_id claim stores the Applicant ID
        # and that your custom user model is Applicant.
        # If you are using Django's default User model with SimpleJWT, request.user will be that User instance.
        # For this example, let's assume the JWT directly identifies an Applicant or Employer.
        
        # The user object attached by JWTAuthentication might be the Applicant/Employer directly
        # if your models are correctly set up with Django's auth system or if SimpleJWT is customized.
        # However, your Applicant/Employer models are not Django AbstractUser.
        # Let's assume the token payload contains user_id which is the Applicant.id
        # We need to ensure that the request.user is actually an Applicant instance.
        # A more robust way would be to check the user_type from the token if available,
        # or ensure this endpoint is only for Applicants.

        applicant_user = request.user
        if not isinstance(applicant_user, Applicant):
            # If request.user is a standard Django User, you might need to fetch the related Applicant profile.
            # For now, let's try to get the applicant ID from the token if it's not directly the applicant model.
            # This part depends heavily on how JWT is configured with your custom models.
            # A common approach if user_id in token is Applicant.id:
            try:
                # Assuming request.user.id is the Applicant ID from the token payload
                applicant = Applicant.objects.get(id=request.user.id) 
            except Applicant.DoesNotExist:
                return Response({'error': 'Applicant profile not found for the authenticated user.'}, status=status.HTTP_403_FORBIDDEN)
            except AttributeError: # If request.user doesn't have an id (e.g. AnonymousUser)
                 return Response({'error': 'Invalid user in token.'}, status=status.HTTP_403_FORBIDDEN)
        else:
            applicant = applicant_user # If request.user is already an Applicant instance

        # Get data from request
        name = request.data.get('name', applicant.name) # Default to applicant's current name
        email = request.data.get('email', applicant.email) # Default to applicant's current email
        phone_number = request.data.get('phone_number')
        start_date_str = request.data.get('start_date')
        resume_file = request.data.get('resume_file')
        years_of_experience_str = request.data.get('years_of_experience')
        expected_salary_str = request.data.get('expected_salary')
        cover_letter = request.data.get('cover_letter')

        # Validate required fields that are not pre-filled or part of the model
        if not all([phone_number, start_date_str, resume_file, years_of_experience_str]):
            return Response({'error': 'Missing required fields: phone_number, start_date, resume_file, years_of_experience are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            job = Job.objects.get(id=job_id)
        except Job.DoesNotExist:
            return Response({'error': 'Job not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Update Applicant details if provided and different
        if name != applicant.name:
            applicant.name = name
        if email != applicant.email: # This could be tricky if email is unique and they try to change to existing one
            # Consider if email change should be allowed here or via a separate profile update mechanism
            pass # For now, let's assume email from token is authoritative or not changed here.
        if phone_number:
            applicant.phone_number = phone_number
        applicant.save() # Save any changes to applicant

        # Create Resume
        if not resume_file:
            return Response({'error': 'Resume file is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        resume_name = f"Resume for {job.job_title} by {applicant.name}"
        resume_instance = Resume.objects.create( # Changed variable name to resume_instance
            applicant=applicant,
            name=resume_name, 
            pdf_file=resume_file,
        )

        # --- Start Resume Analysis Integration ---
        try:
            resume_info_extractor = ResumeInformationExtraction()
            resume_classifier = ResumeClassifier()
            resume_path = resume_instance.pdf_file.path

            extracted_from_resume = resume_info_extractor.parse_resume(resume_path)
            top3_predicted_job_categories, top3_job_recommendations = resume_classifier.get_top3_job_prediction_and_recommendation(resume_path)

            analysis_instance = Analysis.objects.create(
                name=extracted_from_resume.get('name'),
                email=extracted_from_resume.get('email'),
                mobile_number=extracted_from_resume.get('mobile_number'),
                years_of_experience=extracted_from_resume.get('total_experience'),
                experience_level=extracted_from_resume.get('experience_level'),
                experience_description=extracted_from_resume.get('experience_description'),
                experience_range=extracted_from_resume.get('experience_range'),
                skills=extracted_from_resume.get('skills', []),
                educational_institutions=extracted_from_resume.get('educational_institutions', []),
                educational_attainment=extracted_from_resume.get('educational_attainment', []),
                no_of_pages=extracted_from_resume.get('no_of_pages'),
                predicted_job_categories=top3_predicted_job_categories,
                recommended_jobs=top3_job_recommendations,
            )
            resume_instance.analysis = analysis_instance
            resume_instance.save()
        except Exception as e:
            # Log the error and potentially inform the user, but don't fail the whole application
            # For now, we'll just print it. In production, use proper logging.
            print(f"Error during resume analysis for resume {resume_instance.id}: {e}")
            # The application can still proceed without the analysis if it fails
            pass
        # --- End Resume Analysis Integration ---

        # Link Applicant to Job
        # Check if already applied
        if Applicant_Job.objects.filter(applicant=applicant, job=job).exists():
            return Response({'message': 'You have already applied for this job.', 'success': False}, status=status.HTTP_400_BAD_REQUEST)

        Applicant_Job.objects.create(
            applicant=applicant, 
            job=job, 
            is_applied=True,
            # Optionally, store other application details here if Applicant_Job model is extended
            # e.g., cover_letter_snapshot=cover_letter, applied_expected_salary=expected_salary_str etc.
            )

        return Response({'success': True, 'message': 'Application submitted successfully.'}, status=status.HTTP_201_CREATED)

class ApplicantRegistrationView(CreateAPIView):
    queryset = Applicant.objects.all()
    serializer_class = ApplicantSerializer

    def perform_create(self, serializer):
        # Hash the password before saving the applicant
        password = self.request.data.get('password')
        if password:
            serializer.save(password=make_password(password))
        else:
            # Handle case where password is not provided if necessary,
            # or rely on serializer validation
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
            try:
                user = Applicant.objects.get(email=email)
                user_type = 'applicant'
                if not check_password(password, user.password): # Use check_password
                    user = None
            except Applicant.DoesNotExist:
                user = None

            # If not Applicant, try to authenticate as Employer
            if not user:
                try:
                    user = Employer.objects.get(email=email)
                    user_type = 'employer'
                    if not check_password(password, user.password): # Use check_password
                        user = None
                except Employer.DoesNotExist:
                    user = None
            
            if user:
                refresh = RefreshToken.for_user(user) # Generate token for the user instance
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'user_id': user.id,
                    'user_type': user_type,
                    'email': user.email,
                    'name': user.name,
                })
            return Response({'detail': 'Invalid credentials or user not found.'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ApplicantLatestResumeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        applicant_user = request.user
        applicant = None

        # Determine if the request.user is an Applicant instance or needs to be fetched
        # This logic assumes your JWT token correctly identifies the user and their ID
        if isinstance(applicant_user, Applicant):
            applicant = applicant_user
        elif hasattr(request.user, 'id'): # Check if it's a user object with an ID
            try:
                # Attempt to fetch Applicant by the ID from the token
                # This assumes the ID in the token corresponds to an Applicant ID
                applicant = Applicant.objects.get(id=request.user.id)
            except Applicant.DoesNotExist:
                # If not found as Applicant, it could be an Employer or other user type
                # For this endpoint, we only care about Applicants
                return Response({'error': 'Applicant profile not found for the authenticated user.'}, status=status.HTTP_403_FORBIDDEN)
            except AttributeError: # Should not happen if hasattr('id') is true
                 return Response({'error': 'Invalid user in token.'}, status=status.HTTP_403_FORBIDDEN)
        else:
            # If request.user is AnonymousUser or something unexpected
            return Response({'error': 'Authentication credentials were not provided or are invalid.'}, status=status.HTTP_401_UNAUTHORIZED)

        if not applicant: # Double check if applicant was resolved
             return Response({'error': 'Could not identify applicant from token.'}, status=status.HTTP_403_FORBIDDEN)

        try:
            latest_resume = Resume.objects.filter(applicant=applicant).latest('uploaded_at')
            
            # The ResumeSerializer is already configured to include 'analysis'
            # If latest_resume.analysis is None, it will be represented as null in JSON
            serializer = ResumeSerializer(latest_resume)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Resume.DoesNotExist:
            return Response({'message': 'No resumes found for this applicant.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(f"Error fetching latest resume/analysis: {e}") # Basic logging
            return Response({'error': 'An error occurred while fetching resume data.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
