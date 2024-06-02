from django.db import models
import uuid
from django.core.exceptions import ValidationError


class BaseModel(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, max_length=255
    )
    updated_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    class Meta:
        abstract = True


class SuperAdmin(BaseModel):
    fname = models.CharField(max_length=255, default="")
    lname = models.CharField(max_length=255, default="")
    address = models.TextField(default="")
    email = models.EmailField(max_length=255, default="")
    password = models.TextField(default="")
    contact = models.CharField(max_length=20, default="")
    profile = models.ImageField(upload_to="SuperAdmin/", default="SuperAdmin/dummy.jpg")
    Otp = models.IntegerField(default=0)
    OtpCount = models.IntegerField(default=0)
    OtpStatus = models.BooleanField(default=False)
    no_of_attempts_allowed = models.IntegerField(default=3)
    no_of_wrong_attempts = models.IntegerField(default=0)
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.email


class whitelistToken(models.Model):
    user = models.ForeignKey(SuperAdmin, on_delete=models.CASCADE)
    token = models.TextField(default="")
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)


class User(BaseModel):
    email = models.EmailField(max_length=255, default="")
    fname = models.CharField(max_length=255, default="")
    lname = models.CharField(max_length=255, default="")
    contact = models.CharField(max_length=20, default="")
    street_address = models.CharField(max_length=255, default="")
    city = models.CharField(max_length=255, default="")
    field_of_study = models.CharField(max_length=255, default="")
    postal_code = models.CharField(max_length=255, default="")
    address = models.TextField(default="")
    password = models.TextField(default="")
    level_of_education = models.TextField(default="")
    Otp = models.IntegerField(default=0)
    OtpCount = models.IntegerField(default=0)
    OtpStatus = models.BooleanField(default=False)
    no_of_attempts_allowed = models.IntegerField(default=3)
    no_of_wrong_attempts = models.IntegerField(default=0)
    status = models.BooleanField(default=True)
    profile = models.ImageField(upload_to="User/", default="User/dummy.jpg")
    resume = models.FileField(upload_to="User/")

    def __str__(self):
        return self.email


class userwhitelistToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.TextField(default="")
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)


class Jobs(BaseModel):
    JOB_PLATFORM_CHOICES = (
        ('Indeed', 'Indeed'),
        ('LinkedIn', 'LinkedIn'),
    )
    city = models.CharField(max_length=50, blank=True, null=True)
    job_title = models.CharField(max_length=255, default="", blank=True, null=True)
    company_name = models.CharField(max_length=255, default="", blank=True, null=True)
    company_location = models.CharField(max_length=255, default="", blank=True, null=True)
    employment_type = models.CharField(max_length=255, default="", blank=True, null=True)
    applicants = models.CharField(max_length=255, default="", blank=True, null=True)
    job_function = models.CharField(max_length=255, default="", blank=True, null=True)
    seniority_level = models.CharField(max_length=255, default="", blank=True, null=True)
    industries = models.CharField(max_length=255, default="", blank=True, null=True)
    links = models.TextField(default="", blank=True, null=True)
    job_description = models.TextField(default="", blank=True, null=True)
    company_url = models.TextField(default="", blank=True, null=True)
    salary = models.CharField(max_length=250, blank=True, null=True)# for indeed only
    listing_platform = models.CharField(max_length=250, choices=JOB_PLATFORM_CHOICES, blank=True, null=True)

    def __str__(self):
        return self.job_title

    class Meta:
        indexes = [
            models.Index(
                fields=[
                    "city",
                    "job_title",
                    "company_name",
                    "company_location",
                    "employment_type",
                ]
            ),
        ]


class JobView(models.Model):
    JOB_ROLES = (
        ('Indeed', 'Indeed'),
        ('LinkedIn', 'LinkedIn'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    job_id = models.ForeignKey(Jobs, on_delete=models.CASCADE, null=True, blank=True)
    role = models.CharField(max_length=50, choices=JOB_ROLES, blank=True, null=True)
    viewed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.user} ------ {self.role} ------ {self.job_id}" 
    
    class Meta:
        unique_together = (('user', 'job_id'))


class UserJob(models.Model):
    JOB_ROLES = (
        ('Indeed', 'Indeed'),
        ('LinkedIn', 'LinkedIn'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=50, choices=JOB_ROLES)
    job_id = models.ForeignKey(Jobs, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return f"User: {self.user.email}, Role: {self.role}"
    
    class Meta:
        unique_together = (('user', 'job_id'))



class JobFeedback(BaseModel):
    job = models.OneToOneField(Jobs, on_delete=models.CASCADE, related_name='feedbacks', blank=True, null=True)
    admin_id = models.ForeignKey(SuperAdmin, on_delete=models.CASCADE, blank=True, null=True)
    feedback = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'Feedback by {self.admin_id.email} for {self.job.job_title} ______ {self.feedback}'


class UserJobFeedback(BaseModel):
    job_id= models.ForeignKey(Jobs, on_delete=models.CASCADE, related_name='user_job_feedbacks',blank=True, null=True)
    user_id= models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="users_id_job_feedbacks")
    feedback_text= models.TextField()

    class Meta:
        unique_together = (('user_id', 'job_id'))

    def __str__(self):
        return f'Feedback by {self.user_id.email} for {self.job_id.job_title} ______ {self.feedback_text}'
    
    def save(self, *args, **kwargs):
        # Check if a feedback from the same user for the same job already exists
        if UserJobFeedback.objects.filter(job_id=self.job_id, user_id=self.user_id).exclude(pk=self.pk).exists():
            raise ValidationError("A user can only add one feedback per job.")
        super(UserJobFeedback, self).save(*args, **kwargs)