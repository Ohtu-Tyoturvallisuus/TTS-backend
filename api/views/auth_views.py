""" api/views/auth_views.py """

import random
import string
import jwt
from django.conf import settings
from rest_framework import generics, status
from rest_framework.response import Response

from api.models import Account
from api.serializers import SignInSerializer

# <POST> /api/signin/
class SignIn(generics.CreateAPIView):
    """Class for SignIn"""
    serializer_class = SignInSerializer

    def create(self, request, *args, **kwargs):
        username = request.data.get('username')
        user_id = request.data.get('id')
        guest = request.data.get('guest')
        if not username:
            return Response({"error": "Username is required"}, status=status.HTTP_400_BAD_REQUEST)

        if guest or not user_id:
            characters = string.ascii_letters + string.digits
            user_id = ''.join(random.choice(characters) for _ in range(64))

        payload = {
            'username': username,
            'user_id': user_id,
        }

        token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

        _, created = Account.objects.get_or_create(username=username, user_id=user_id)
        if created:
            message = f"User '{username}' created and signed in successfully"
            status_code = status.HTTP_201_CREATED
        else:
            message = f"User '{username}' signed in successfully"
            status_code = status.HTTP_200_OK

        return Response({"message": message, 'access_token': token}, status=status_code)
