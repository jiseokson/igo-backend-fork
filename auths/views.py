import os
from typing import Union
import requests

from django.contrib.auth import get_user_model

from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from accounts.managers import OAUTH_PROVIDER

User = get_user_model()


class OAuthTokenObtainView(APIView):

    allowed_methods = ('POST',)
    permission_classes = (AllowAny,)

    # redirect_uri = {
    #     'github': 'http://localhost:3000/githubCallback',
    #     'kakao': 'http://localhost:3000/kakaoCallback',
    #     'google': 'http://localhost:3000/googleCallback'
    # }

    access_token_uri = {
        'github': 'https://github.com/login/oauth/access_token',
        'kakao': 'https://kauth.kakao.com/oauth/token',
        'google': 'https://oauth2.googleapis.com/token'
    }

    user_info_uri = {
        'github': 'https://api.github.com/user',
        'kakao': 'https://kapi.kakao.com/v2/user/me',
        'google': 'https://www.googleapis.com/oauth2/v1/userinfo'
    }

    def get_client_id(self, provider):
        return os.getenv('REACT_APP_' + provider.upper() + '_CLIENT_ID')

    def get_client_secret(self, provider):
        return os.getenv('REACT_APP_' + provider.upper() + '_SECRET_KEY')

    def get_redirect_uri(self, provider):
        return os.getenv(provider.upper() + '_REDIRECT_URI')

    def request_access_token(self, provider: str, access_code: str) -> dict:
        if provider == 'github':
            return requests.post(
                self.access_token_uri[provider],
                headers={
                    'Accept': 'application/json'
                },
                params={
                    'client_id': self.get_client_id(provider),
                    'client_secret': self.get_client_secret(provider),
                    'code': access_code,
                }
            )
        elif provider == 'kakao':
            return requests.post(
                self.access_token_uri[provider],
                headers={
                    'Content-type': 'application/x-www-form-urlencoded;charset=utf-8'
                },
                data={
                    'grant_type': 'authorization_code',
                    'client_id': self.get_client_id(provider),
                    'redirect_uri': self.get_redirect_uri(provider),
                    'code': access_code,
                }
            )
        elif provider == 'google':
            return requests.post(
                self.access_token_uri[provider],
                headers={
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                data={
                    'grant_type': 'authorization_code',
                    'client_id': self.get_client_id(provider),
                    'client_secret': self.get_client_secret(provider),
                    'redirect_uri': self.get_redirect_uri(provider),
                    'code': access_code,
                }
            )

    def get_access_token_error(self, provider: str, response: dict) -> str:
        # !!! google의 에러코드 확인된 적 없음
        if provider in ('github', 'kakao', 'google',):
            return response.get('error')

    def get_access_token(self, provider: str, response: dict) -> str:
        if provider in ('github', 'kakao', 'google',):
            return response.get('access_token')

    def reqeust_user_info(self, provider, access_token) -> Union[str, None]:
        return requests.get(
            self.user_info_uri[provider],
            headers={
                'Authorization': f'Bearer {access_token}'
            }
        )

    def get_user_id(self, provider, response):
        if provider in ('github', 'kakao', 'google',):
            return str(response.get('id'))

    def post(self, request, provider: str) -> Response:
        # OAuth 제공 업체 이름, 요청 body의 유효성 검사
        access_code = request.data.get('code')
        if (access_code is None) or (provider not in OAUTH_PROVIDER):
            return Response(
                {
                    'detail': 'Request form is not valid',
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # access code <-> access token 교환
        response = self.request_access_token(provider, access_code)
        if response.status_code != 200:
            return Response(
                {
                    'detail': self.get_access_token_error(provider, response.json())
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )
        access_token = self.get_access_token(provider, response.json())

        # OAuth 제공 업체 provider에게 사용자 정보 요청
        response = self.reqeust_user_info(provider, access_token)
        if response.status_code != 200:
            return Response(
                {
                    'detail': 'OAuth User ID not found'
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        oauth_id = self.get_user_id(provider, response.json())

        # OAuth 인증으로 가입한 사용자 정보 탐색
        try:
            user = User.oauths.filter(
                oauth_provider=provider).get(oauth_id=oauth_id)
        except User.DoesNotExist as e:
            user = User.oauths.create_user(
                oauth_provider=provider, oauth_id=oauth_id)

        # JWT 발급, 응답
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'is_register': user.is_register,
            },
            status=status.HTTP_200_OK,
        )
