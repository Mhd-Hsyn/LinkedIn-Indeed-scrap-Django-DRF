from datetime import datetime, timedelta
from rest_framework.viewsets import ModelViewSet
from django.db import IntegrityError
from django.db.models import Max
from rest_framework.exceptions import ValidationError
from django.db.models import Count
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.http import HttpResponse
from django.conf import settings
from decouple import config
from Usable import usable as uc
from .serilizer import *
from webapi.models import *
from .pagination import JobsPagination
from rest_framework.decorators import action
from rest_framework import status
from Usable.permissions import *
from django.contrib.auth.hashers import check_password
import Usable.emailpattern as verfied
import random
from Scrap.scrap_indeed.scrap_indeed import run_scraping
from Scrap.scrap_linkdin.script_without_login import ScrapLinkdin
from rest_framework import filters
from django.db.models import Q
from unidecode import unidecode
from rest_framework.exceptions import ValidationError


STATES= [
    "Mississippi",
    "New Hampshire",
    "Alaska",
    "New York",
    "Ohio",
    "Pennsylvania",
    "Illinois",
    "North Carolina",
    "Oklahoma",
    "Massachusetts",
    "North Dakota",
    "Kansas",
    "Kentucky",
    "Washington",
    "Colorado",
    "Tennessee",
    "Wisconsin",
    "Hawaii",
    "New Mexico",
    "Oregon",
    "South Dakota",
    "Connecticut",
    "West Virginia",
    "Wyoming",
    "Nebraska",
    "Nevada",
    "Delaware",
    "Arizona",
    "Maine",
    "Alabama",
    "Georgia",
    "Florida",
    "Michigan",
    "Arkansas",
    "New Jersey",
    "Indiana",
    "Iowa",
    "South Carolina",
    "Maryland",
    "Louisiana",
    "Rhode Island",
    "California",
    "Texas",
    "Utah",
    "Vermont",
    "Montana",
    "Missouri",
    "Virginia",
    "Idaho",
    "Minnesota"
]



# def index(request):
#     return HttpResponse("<h1>Project-Kuber</h1>")


