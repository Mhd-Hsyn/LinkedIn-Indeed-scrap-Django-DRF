import jwt
import datetime
import re
from webapi.models import *
from decouple import config
import string
import secrets
from google.oauth2 import id_token
from google.auth.transport import requests


def requireKeys(reqArray, requestData):
    try:
        for j in reqArray:
            if not j in requestData:
                return False

        return True

    except:
        return False


def allfieldsRequired(reqArray, requestData):
    try:
        for j in reqArray:
            if len(requestData[j]) == 0:
                return False

        return True

    except:
        return False


def checkemailforamt(email):
    emailregix = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"

    if re.match(emailregix, email):
        return True

    else:
        return False


def passwordLengthValidator(passwd):
    if len(passwd) >= 8 and len(passwd) <= 20:
        return True

    else:
        return False


def keyValidation(keyStatus, reqStatus, requestData, requireFields):
    if keyStatus:
        keysStataus = requireKeys(requireFields, requestData)
        if not keysStataus:
            return {
                "status": False,
                "message": f"{requireFields} all keys are required",
            }

    if reqStatus:
        requiredStatus = allfieldsRequired(requireFields, requestData)
        if not requiredStatus:
            return {"status": False, "message": "All Fields are Required"}


def makedict(obj, key, imgkey=False):
    dictobj = {}

    for j in range(len(key)):
        keydata = getattr(obj, key[j])
        if keydata:
            dictobj[key[j]] = keydata

    if imgkey:
        imgUrl = getattr(obj, key[-1])
        if imgUrl:
            dictobj[key[-1]] = imgUrl.url
        else:
            dictobj[key[-1]] = ""

    return dictobj


def generate_random_password(length=12):
    characters = string.ascii_letters + string.digits
    password = "".join(secrets.choice(characters) for _ in range(length))
    return password


def exceptionhandler(val):
    error_messages = []

    if isinstance(val, dict):
        if "error" in val:
            error_messages.append(val["error"])
    else:
        for field, errors in val.errors.items():
            error_message = f"{field}: {', '.join(errors)}"
            error_messages.append(error_message)

    return ", ".join(error_messages)


def blacklisttoken(id, token):
    try:
        whitelistToken.objects.get(user=id, token=token).delete()
        return True

    except:
        return False


def all_blacklisttoken(id):
    try:
        whitelistToken.objects.filter(user=id).delete()
        return True

    except:
        return False


def generatedToken(fetchuser, authKey, totaldays, request):
    try:
        access_token_payload = {
            "id": str(fetchuser.id),
            "email": fetchuser.email,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(days=totaldays),
            "iat": datetime.datetime.utcnow(),
        }

        userpayload = {
            "id": str(fetchuser.id),
            "email": fetchuser.email,
        }

        access_token = jwt.encode(access_token_payload, authKey, algorithm="HS256")
        userwhitelistToken(user=fetchuser, token=access_token).save()
        return {"status": True, "token": access_token, "payload": userpayload}

    except Exception as e:
        return {
            "status": False,
            "message": "Something went wrong in token creation",
            "details": str(e),
        }


def superadmingeneratedToken(fetchuser, authKey, totaldays, request):
    try:
        access_token_payload = {
            "id": str(fetchuser.id),
            "email": fetchuser.email,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(days=totaldays),
            "iat": datetime.datetime.utcnow(),
        }

        userpayload = {
            "id": str(fetchuser.id),
            "email": fetchuser.email,
        }

        access_token = jwt.encode(access_token_payload, authKey, algorithm="HS256")
        whitelistToken(user=fetchuser, token=access_token).save()
        return {"status": True, "token": access_token, "payload": userpayload}

    except Exception as e:
        return {
            "status": False,
            "message": "Something went wrong in token creation",
            "details": str(e),
        }


def User_Token(fetchuser):
    """
    User Generate Token When User Login
    """
    try:
        secret_key = config("User_jwt_token")
        totaldays = 1
        token_payload = {
            "id": str(fetchuser.id),
            "email": fetchuser.email,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(days=totaldays),
            "iat": datetime.datetime.utcnow(),
        }
        detail_payload = {
            "id": str(fetchuser.id),
            "email": fetchuser.email,
            "fullname": fetchuser.fullname,
        }

        token = jwt.encode(token_payload, key=secret_key, algorithm="HS256")
        print(token)
        print(fetchuser)
        userwhitelistToken(user=fetchuser, token=token).save()
        return {"status": True, "token": token, "payload": detail_payload}
    except Exception as e:
        return {"status": False, "message": f"Error during generationg token {str(e)}"}


def execptionhandler(val):
    if "error" in val.errors:
        error = val.errors["error"][0]
    else:
        key = next(iter(val.errors))
        error = key + ", " + val.errors[key][0]

    return error


def makedict(obj, key, imgkey=False):
    dictobj = {}
    print(obj)

    for j in range(len(key)):
        keydata = getattr(obj, key[j])
        if keydata:
            dictobj[key[j]] = keydata

    if imgkey:
        imgUrl = getattr(obj, key[-1])
        if imgUrl:
            dictobj[key[-1]] = imgUrl.url
        else:
            dictobj[key[-1]] = ""
    print(dictobj)
    return dictobj


def authTokengoogle(token):
    try:
        idinfo = id_token.verify_oauth2_token(
            token, requests.Request(), config("CLIENT_ID")
        )
        return idinfo
    except ValueError as e:
        # Handle the error (e.g., log it or return an error response)
        print("Error:", str(e))
        return False


from decouple import config
import requests


def verify_google_access_token(access_token):
    try:
        # Validate the access token using the Google API tokeninfo endpoint
        response = requests.get(
            f"https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={access_token}"
        )

        if response.status_code == 200:
            id_info = response.json()

            # Print or log the id_info for debugging
            print("id_info:", id_info)

            # Check if id_info is not None and has the expected attributes
            if id_info and "audience" in id_info:
                # Verify that the client ID matches
                if id_info["audience"] == config("CLIENT_ID"):
                    return id_info
                else:
                    print("Invalid client ID in token.")
            else:
                print("Invalid response from tokeninfo endpoint.")

        else:
            print(f"Token validation failed. Response: {response.text}")

    except Exception as e:
        # Handle other exceptions if needed
        print("Error:", str(e))

    return None


def verify_facebook_access_token(access_token):
    import requests

    response = requests.get(
        f"https://graph.facebook.com/v17.0/me?fields=id,name,email&access_token={access_token}"
    )
    if response.status_code == 200:
        user_info = response.json()
        return user_info
    else:
        return None
