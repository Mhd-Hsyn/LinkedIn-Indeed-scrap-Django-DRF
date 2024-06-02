from django.urls import path, include
from rest_framework.routers import DefaultRouter
from adminapp.views import *

router = DefaultRouter()
router.register(r"admin", AdminAuthViewset)
router.register(r"adminapi", SuperAdminApiViewset, basename="adminapi")
router.register(r"users", UserAdminApiViewset, basename="adminapi")
router.register(r"jobs", AdminJobRightViewset, basename="jobs")
router.register(r"job-feedback", FeedbackOnJob, basename="user-job-feedback")


urlpatterns = [
    path("", include(router.urls)),
]
