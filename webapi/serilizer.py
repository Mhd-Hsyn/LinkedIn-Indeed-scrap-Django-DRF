from rest_framework import serializers
from Usable import usable as uc
from webapi.models import *
from passlib.hash import django_pbkdf2_sha256 as handler


class UsersSerializer(serializers.ModelSerializer):
    profile = serializers.ImageField(required=False)

    class Meta:
        model = User
        fields = [
            "email",
            "password",
            "fname",
            "lname",
            "contact",
            "address",
            "profile",
        ]

    def save(self, **kwargs):
        password = self.validated_data.get("password")
        if password:
            self.validated_data["password"] = handler.hash(password)

        return super().save(**kwargs)


class LoginSerializer(serializers.Serializer):
    class Meta:
        model = User
        fields = ["email", "password"]




class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User


class Jobs_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Jobs
        fields = ['id', 'created_at', 'listing_platform', 'job_title', 'company_name', 'company_location', 'company_url','employment_type', 'job_function', 'seniority_level', 'industries', 'job_description', 'links']
        # fields = "__all__"


class AddJob_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Jobs
        fields = "__all__"


class JobViewSerializer(serializers.ModelSerializer):
    job_id = serializers.UUIDField()  # For job_id field

    class Meta:
        model = JobView
        fields = ['job_id']

    def create(self, validated_data):
        job_id = validated_data['job_id']
        user = self.context['user']

        fetch_job = Jobs.objects.filter(id=job_id).first()

        if fetch_job:
            return JobView.objects.create(user=user, job_id=fetch_job, role=fetch_job.listing_platform)
        else:
            raise serializers.ValidationError("Invalid job_id")


class TrendingJobs_Serializer(serializers.ModelSerializer):
    view_count = serializers.IntegerField()
    class Meta:
        model = Jobs
        fields = "__all__"



class AddUserJobFeedback_Serializer(serializers.ModelSerializer):
    class Meta:
        model = UserJobFeedback
        fields = "__all__"