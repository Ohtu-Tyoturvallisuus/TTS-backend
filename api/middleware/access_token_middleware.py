""" api/middleware/MicrosoftTokenMiddleware.py """

import jwt
from jwt import ExpiredSignatureError, InvalidTokenError
from django.http import JsonResponse
from django.conf import settings

class AccessTokenMiddleware:
    """Middleware for ensuring that the requests sent to the backend come from authorized users"""

    def __init__(self, get_response):
        self.get_response = get_response
        self.jwt_secret_key = settings.SECRET_KEY

    def __call__(self, request):
        """This method activates each time the middleware is called"""

        # Allow admin panel and the sign-in endpoint without a token
        if request.path.startswith('/admin/') or request.path == '/api/signin/':
            return self.get_response(request)

        # Check that POST, PUT, PATCH and DELETE requests come from authorized users
        if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            token = self.get_token_from_header(request)
            if not token:
                return JsonResponse(
                    {'error': 'Authentication credentials were not provided'},
                    status=401
                )

            if not self.validate_token(token):
                return JsonResponse({'error': 'Invalid or expired token'}, status=401)

        # Proceed with the request if token is valid
        return self.get_response(request)

    def get_token_from_header(self, request):
        """Method for extracting the access token from the authorization header"""

        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            return auth_header.split(' ')[1]
        return None

    def validate_token(self, token):
        """Method for validating the access token"""

        try:
            # Decode the token using the secret key
            jwt.decode(token, self.jwt_secret_key, algorithms=["HS256"])
            return True
        except ExpiredSignatureError:
            return False  # Token is expired
        except InvalidTokenError:
            return False  # Token is invalid
