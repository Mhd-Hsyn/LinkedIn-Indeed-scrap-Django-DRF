from django.contrib import admin
from django.http import HttpResponse
from import_export.admin import ImportExportModelAdmin
import csv
# Register your models here.
from .models import *

# Register your models here.
admin.site.register(SuperAdmin)
admin.site.register(User)
admin.site.register(JobFeedback)
admin.site.register(whitelistToken)
admin.site.register(UserJob)
admin.site.register(JobView)
admin.site.register(userwhitelistToken)
admin.site.register(UserJobFeedback)

class CustomModelAdmin(ImportExportModelAdmin):
    search_fields = ['job_title', 'company_name', 'job_description', 'industries']  # Add fields you want to search
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.order_by('-created_at')  # Assuming 'created_at' is the field representing creation date/time

admin.site.register(Jobs, CustomModelAdmin)