class UserAuthViewset(ModelViewSet):
    queryset = User.objects.all()

    @action(detail=False, methods=["POST"])
    def signup(self, request):
        try:
            requireFields = [
                "email",
                "password",
                "fname",
                "lname",
            ]
            profile= request.data.get("profile", None)
            if profile is not None and not profile: 
                del request.data['profile']
            validator = uc.keyValidation(True, True, request.data, requireFields)
            if validator:
                return Response(
                    {"status": False, "message": "All fields are required"}, status=200
                )

            email_valid = uc.checkemailforamt(request.data.get("email"))
            if not email_valid:
                return Response(
                    {"status": False, "message": "Invalid email format"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            password_valid = uc.passwordLengthValidator(request.data.get("password"))
            if not password_valid:
                return Response(
                    {
                        "status": False,
                        "message": "Password length should be at least 8 characters",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            serializer = UsersSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            email = serializer.validated_data["email"]
            if User.objects.filter(email=email).exists():
                return Response(
                    {"status": False, "message": "Email address already exists"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            serializer.save()
            return Response(
                {"status": True, "message": "Signup Successfully"},
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            return Response(
                {"status": False, "message": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=["post"])
    def login(self, request):
        try:
            serializer = LoginSerializer(data=request.data)
            email = request.data["email"]
            password = request.data["password"]

            user = User.objects.filter(email=email).first()

            if user:
                if user.status:
                    if check_password(password, user.password):
                        generate_auth = uc.generatedToken(
                            user, config("User_jwt_token"), 1, request
                        )
                        print(generate_auth)
                        if generate_auth["status"]:
                            user.no_of_wrong_attempts = 0
                            user.save()

                            return Response(
                                {
                                    "status": True,
                                    "message": "Login Successfully",
                                    "token": generate_auth["token"],
                                    "data": generate_auth["payload"],
                                },
                                status=200,
                            )
                        else:
                            return Response(generate_auth)
                    else:
                        return Response(
                            {"status": False, "message": "Invalid Credentials"},
                            status=401,
                        )
                else:
                    return Response(
                        {"status": False, "message": "Your Account is disabled"},
                        status=403,
                    )
            else:
                return Response(
                    {"status": False, "message": "Invalid Credentials"}, status=401
                )

        except Exception as e:
            message = {"status": False}
            (
                message.update(message=str(e))
                if settings.DEBUG
                else message.update(message="Internal server error")
            )
            return Response(message, status=500)

    @action(detail=False, methods=["post"])
    def forgetPasswordSendOtp(self, request):
        try:
            requireFields = ["email"]
            validator = uc.keyValidation(True, True, request.data, requireFields)
            if validator:
                return Response(validator, status=200)

            else:
                email = request.data["email"]
                emailstatus = uc.checkemailforamt(email)
                if not emailstatus:
                    return Response(
                        {"status": False, "message": "Email format is incorrect"}
                    )

                fetchadmin = User.objects.filter(email=email).first()

                if fetchadmin:
                    token = random.randrange(100000, 999999, 6)
                    fetchadmin.Otp = token
                    fetchadmin.OtpCount = 0
                    fetchadmin.OtpStatus = True
                    fetchadmin.save()
                    emailstatus = verfied.forgetEmailPattern(
                        {
                            "subject": "forget password",
                            "EMAIL_HOST_USER": config("EMAIL_HOST_USER"),
                            "toemail": email,
                            "token": token,
                        }
                    )
                    if emailstatus:
                        return Response(
                            {
                                "status": True,
                                "message": "Email send successfully",
                                "id": fetchadmin.id,
                                "otp": token,
                            }
                        )

                    else:
                        return Response(
                            {"status": False, "message": "Something went wrong"}
                        )
                else:
                    return Response({"status": False, "message": "Email doesnot exist"})

        except Exception as e:
            message = {"status": False}
            (
                message.update(message=str(e))
                if settings.DEBUG
                else message.update(message="Internal server error")
            )
            return Response(message, status=500)

    @action(detail=False, methods=["POST"])
    def checkOtp(self, request):
        try:
            requireFields = ["otp", "id"]
            validator = uc.keyValidation(True, True, request.data, requireFields)

            if validator:
                return Response(validator, status=200)

            else:
                otp = request.data["otp"]
                uid = request.data["id"]
                fetchuser = User.objects.filter(id=uid).first()
                print("Current OtpCount:", fetchuser.OtpCount)
                if fetchuser:
                    if fetchuser.OtpStatus and fetchuser.OtpCount < 3:
                        if fetchuser.Otp == int(otp):
                            fetchuser.Otp = 0
                            fetchuser.save()
                            print("OTP verified successfully")
                            return Response(
                                {
                                    "status": True,
                                    "message": "Otp verified . . . ",
                                    "id": str(fetchuser.id),
                                },
                                status=status.HTTP_200_OK,
                            )
                        else:
                            fetchuser.OtpCount += 1
                            fetchuser.save()
                            print("OTP verification failed. OtpCount incremented.")
                            if fetchuser.OtpCount >= 30:
                                fetchuser.Otp = 0
                                fetchuser.OtpCount = 0
                                fetchuser.OtpStatus = False
                                fetchuser.save()
                                print("OTP expired. Resetting OtpCount.")
                                return Response(
                                    {
                                        "status": False,
                                        "message": f"Your OTP is expired . . . Kindly get OTP again",
                                    }
                                )
                            return Response(
                                {
                                    "status": False,
                                    "message": f"Your OTP is wrong",
                                }
                            )
                    return Response(
                        {
                            "status": False,
                            "message": "Your OTP is expired . . . Kindly get OTP again",
                        },
                        status=404,
                    )
                return Response(
                    {"status": False, "message": "User not exist"}, status=404
                )

                return Response(
                    {"status": False, "message": "User not exist"}, status=404
                )

        except Exception as e:
            message = {"status": False}
            (
                message.update(message=str(e))
                if settings.DEBUG
                else message.update(message="Internal server error")
            )
            return Response(message, status=500)

    @action(detail=False, methods=["POST"])
    def resetPassword(self, request):
        try:
            requireFeild = ["id", "newpassword"]
            validator = uc.keyValidation(True, True, request.data, requireFeild)
            if validator:
                return Response(validator, status=400)

            uid = request.data["id"]
            newpassword = request.data["newpassword"]
            if not uc.passwordLengthValidator(newpassword):
                return Response(
                    {
                        "status": False,
                        "error": "Password length must be greater than 8",
                    },
                    status=400,
                )
            fetchuser = User.objects.filter(id=uid).first()
            if fetchuser:
                if fetchuser.OtpStatus == True and fetchuser.Otp == 0:
                    fetchuser.password = handler.hash(newpassword)
                    fetchuser.OtpStatus = False
                    fetchuser.OtpCount = 0
                    fetchuser.save()
                    fetch_tokens = userwhitelistToken.objects.filter(user=fetchuser)
                    if fetch_tokens:
                        fetch_tokens.delete()
                    return Response(
                        {
                            "status": True,
                            "message": "Forget Password Successfully ",
                        },
                        status=200,
                    )
                return Response(
                    {
                        "status": False,
                        "message": "Your OTP is expired . . . Kindly get OTP again",
                    },
                    status=400,
                )
            return Response(
                {"status": False, "message": "User Not Exist !!!"}, status=404
            )
        except Exception as e:
            return Response({"status": False, "message": str(e)}, status=400)



class UserApiViewset(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [authorization]

    @action(detail=False, methods=["GET", "PUT"])
    def profile(self, request):
        try:
            if request.method == "GET":
                fetchuser = User.objects.filter(id=request.GET["token"]["id"]).first()
                access_token_payload = {
                    "id": fetchuser.id,
                    "fname": fetchuser.fname,
                    "email": fetchuser.email,
                    "lname": fetchuser.lname,
                    "contact": fetchuser.contact,
                    "street_address": fetchuser.street_address,
                    "city": fetchuser.city,
                    "field_of_study": fetchuser.field_of_study,
                    "postal_code": fetchuser.postal_code,
                    "address": fetchuser.address,
                    "level_of_education": fetchuser.level_of_education,
                    "postal_code": fetchuser.postal_code,
                    "profile": fetchuser.profile.url,
                }
                if fetchuser.resume:
                    access_token_payload["resume"] = fetchuser.resume.url

                return Response({"status": True, "data": access_token_payload})

            if request.method == "PUT":
                requireFields = [
                    "fname",
                    "lname",
                    "contact",
                    "street_address",
                    "city",
                    "field_of_study",
                    "postal_code",
                    "address",
                    "level_of_education",
                    "profile",
                ]
                validator = uc.keyValidation(True, True, request.data, requireFields)
                if validator:
                    return Response(validator, status=422)
                else:
                    try:
                        fetchuser = User.objects.get(id=request.GET["token"]["id"])

                        for field in requireFields:
                            if field in request.data:
                                setattr(fetchuser, field, request.data[field])

                        if request.FILES.get("profile"):
                            fetchuser.profile = request.FILES["profile"]

                        if request.FILES.get("resume"):
                            fetchuser.resume = request.FILES["resume"]

                        fetchuser.save()

                        obj = uc.makedict(
                            fetchuser,
                            [
                                "id",
                                "email",
                                "contact",
                                "fname",
                                "lname",
                                "address",
                                "profile",
                            ],
                            True,
                        )

                        return Response(
                            {
                                "status": True,
                                "message": "Profile Edit Successfully",
                                "data": obj,
                            }
                        )

                    except User.DoesNotExist:
                        return Response(
                            {"status": False, "message": "User not found"}, status=404
                        )

        except Exception as e:
            message = {"status": False}
            (
                message.update(message=str(e))
                if settings.DEBUG
                else message.update(message="Internal server error")
            )
            return Response(message, status=500)


from collections import OrderedDict


class JobScrap_Viewset(ModelViewSet):
    queryset = Jobs.objects.all()
    serializer_class = Jobs_Serializer

    @action(detail=False, methods=["POST"])
    def post_job(self, request):
        try:
            data = request.data
            new_data= data
            ser = AddJob_Serializer(data=new_data)
            if ser.is_valid():
                ser.save()
                return Response(
                    {"status": True, "message": "LinkedIn data posted Successfully"},
                    status=201,
                )
            else:
                return Response(
                    {"status": False, "message": f"{ser.errors}"}, status=400
                )

        except Exception as e:
            message = {"status": False}
            (
                message.update(message=str(e))
                if settings.DEBUG
                else message.update(message="Internal server error")
            )
            return Response(message, status=500)


    @action(detail=False, methods=["GET"])
    def get_jobs(self, request):
        try:
            if request.method == "GET":
                city = request.GET.get("city", None)
                job_title = request.GET.get("job_title", None)
                company_name = request.GET.get("company_name", None)
                keyword = request.GET.get("keyword", None)
                job_type = request.GET.get("job_type", None)
                date_posted = request.GET.get("date_posted", None)

                query_params = Q()  # Start with an empty query

                if city:
                    city = unidecode(city)  # Convert city name to ASCII characters
                    # Apply an OR operation between city and company_location
                    query_params |= Q(city__icontains=city) | Q(company_location__icontains=city)

                if job_title:
                    query_params &= Q(job_title__icontains=job_title)

                if company_name:
                    query_params &= Q(company_name__icontains=company_name)
                if job_type:
                    query_params &= Q(employment_type__icontains= job_type)
                if keyword:
                    keyword = unidecode(keyword)  # Convert query to ASCII characters
                    # Apply an OR operation across all fields
                    query_params &= (
                        Q(city__icontains=keyword) |
                        Q(company_location__icontains=keyword) |
                        Q(job_title__icontains=keyword) |
                        Q(job_description__icontains=keyword) |
                        Q(company_name__icontains=keyword)|
                        Q(job_function__icontains=keyword) |
                        Q(seniority_level__icontains=keyword) |
                        Q(industries__icontains=keyword) |
                        Q(employment_type__icontains=keyword)
                    )
                if date_posted:
                    current_date = datetime.now().date()
                    if date_posted == "less_than_1_day":
                        query_params &= Q(created_at__gte=current_date - timedelta(days=1))
                    elif date_posted == "under_1_week":
                        query_params &= Q(created_at__gte=current_date - timedelta(weeks=1))
                    elif date_posted == "under_1_month":
                        query_params &= Q(created_at__gte=current_date - timedelta(weeks=4))
                    elif date_posted == "older_than_1_month":
                        query_params &= Q(created_at__lt=current_date - timedelta(weeks=4))

                # Apply filtering based on query_params
                results = Jobs.objects.filter(query_params)
                print(results)

                # Order queryset by created_at field in descending order
                results = results.order_by("-created_at")
                # Paginate the queryset
                paginator = JobsPagination()
                paginated_results = paginator.paginate_queryset(results, request)
                ser = Jobs_Serializer(paginated_results, many=True)
                return paginator.get_paginated_response(ser.data)

        except Exception as e:
            message = {"status": False}
            (
                message.update(message=str(e))
                if settings.DEBUG
                else message.update(message="Internal server error")
            )
            return Response(message, status=500)

    @action(detail=False, methods=["GET"])
    def getSuggestions(self, request):
        query = request.query_params.get("query", "")
        city = request.query_params.get("city", "")
        company_name = request.query_params.get("company_name", "")

        if not query and not city and not company_name:
            return Response(
                "At least one of the parameters 'query', 'city', or 'company_name' is required.",
                status=400,
            )

        if query and not city and not company_name:
            jobs_suggestions = Jobs.objects.filter(
                job_title__icontains=query
            ).values_list("id", "job_title")

            top_suggestions = list(jobs_suggestions[:5])

            return Response(
                {
                    "jobs_suggestions": top_suggestions,
                },
                status=status.HTTP_200_OK,
            )

        elif not query and city and not company_name:

            unique_cities= [state for state in STATES if state.lower().startswith(city.lower())]
            return Response(
                {"city_suggestions": unique_cities}, status=status.HTTP_200_OK
            )

        elif not query and not city and company_name:
            jobs_suggestions = Jobs.objects.filter(
                company_name__icontains=company_name
            ).values_list("id", "company_name")[:5]

            unique_jobs_suggestions = {}

            for id, name in jobs_suggestions:
                unique_jobs_suggestions.setdefault(name, id)

            return Response(
                {
                    "company_suggestions": list(
                        unique_jobs_suggestions.items()
                    )
                },
                status=status.HTTP_200_OK,
            )

class GetDataViewSet(ModelViewSet):
    def retrieve(self, request, pk=None):
        try:
            linkedin_job = Jobs.objects.get(pk=pk)
            serializer = Jobs_Serializer(linkedin_job)
            return Response(serializer.data)
        
        except Jobs.DoesNotExist:
            return Response({"message": "Job not found."}, status=404)


class UserSaveJob(APIView):
    permission_classes= [authorization]
    def post(self, request):
        try:
            user_id= request.GET['token']['id']
            job_id= request.data.get("job_id", None)
            if not job_id:
                return Response ({
                    "status": False,
                    "message": "id not give"
                    },status=400
                    )
            if UserJob.objects.filter(user_id=user_id, job_id__id=job_id).exists():
                return Response({
                    "status": False,
                    "message": "Job already saved"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            fetch_job = Jobs.objects.filter(id= job_id).first()
            if fetch_job:
                UserJob.objects.create(
                    user_id= user_id,
                    role= fetch_job.listing_platform,
                    job_id= fetch_job
                )
                return Response({
                    "status": True,
                    "message": f"Job saved successfully from {fetch_job.listing_platform}"
                }, status=status.HTTP_201_CREATED)
            
            return Response({
                "status": False,
                "message": "Job not found in either Indeed or LinkedIn"
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response (str(e), status= 400)
    

    def get(self, request):
        user_id= request.GET['token']['id']
        # Fetch all jobs saved by the user
        user_jobs = UserJob.objects.filter(user_id=user_id)
        
        linkedin_jobs = [uj.job_id for uj in user_jobs if uj.role == 'LinkedIn']
        indeed_jobs = [uj.job_id for uj in user_jobs if uj.role == 'Indeed']

        # Serialize the data
        linkedin_serializer = Jobs_Serializer(linkedin_jobs, many=True)
        indeed_serializer = Jobs_Serializer(indeed_jobs, many=True)
        
        return Response({
            "status": True,
            "linkedin_jobs": linkedin_serializer.data,
            "indeed_jobs": indeed_serializer.data
        }, status=status.HTTP_200_OK)
    
    def delete(self, request):
        user_id= request.GET['token']['id']
        job_id= request.data.get("job_id", None)
        if not job_id:
            return Response ({
                "status": False,
                "message": "id not give"
                },status=400
                )
        user_job = UserJob.objects.filter(user_id=user_id, job_id__id=job_id).first()
        
        if not user_job:
            return Response({
                "status": False,
                "message": "Job not found for this user"
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Delete the user-saved job
        user_job.delete()
        
        return Response({
            "status": True,
            "message": "Job deleted successfully"
        }, status=status.HTTP_200_OK)



class GetJobsWithID(APIView):
    def post(self, request):
        try:
            id_list= request.data.get('id_list', None)
            if not id_list:
                return Response ({'status': False, "message": "id_list must be required ..."}, status=500)
            # Query Indeed jobs with the provided IDs
            indeed_jobs = Jobs.objects.filter(id__in=id_list, listing_platform= "Indeed")
            indeed_serializer = Jobs_Serializer(indeed_jobs, many=True)
            
            # Query LinkedIn jobs with the provided IDs
            linkedin_jobs = Jobs.objects.filter(id__in=id_list, listing_platform= "LinkedIn")
            linkedin_serializer = Jobs_Serializer(linkedin_jobs, many=True)
            
            return Response({
                'status': True,
                'linkedin_jobs': linkedin_serializer.data,
                'indeed_jobs': indeed_serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as swr:
            message = {"status": False}
            (
                message.update(message=str(swr))
                if settings.DEBUG
                else message.update(message="Internal server error")
            )
            return Response(message, status=500)


class SaveUserJobs_LocalToDB(APIView):
    permission_classes= [authorization]

    def post(self, request):
        try:
            user_id= request.GET['token']['id']
            id_list= request.data.get('id_list', None)
            if not id_list:
                return Response ({
                    "status": False,
                    "message": "id_list must be required"
                }, status=status.HTTP_400_BAD_REQUEST)
            existing_user_jobs = UserJob.objects.filter(user_id=user_id)

            for job_id in id_list:
                if not existing_user_jobs.filter(job_id=job_id).exists():
                    # Fetch job from either Indeed or LinkedIn
                    fetch_job = Jobs.objects.filter(id=job_id).first()
                    if fetch_job:
                        UserJob.objects.create(user_id=user_id, role=fetch_job.listing_platform, job_id=fetch_job)

            return Response({
                "status": True,
                "message": "Jobs saved successfully"
            }, status=status.HTTP_201_CREATED)
            
        except Exception as swr:
            message = {"status": False}
            (
                message.update(message=str(swr))
                if settings.DEBUG
                else message.update(message="Internal server error")
            )
            return Response(message, status=500)

class GetTrendingJob(APIView):
    def get(self, request):
        try:
            # Define the keywords to search for
            keywords = [
                "Pharma",
                "Pharmaceutical",
                "biotech",
                "lifesciences",
                "therapeutics",
                "medical lab",
                "Biosciences",
                'Vertex Pharmaceuticals', 
                'Takeda', 
                'Gilead Sciences', 
                'Eli Lilly', 
                'Pfizer', 
                'Astrazeneca', 
                'Pharmaceuticals', 
                'Orbital Therapeutics',
                ]

            keyword_filter = Q()
            for keyword in keywords:
                keyword_filter |= Q(company_name__icontains=keyword) | Q(job_title__icontains=keyword)

            # Get the top 5 most viewed LinkedIn jobs
            top_linkedin_jobs = Jobs.objects.filter(
                keyword_filter, 
                listing_platform='LinkedIn'
            ).annotate(
                view_count=Count('jobview')
            ).order_by('-view_count')[:5]

            # Get the top 5 most viewed Indeed jobs
            top_indeed_jobs = Jobs.objects.filter(
                keyword_filter, 
                listing_platform='Indeed'
            ).annotate(
                view_count=Count('jobview')
            ).order_by('-view_count')[:5]


            indeed_serializer = TrendingJobs_Serializer(top_indeed_jobs, many=True)
            linkedin_serializer = TrendingJobs_Serializer(top_linkedin_jobs, many=True)

            return Response({
                'top_linkedin_jobs': linkedin_serializer.data,
                'top_indeed_jobs': indeed_serializer.data
            })

        except Exception as e:
            return Response({"status": False, "message": str(e)}, status=500)



class AddViewsOnJob(APIView):
    permission_classes= [authorization]
    def post(self, request):
        try:
            user_id= request.GET['token']['id']
            job_id= self.request.data.get("job_id")
            if not job_id:
                return Response({"status": False, "message": "job_id required ..."}, status=400)

            user= User.objects.filter(id=user_id).first()
            serializer = JobViewSerializer(data=request.data, context={'user': user})
            if serializer.is_valid():
                serializer.save()
                return Response({"status": True, "message": "Job view added successfully"}, status=200)
            else:
                return Response({"status": False, "message": serializer.errors}, status=400)
            
        except IntegrityError:
            return Response({"status": False, "message": "You have already viewed this job"}, status=400)

        except ValidationError as error:
            if 'Invalid job_id' in error.detail:
                return Response({"status": False, "message": "Invalid job_id"}, status=400)
            else:
                return Response({"status": False, "message": error.detail}, status=400)

        except Exception as swr:
            message = {"status": False}
            (
                message.update(message=str(swr))
                if settings.DEBUG
                else message.update(message="Internal server error")
            )
            return Response(message, status=500)



class AddJobFeedback(APIView):
    permission_classes= [authorization]
    def post(self, request):
        try:
            user_id= request.GET["token"]["id"]
            required_fields= ["job_id", 'feedback']
            validator= uc.keyValidation(True, True, request.data, required_fields)
            if validator:
                return Response (validator, status= status.HTTP_400_BAD_REQUEST)
            
            fetch_job = Jobs.objects.filter(id = request.data.get("job_id")).first()
            if not fetch_job:
                return Response(
                    {
                        "status": False, 
                        "message": "Job not found with this ID"
                    }, status=status.HTTP_400_BAD_REQUEST
            )

            data= {
                "user_id": user_id,
                "job_id": request.data.get("job_id"),
                "feedback_text": request.data.get("feedback")
            }
            fetch_feedback= UserJobFeedback.objects.filter(job_id= fetch_job, user_id= user_id).first()
            jod_feedback_ser= AddUserJobFeedback_Serializer(instance=fetch_feedback, data= data)
            if jod_feedback_ser.is_valid():
                message= "Job Feedback Updated successfully" if fetch_feedback else "Job Feedback Added successfully"
                code_status= status.HTTP_200_OK if fetch_feedback else status.HTTP_201_CREATED
                jod_feedback_ser.save()
                return Response ({"status": True, "message": message}, status= code_status)
            else:
                error= uc.execptionhandler(jod_feedback_ser)
                return Response ({"status": False, "message":error}, status=400)

        except Exception as e:
            return Response(
                {"status": False, "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    