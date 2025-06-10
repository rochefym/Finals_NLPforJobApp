from django.urls import path
from api.views import (
    JobListView, 
    JobDetailView, 
    JobStatsView, 
    ApplyToJobView,
    ApplicantRegistrationView,  
    EmployerRegistrationView,
    LoginView  # Import LoginView
)

urlpatterns = [
    path('jobs/', JobListView.as_view(), name='job-list'),
    path('jobs/<int:id>/', JobDetailView.as_view(), name='job-detail'),
    path('jobs/<int:job_id>/apply/', ApplyToJobView.as_view(), name='apply-to-job'),
    path('stats/', JobStatsView.as_view(), name='job-stats'),
    path('register/applicant/', ApplicantRegistrationView.as_view(), name='register-applicant'), 
    path('register/employer/', EmployerRegistrationView.as_view(), name='register-employer'), 
    path('login/', LoginView.as_view(), name='login'), # Add login path
]
