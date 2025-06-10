from rest_framework import serializers
from api.models import Resume, Analysis, Applicant, Employer, Job, Applicant_Job


class ApplicantSerializer(serializers.ModelSerializer):     
    class Meta:
        model = Applicant
        fields = ['id', 'name', 'email', 'phone_number', 'password'] # Include password
        extra_kwargs = {
            'password': {'write_only': True} # Make password write-only
        }

    def create(self, validated_data):
        # Hash password before saving
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password) # Django's built-in way to hash
        instance.save()
        return instance


class AnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = Analysis
        fields = '__all__'


class ResumeSerializer(serializers.ModelSerializer):
    analysis = AnalysisSerializer(read_only=True)

    class Meta:
        model = Resume
        fields = '__all__'


class EmployerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employer
        fields = ['id', 'name', 'email', 'phone_number', 'company_name', 'company_profile', 'password'] # Include password
        extra_kwargs = {
            'password': {'write_only': True} # Make password write-only
        }

    def create(self, validated_data):
        # Hash password before saving
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password) # Django's built-in way to hash
        instance.save()
        return instance


class JobSerializer(serializers.ModelSerializer):
    employer = EmployerSerializer(read_only=True)
    class Meta:
        model = Job
        fields = '__all__'


class ApplicantJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Applicant_Job
        fields = '__all__'


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email and password:
            # Note: Authentication logic will be in the view
            # Here we just ensure fields are present
            pass
        else:
            raise serializers.ValidationError("Must include 'email' and 'password'.")

        return data


