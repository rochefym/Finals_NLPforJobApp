from django.db import models


class Applicant(models.Model):
    name = models.CharField(max_length=100)
    password = models.CharField(max_length=128)  
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20)
    
    def __str__(self):
        return f"{self.id} - {self.name}"


class Analysis(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    email = models.CharField(max_length=100, null=True, blank=True)
    mobile_number = models.CharField(max_length=100, null=True, blank=True)
    years_of_experience  = models.DecimalField(max_digits=10, decimal_places=1, null=True, blank=True)
    experience_level = models.CharField(max_length=100, null=True, blank=True)
    experience_description = models.CharField(max_length=300, null=True, blank=True)
    experience_range = models.CharField(max_length=100, null=True, blank=True)
    skills = models.JSONField(default=list) 
    educational_institutions = models.JSONField(default=list) 
    educational_attainment = models.JSONField(default=list) 
    no_of_pages = models.IntegerField(null=True, blank=True)
    predicted_job_categories= models.JSONField(default=list)
    recommended_jobs = models.JSONField(default=list)
    
    def __str__(self):
        return f"Analysis id: {self.id}"


class Resume(models.Model):
    applicant = models.ForeignKey(Applicant, on_delete=models.CASCADE, related_name='resumes')
    analysis = models.ForeignKey(Analysis, on_delete=models.CASCADE, related_name='resumes', null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    pdf_file = models.FileField(upload_to='pdfs/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.id} - {self.name}"



#### maria's code ####

class Job(models.Model):
    employer = models.ForeignKey('Employer', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    requirements = models.TextField()
    skills = models.JSONField(default=list)  # Store as ['Python', 'Django', ...]
    salary_range = models.CharField(max_length=100)
    location = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    posted_at = models.DateTimeField(auto_now_add=True)

class Employer(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    company_name = models.CharField(max_length=255)
    company_profile = models.TextField()

class ApplicantJob(models.Model):
    applicant = models.ForeignKey(Applicant, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    similarity_score = models.FloatField()  # 0.0 to 1.0
    is_applied = models.BooleanField(default=False)
    last_updated = models.DateTimeField(auto_now=True)




