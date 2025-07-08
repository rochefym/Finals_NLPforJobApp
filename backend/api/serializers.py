from rest_framework import serializers
from api.models import Resume, Analysis, Applicant, ApplicantJob


class ApplicantSerializer(serializers.ModelSerializer):     
    class Meta:
        model = Applicant
        fields = '__all__'


class AnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = Analysis
        fields = '__all__'


class ResumeSerializer(serializers.ModelSerializer):
    analysis = AnalysisSerializer(read_only=True)

    class Meta:
        model = Resume
        fields = '__all__'


### maria's code ###

class ApplicantJobSerializer(serializers.ModelSerializer):
    applicant = ApplicantSerializer()
    job = serializers.SerializerMethodField()
    
    class Meta:
        model = ApplicantJob
        fields = ['id', 'applicant', 'job', 'similarity_score', 'is_applied']
    
    def get_job(self, obj):
        return {
            'id': obj.job.id,
            'title': obj.job.title,
            'company': obj.job.employer.company_name
        }