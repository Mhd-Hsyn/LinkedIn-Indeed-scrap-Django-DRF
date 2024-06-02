from django.urls import path, include
from rest_framework.routers import DefaultRouter
from webapi.views import *

router = DefaultRouter()
router.register(r"users", UserAuthViewset)
router.register(r"jobsScrap", JobScrap_Viewset, basename="linkdinScrap")
router.register(r"jobs", GetDataViewSet, basename="jobs")

urlpatterns = [
    path("", include(router.urls)),
    path("user_save_job",UserSaveJob.as_view(), name= "user_save_job"),
    path("get_jobs",GetJobsWithID.as_view(), name= "get_jobs"),
    path("savejobs_localToDB",SaveUserJobs_LocalToDB.as_view(), name= "savejobs_localToDB"),
    path("track_trend_job",GetTrendingJob.as_view(), name= "track_trend_job"),
    path("add_jobview",AddViewsOnJob.as_view(), name= "add_jobview"),
    path("add_jobfeedback",AddJobFeedback.as_view(), name= "add_jobfeedback"),
    
]
