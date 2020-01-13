import logging
from json import JSONDecodeError
import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response

# ======================================================================================================================
# SSO AUTH backend
# ======================================================================================================================

User = get_user_model()
logger = logging.getLogger(__name__)

SSO_HEADER = getattr(settings, "SSO_HEADER", "Bearer")


def get_token(request):
    """
    Getting auth token from request data
    :param request: Http Request object
    :return: token string OR None
    """
    authorization = request.META.get('HTTP_AUTHORIZATION', "")
    if authorization.startswith('Token'):
        return authorization.split(" ")[-1]
    return None


def get_sso_response(url, function_method, data={}, headers={}):
    """
    Make request to SSO service
    :param url: full URL request
    :param function_method: method from requests library : requests.post OR requests.get
    :param data: request data, by default it's empty dict
    :param headers: request headers, by default it's empty dict
    :return: SSO response
    """
    try:
        request = function_method(url, json=data, headers=headers)
        response = Response(request.json(), status=request.status_code)
    except (requests.exceptions.RequestException, JSONDecodeError):
        logger.warning("Response error from: %s", url)
        response = Response({"detail": "SSO error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return response


def get_sso_user(request):
    """
    Getting User data from SSO service
    :param request: Http Request object
    :return: data from response OR empty dict
    """
    data = {}
    token = get_token(request)
    if token:
        response = get_sso_response(settings.SSO_AUTH_URL, requests.post, {"token": token})
        if response.status_code == status.HTTP_200_OK:
            data = response.data
        elif response.status_code == status.HTTP_401_UNAUTHORIZED:
            raise AuthenticationFailed()
    return data


class ExternalAuthBackend(BaseAuthentication):
    """
    RestFramework Authentication Backend, for insert this to project, need to add this in the settings:
    REST_FRAMEWORK ={
        DEFAULT_AUTHENTICATION_CLASSES : (drf_util.backends.ExternalAuthBackend,),
        ...}
    SSO_AUTH_URL = "http://my-sso.example/auth-to-user"
    """

    def authenticate(self, request, **kwargs):
        """
        Authenticate User by request
        :param request: Http Request object
        :param kwargs: not needed, it's from BaseAuthentication
        :return: tuple OR None
        """
        user = ExternalAuthBackend.get_user(request)
        return (user, None) if user else None

    @staticmethod
    def get_user(request):
        """
        Getting User by request
        :param request: Http Request object
        :return: user OR None
        """
        # getting user from SSO service
        data_response = get_sso_user(request)
        if data_response and data_response.get("username"):
            email = data_response.get("email")
            # create user in local User model
            user, _ = User.objects.get_or_create(username=data_response.get("username"))
            if not user.email and email:
                user.email = email
                user.save()
            return user
        return None

    def authenticate_header(self, request):
        return "Not found"
