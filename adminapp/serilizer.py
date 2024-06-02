from rest_framework import serializers
from Usable import usable as uc
from webapi.models import *
from passlib.hash import django_pbkdf2_sha256 as handler


class SuperAdminsSerializer(serializers.ModelSerializer):
    profile = serializers.ImageField(required=False)

    class Meta:
        model = SuperAdmin
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


class LoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = SuperAdmin
        fields = ["email", "password"]


class AdminProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = SuperAdmin
        fields = ["fname", "lname", "email", "contact", "profile", "address"]


class FetchUsersSerializer(serializers.ModelSerializer):
    last_login= serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ["id", "status", "fname", "lname", "email", "last_login", "contact", "profile", "street_address"]

    def get_last_login(self, obj):
        latest_token = userwhitelistToken.objects.filter(user=obj).order_by('-created_at').first()
        if latest_token:
            return latest_token.created_at.strftime('%Y-%m-%d %H:%M:%S')
        return None


# Track user

class UserJobView_SerializerAdmin(serializers.ModelSerializer):
    job_title= serializers.CharField(source= "job_id.job_title")
    class Meta:
        model = JobView
        fields = ['job_id', 'job_title']

class UserJobSave_SerializerAdmin(serializers.ModelSerializer):
    job_title= serializers.CharField(source= "job_id.job_title")
    class Meta:
        model = UserJob
        fields = ['job_id', 'job_title']



class UserAllFeedback_Serializer(serializers.ModelSerializer):
    job_title= serializers.CharField(source= "job_id.job_title")
    class Meta:
        model= UserJobFeedback
        fields= ['feedback_text', 'job_id', 'job_title']

class FetchUsersAllDetail_Serializer(serializers.ModelSerializer):
    last_login = serializers.SerializerMethodField()
    viewed_jobs = serializers.SerializerMethodField()
    saved_jobs = serializers.SerializerMethodField()
    all_feedbacks= UserAllFeedback_Serializer(many=True, source="users_id_job_feedbacks")
    
    class Meta:
        model = User
        fields = ["id", "status", "fname", "lname", "email", "last_login", "contact", "profile", "street_address", "viewed_jobs", "saved_jobs", "all_feedbacks"]

    def get_last_login(self, obj):
        latest_token = userwhitelistToken.objects.filter(user=obj).order_by('-created_at').first()
        if latest_token:
            return latest_token.created_at.strftime('%Y-%m-%d %H:%M:%S')
        return None

    def get_viewed_jobs(self, obj):
        viewed_jobs = JobView.objects.filter(user=obj)
        return UserJobView_SerializerAdmin(viewed_jobs, many=True).data

    def get_saved_jobs(self, obj):
        saved_jobs = UserJob.objects.filter(user=obj)
        return UserJobSave_SerializerAdmin(saved_jobs, many=True).data






class UserStatusUpdateSerializer(serializers.Serializer):
    status = serializers.BooleanField(required=True)


class JobsTitle_Serializer(serializers.ModelSerializer):
    view_count = serializers.SerializerMethodField()
    class Meta:
        model = Jobs
        # fields = ['id', 'view_count', 'listing_platform', 'job_title', 'company_name','employment_type', 'seniority_level']
        fields = "__all__"
    
    def get_view_count(self, obj):
        return JobView.objects.filter(job_id=obj).count()


# For JobAndFeedback_Serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'fname', 'lname', 'profile']

class UserJobFeedbackSerializer(serializers.ModelSerializer):
    user = UserSerializer(source='user_id')

    class Meta:
        model = UserJobFeedback
        fields = ['user', 'feedback_text']

class JobAndFeedback_Serializer(serializers.ModelSerializer):
    view_count = serializers.SerializerMethodField()
    feedback= serializers.SerializerMethodField()
    users_feedback = UserJobFeedbackSerializer(many=True, source='user_job_feedbacks')

    class Meta:
        model = Jobs
        fields = [
            'id', 'view_count', 'created_at', 'listing_platform', 
            'job_title', 'company_name', 'company_location', 'company_url',
            'employment_type', 'job_function', 'seniority_level', 'industries', 
            # 'job_description', 
            'links', "feedback", "users_feedback"]
        # fields = "__all__"
    
    def get_feedback(self, obj):
        fetch_feedback = JobFeedback.objects.filter(job=obj).first()
        if fetch_feedback:
            return fetch_feedback.feedback
        return None

    def get_view_count(self, obj):
        return JobView.objects.filter(job_id=obj).count()


class AddJob_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Jobs
        fields = "__all__"


class AddJobFeedback_Serializer(serializers.ModelSerializer):
    class Meta:
        model = JobFeedback
        fields = "__all__"





class UserAllFeedbacksOnJob_Serializer(serializers.ModelSerializer):
    job_title= serializers.CharField(source= 'job_id.job_title')
    user_detail=  UserSerializer(source='user_id')

    class Meta:
        model= UserJobFeedback
        fields= ['job_id', 'job_title', 'user_detail', 'feedback_text']

        

class AdminAllFeedbacksOnJob_Serializer(serializers.ModelSerializer):
    job_title= serializers.CharField(source= 'job.job_title')
    job_id= serializers.CharField(source= 'job')
    feedback_text= serializers.CharField(source= 'job')

    class Meta:
        model= JobFeedback
        fields= ['job_id', 'job_title', 'feedback_text']
