from rest_framework import serializers
from api.models import Resume, Analysis, Applicant


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


