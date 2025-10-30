from django.conf import settings
from rest_framework import response
from rest_framework.response import Response
from authentication.models import User
from payments.models import Traveller

import jwt

def generate_user_response(user, refresh=None, **kwargs):
    role = user.role.name if user.role else "Normal User"
    
    try:
        traveller = Traveller.objects.get(user=user)
    except Traveller.DoesNotExist:
        traveller = None

    if traveller:
        user_data = {
            "role": role,
            "user_id": user.id,
            "company_name": user.company_id.name if user.company_id else None,
            "traveller_id": traveller.id,
            "first_name": traveller.user.first_name,
            "last_name": traveller.user.last_name,
            "email": traveller.user.email,
            "username": traveller.user.username,
            "phone": traveller.phone,
            "cloudflare_image_url": traveller.user.cloudflare_image_url,
            "acceptOffers": traveller.accept_offers,
            "is_admin": user.is_admin,
            "is_superuser": user.is_superuser,
            "is_staff": user.is_staff,
            "is_active": user.is_active,
            "created_by": traveller.created_by,
            "updated_by": traveller.updated_by,
            "created_at": traveller.created_at,
            "updated_at": traveller.updated_at,
        }
    else:
        user_data = {
            "role": role,
            "user_id": user.id,
            "company_name": user.company_id.name if user.company_id else None,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "username": user.username,
            "phone": getattr(user, "primary_phone", None),
            "cloudflare_image_url": user.cloudflare_image_url,
            "is_admin": user.is_admin,
            "is_superuser": user.is_superuser,
            "is_staff": user.is_staff,
            "is_active": user.is_active,
            "created_by": user.created_by.first_name if user.created_by else None,
            "updated_by": user.updated_by.first_name if user.updated_by else None,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
        }
    
    response_data = {}
    if kwargs.get("is_admin_login") == True:
        # শুধুমাত্র is_admin_login এ token গুলো body তে add করো
        # response_data["refreshToken"] = str(refresh)
        response_data["accessToken"] = str(refresh.access_token)
    # response_data te user er full details add kora hoilo
    response_data["user"] = user_data

    #  <class 'rest_framework.response.Response'> rest_framework er response er Response 
    # class create kora hoilo, response data diye 'response' naam e tar akta instance create 
    # kora hoilo.
    response = Response(response_data)


    if refresh:
        if kwargs.get("is_login") == True:
            # refresh and access token set as HTTPOnly cookie
            response.set_cookie(
                key="refreshToken",
                value=str(refresh),
                httponly=True,
                secure=not settings.DEBUG,
                samesite="Lax",
                path="/",
                max_age = 24 * 60 * 60,
            )
            response.set_cookie(
                key="accessToken",
                value=str(refresh.access_token),
                httponly=True,
                secure=not settings.DEBUG,
                samesite="Lax",
                path="/",
                max_age = 15 * 60,
            )
        elif kwargs.get("is_refresh") == True:
            response.set_cookie(
                key="accessToken",
                value=str(refresh.access_token),
                httponly=True,
                secure=not settings.DEBUG,
                samesite="Lax",
                path="/",
                max_age = 15 * 60,
            )
        elif kwargs.get("is_admin_login") == True:
            print("from is_admin_login")
            response.set_cookie(
                key="refreshToken",
                value=str(refresh),
                # httponly=True,
                secure=not settings.DEBUG,
                samesite="Lax",
                path="/",
                max_age = 24 * 60 * 60,
            )
            response.set_cookie(
                key="accessToken",
                value=str(refresh.access_token),
                # httponly=True,
                secure=not settings.DEBUG,
                samesite="Lax",
                path="/",
                max_age = 15 * 60,
            )
            print("type of response : ", type(response))
            response['refreshToken']=str(refresh)
            response['accessToken']=str(refresh.access_token)

    return response
