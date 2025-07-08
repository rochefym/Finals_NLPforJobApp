from django.urls import path
from api.views import (ApplicantJobMatches, JobApplicantMatches, UpdateMatchesForJob)

urlpatterns = [
    path('applicant/<int:applicant_id>/matches/', ApplicantJobMatches.as_view()),
    path('job/<int:job_id>/matches/', JobApplicantMatches.as_view()),
    path('job/<int:job_id>/update-matches/', UpdateMatchesForJob.as_view()),
]