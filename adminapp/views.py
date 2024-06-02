from django.db.models import Q
from unidecode import unidecode
from datetime import datetime, timedelta
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from django.conf import settings
from decouple import config
from Usable import usable as uc
from webapi.models import *
from rest_framework.decorators import action
from rest_framework import status
from Usable.permissions import *
from django.contrib.auth.hashers import check_password
import Usable.emailpattern as verfied
import random
from .serilizer import *
from webapi.serilizer import *
from .pagination import *

class AdminAuthViewset(ModelViewSet):
    queryset = SuperAdmin.objects.all()

    @action(detail=False, methods=["POST"])
    def signup(self, request):
        try:
            requireFields = [
                "email",
                "password",
                "fname",
                "lname",
                "contact",
                "address",
            ]
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

            serializer = SuperAdminsSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            email = serializer.validated_data["email"]
            if SuperAdmin.objects.filter(email=email).exists():
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

            user = SuperAdmin.objects.filter(email=email).first()

            if user and check_password(password, user.password):
                generate_auth = uc.superadmingeneratedToken(
                    user, config("Superadmin_jwt_token"), 100, request
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

                fetchadmin = SuperAdmin.objects.filter(email=email).first()

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
    def verify_otp(self, request):
        try:
            ##validator keys and required
            requireFields = ["otp", "id"]
            validator = uc.keyValidation(True, True, request.data, requireFields)

            if validator:
                return Response(validator,status=status.HTTP_400_BAD_REQUEST)

            else:
                otp = request.data["otp"]
                id = request.data["id"]
                fetchuser = SuperAdmin.objects.filter(id=id).first()
                if fetchuser:
                    if fetchuser.OtpStatus and fetchuser.OtpCount < 3:
                        if fetchuser.Otp == int(otp):
                            fetchuser.Otp = 0
                            fetchuser.OtpStatus = True
                            fetchuser.save()
                            return Response(
                                {
                                    "status": True,
                                    "message": "Otp verified",
                                    "email": str(fetchuser.email),
                                },
                                status=status.HTTP_200_OK,
                            )
                        else:
                            fetchuser.OtpCount += 1
                            fetchuser.save()
                            if fetchuser.OtpCount >= 3:
                                fetchuser.Otp = 0
                                fetchuser.OtpCount = 0
                                fetchuser.OtpStatus = False
                                fetchuser.save()
                                return Response(
                                    {
                                        "status": False,
                                        "message": f"Your OTP is expired . . . Kindly get OTP again",
                                    },status=status.HTTP_400_BAD_REQUEST
                                )
                            return Response(
                                {
                                    "status": False,
                                    "message": f"Your OTP is wrong . You have only {3- fetchuser.OtpCount} attempts left ",
                                },status=status.HTTP_400_BAD_REQUEST
                            )
                    return Response(
                        {
                            "status": False,
                            "message": "Your OTP is expired . . . Kindly get OTP again",
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                return Response(
                    {"status": False, "message": "User not exist"}, status=404
                )

        except Exception as e:
            message = {"status": False}
            message.update(message=str(e)) if settings.DEBUG else message.update(
                message="Internal server error"
            )
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=["POST"])
    def reset_password(self, request):
        try:
            requireFeild = ["id", "newpassword"]
            validator = uc.keyValidation(True, True, request.data, requireFeild)
            if validator:
                return Response(validator, status=status.HTTP_400_BAD_REQUEST)

            id = request.data["id"]
            newpassword = request.data["newpassword"]
            if not uc.passwordLengthValidator(newpassword):
                return Response(
                    {
                        "status": False,
                        "error": "Password length must be greater than 8",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            fetchuser = SuperAdmin.objects.filter(id=id).first()
            if fetchuser:
                if fetchuser.OtpStatus and fetchuser.Otp == 0:
                    fetchuser.password = handler.hash(newpassword)
                    fetchuser.OtpStatus = False
                    fetchuser.OtpCount = 0
                    fetchuser.save()
                    return Response(
                        {
                            "status": True,
                            "message": "Password updates successfully ",
                        },
                        status=status.HTTP_200_OK,
                    )
                return Response(
                    {"status": False, "message": "Token not verified !!!!"}, status=status.HTTP_400_BAD_REQUEST
                )
            return Response(
                {"status": False, "message": "User Not Exist !!!"}, status=404
            )
        except Exception as e:
            message = {"status": False}
            message.update(message=str(e)) if settings.DEBUG else message.update(
                message="Internal server error"
            )
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SuperAdminApiViewset(ModelViewSet):
    permission_classes = [adminauthorization]

    @action(detail=False, methods= ["GET"])
    def admin_logout(self, request):
        try:
            uc.blacklisttoken(request.GET["token"]['id'], request.META['HTTP_AUTHORIZATION'][7:])
            return Response ({"status": True, "message": "Logout Successfully"}, status= 200)
        except Exception as e:
            return Response({"status": False, "error": f"Something wrong {str(e)}"}, status= 400)

    @action(detail= False, methods= ['POST'])
    def admin_change_pass(self, request):
        try:
            requireFeilds = ["oldpassword", "newpassword"]
            feild_status = uc.keyValidation(True, True, request.data, requireFeilds)
            if feild_status:
                return Response(feild_status, status= 400)
                    
            admin_id = request.GET["token"]["id"]
            fetchuser = SuperAdmin.objects.filter(id = admin_id).first()
            if handler.verify(request.data['oldpassword'],fetchuser.password):
                if uc.passwordLengthValidator(request.data['newpassword']):
                    fetchuser.password = handler.hash(request.data["newpassword"])
                    # delete old token
                    uc.all_blacklisttoken(fetchuser)
                    # generate new token
                    token = uc.superadmingeneratedToken(fetchuser,config("Superadmin_jwt_token"), 100, request) 
                    fetchuser.save()
                    return Response({"status": True, "message": "Password Successfully Changed", "token" : token["token"]}, status = 200)
                else:
                    return Response({"status":False, "error":"New Password Length must be graterthan 8"}, status= 400)
            else:
                return Response({"status":False, "error":"Old Password not verified"}, status= 400)
        except Exception as e:
            return Response({"status": False, "error": str(e)}, status= 400)

    @action(detail=False, methods=["GET", "PUT"])
    def profile(self, request):
        try:
            if request.method == "GET":
                fetchuser = SuperAdmin.objects.filter(
                    id=request.GET["token"]["id"]
                ).first()
                if fetchuser:
                    admin_profile_ser= AdminProfileSerializer(fetchuser)
                    return Response({"status": True,  "data": admin_profile_ser.data}, status= 200)
                return Response({"status": False, "message": "Admin not found" }, status=400)

            if request.method == "PUT":
                requireFields = ["contact", "fname", "lname", "address"]
                validator = uc.keyValidation(True, True, request.data, requireFields)
                if validator:
                    return Response(validator, status=422)
                
                fetchuser = SuperAdmin.objects.filter(id=request.GET["token"]["id"]).first()
                if fetchuser:
                    admin_ser= AdminProfileSerializer(instance=fetchuser, data=request.data)
                    if admin_ser.is_valid():
                        admin_ser.save()
                        return Response(
                            {
                                "status": True,
                                "message": "Update Successfully",
                                "data": admin_ser.data,
                            }, status=200
                        )
                    else:
                        error= uc.exceptionhandler(admin_ser)
                        return Response(
                            {
                                "status": False,
                                "message": error
                            }, status=400
                        )
                else:
                    return Response(
                        {
                            "status": False,
                            "message": "User not found"
                        }, status=400
                    )

        except Exception as e:
            message = {"status": False}
            (
                message.update(message=str(e))
                if settings.DEBUG
                else message.update(message="Internal server error")
            )
            return Response(message, status=500)

    


class UserAdminApiViewset(ModelViewSet):
    permission_classes = [adminauthorization]

    @action(detail=False, methods=["GET"])
    def dashboard(self, request):
        fetch_all_users = User.objects.all().count()
        fetch_all_jobs= Jobs.objects.all().count()
        fetch_all_linkedin= Jobs.objects.filter(listing_platform= "LinkedIn").count()
        fetch_all_indeed= Jobs.objects.filter(listing_platform= "Indeed").count()

        return Response ({
            "all_users_count": fetch_all_users,
            "all_jobs_count":fetch_all_jobs,
            "all_linkedin_jobs_count": fetch_all_linkedin,
            "all_indeed_jobs_count": fetch_all_indeed
        })


    @action(detail=False, methods=["GET"])
    def profiles(self, request):
        fetch_users = User.objects.all()
        paginator = UsersPagination()
        paginated_users = paginator.paginate_queryset(fetch_users, request)
        job_ser = FetchUsersSerializer(paginated_users, many=True)
        return paginator.get_paginated_response(job_ser.data)

    @action(detail=False, methods=["GET"])
    def get_user_detail(self, request):
        user_id= request.GET.get("id", None)
        if not user_id:
            return Response(
                {
                    "status": False,
                    "message": "user id req in params"
                }, status=400
            )
        fetch_user = User.objects.filter(id = user_id).first()
        if fetch_user:
            user_ser = FetchUsersAllDetail_Serializer(fetch_user)
            return Response({"status": True, "data": user_ser.data}, status=status.HTTP_200_OK)
        else :
            return Response(
                {
                    "status": False,
                    "message": "job not found"
                }, status=400
            )

    @action(detail=False, methods=["PUT"])
    def update_user_status(self, request):
        try:
            serializer = UserStatusUpdateSerializer(data=request.data)
            if serializer.is_valid():
                user_id = request.data.get("id")
                status_value = request.data.get("status")

                try:
                    user = User.objects.get(id=user_id)
                    if status_value == 'true':
                        status_value= True
                    elif status_value== 'false':
                        status_value= False
                    user.status = status_value
                    user.save()
                    return Response(
                        {"status": "User status updated successfully"},
                        status=status.HTTP_200_OK,
                    )
                except User.DoesNotExist:
                    return Response(
                        {"status": False, "message": "User not found"}, status=status.HTTP_404_NOT_FOUND
                    )
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"status": False, "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AdminJobRightViewset(ModelViewSet):
    permission_classes = [adminauthorization]
    queryset = Jobs.objects.all()

    @action(detail=False, methods=["GET"])
    def get_all_jobs(self, request):
        fetch_jobs = Jobs.objects.all().order_by("-created_at")
        paginator = JobsPagination()
        paginated_jobs = paginator.paginate_queryset(fetch_jobs, request)
        job_ser = JobsTitle_Serializer(paginated_jobs, many=True)
        return paginator.get_paginated_response(job_ser.data)


    @action(detail=False, methods=["GET"])
    def get_job_detail(self, request):
        try:

            job_id= request.GET.get("id", None)
            if not job_id:
                return Response(
                    {
                        "status": False,
                        "message": "job id req in params"
                    }, status=400
                )
            fetch_job = Jobs.objects.filter(id = job_id).first()
            if fetch_job:
                job_ser = JobAndFeedback_Serializer(fetch_job)
                return Response({"status": True, "data": job_ser.data}, status=status.HTTP_200_OK)
            else :
                return Response(
                    {
                        "status": False,
                        "message": "job not found"
                    }, status=400
                )
        except Exception as  e:
            return Response(
                {"status": False, "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    

    @action(detail=False, methods=['POST'])
    def add_job(self, request):
        try:
            required_fields= ['job_title', 'company_name', 'city','company_location', 'employment_type', 'seniority_level', 'job_description']
            validator= uc.keyValidation(True, True, request.data, required_fields)
            if validator:
                return Response (validator, status= status.HTTP_400_BAD_REQUEST)
            
            job_ser= AddJob_Serializer(data= request.data)
            if job_ser.is_valid():
                job_ser.save()
                return Response ({"status": True, "message":"Job added successfully"}, status=201)
            else:
                error= uc.execptionhandler(job_ser)
                return Response ({"status": False, "message":error}, status=400)


        except Exception as e:
            return Response(
                {"status": False, "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
    @action(detail=False, methods=['PUT'])
    def update_job(self, request):
        try:
            required_fields= ['id', 'job_title', 'company_name', 'city','company_location', 'employment_type', 'seniority_level', 'job_description']
            validator= uc.keyValidation(True, True, request.data, required_fields)
            if validator:
                return Response (validator, status= status.HTTP_400_BAD_REQUEST)
            
            fetch_job = Jobs.objects.filter(id = request.data.get("id")).first()
            if not fetch_job:
                return Response(
                    {
                        "status": False, 
                        "message": "Job not found with this ID"
                    }, status=status.HTTP_400_BAD_REQUEST
            )
            job_ser= AddJob_Serializer(instance=fetch_job, data= request.data)
            if job_ser.is_valid():
                job_ser.save()
                return Response ({"status": True, "message":"Job Updated successfully"}, status=200)
            else:
                error= uc.execptionhandler(job_ser)
                return Response ({"status": False, "message":error}, status=400)

        except Exception as e:
            return Response(
                {"status": False, "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['DELETE'])
    def delete_job(self, request):
        try:
            required_fields= ['id']
            validator= uc.keyValidation(True, True, request.data, required_fields)
            if validator:
                return Response (validator, status= status.HTTP_400_BAD_REQUEST)
            
            fetch_job = Jobs.objects.filter(id = request.data.get("id")).first()
            if not fetch_job:
                return Response(
                    {
                        "status": False, 
                        "message": "Job not found with this ID"
                    }, status=status.HTTP_400_BAD_REQUEST
            )
            fetch_job.delete()
            return Response ({"status": True, "message":"Job Deleted successfully"}, status=200)

        except Exception as e:
            return Response(
                {"status": False, "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    

    @action(detail=False, methods=["GET"])
    def get_filter_jobs(self, request):
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


    @action(detail=False, methods=['POST'])
    def add_job_feedback(self, request):
        try:
            admin_id= request.GET["token"]["id"]
            required_fields= ["id", 'feedback']
            validator= uc.keyValidation(True, True, request.data, required_fields)
            if validator:
                return Response (validator, status= status.HTTP_400_BAD_REQUEST)
            
            fetch_job = Jobs.objects.filter(id = request.data.get("id")).first()
            if not fetch_job:
                return Response(
                    {
                        "status": False, 
                        "message": "Job not found with this ID"
                    }, status=status.HTTP_400_BAD_REQUEST
            )

            data= {
                "admin_id": admin_id,
                "job": request.data.get("id"),
                "feedback": request.data.get("feedback")
            }
            fetch_feedback= JobFeedback.objects.filter(job= fetch_job).first()
            jod_feedback_ser= AddJobFeedback_Serializer(instance=fetch_feedback, data= data)
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
    
    @action(detail=False, methods=['DELETE'])
    def delete_job_feedback(self, request):
        try:
            admin_id= request.GET["token"]["id"]
            required_fields= ["id"]
            validator= uc.keyValidation(True, True, request.data, required_fields)
            if validator:
                return Response (validator, status= status.HTTP_400_BAD_REQUEST)
            
            fetch_job = Jobs.objects.filter(id = request.data.get("id")).first()
            if not fetch_job:
                return Response(
                    {
                        "status": False, 
                        "message": "Job not found with this ID"
                    }, status=status.HTTP_400_BAD_REQUEST
            )

            fetch_feedback= JobFeedback.objects.filter(job= fetch_job).first()
            if fetch_feedback:
                fetch_feedback.delete()
                message= "Job Feedback Deleted successfully" 
                code_status= status.HTTP_200_OK
                return Response ({"status": True, "message": message}, status= code_status)
            else:
                return Response ({"status": False, "message":"feedback not found"}, status=400)


        except Exception as e:
            return Response(
                {"status": False, "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    

    @action(detail=False, methods=['GET'])
    def get_job_feedback(self, request):
        try:
            admin_id= request.GET["token"]["id"]
            required_fields= ["job_id"]
            validator= uc.keyValidation(True, True, request.GET, required_fields)
            if validator:
                return Response (validator, status= status.HTTP_400_BAD_REQUEST)
            
            fetch_jobfeedback = JobFeedback.objects.filter(job_id = request.GET.get("job_id")).first()
            feedback= ""
            if fetch_jobfeedback:
                feedback= fetch_jobfeedback.feedback
            
            return Response({'status': True, "feedback": feedback}, status= 200)


        except Exception as e:
            return Response(
                {"status": False, "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class FeedbackOnJob(ModelViewSet):
    permission_classes = [adminauthorization]

    @action (detail= False, methods=['GET'])
    def user_all_feedbacks(self, request):
        try :
            fetch_all_feedbacks= UserJobFeedback.objects.all()
            paginator = UsersJobsFeedbackPagination()
            paginated_feedbacks = paginator.paginate_queryset(fetch_all_feedbacks, request)
            ser= UserAllFeedbacksOnJob_Serializer(paginated_feedbacks, many=True)
            return paginator.get_paginated_response(ser.data)

        except Exception as e:
            return Response(
                {"status": False, "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


    @action (detail= False, methods=['GET'])
    def admin_all_feedbacks(self, request):
        try:
            fetch_all_feedbacks= JobFeedback.objects.all()
            paginator = UsersJobsFeedbackPagination()
            paginated_feedbacks = paginator.paginate_queryset(fetch_all_feedbacks, request)
            ser= AdminAllFeedbacksOnJob_Serializer(paginated_feedbacks, many=True)
            return paginator.get_paginated_response(ser.data)

        except Exception as e:
            return Response(
                {"status": False, "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


