""" api/middleware/MicrosoftTokenMiddleware.py """

import requests
from django.http import JsonResponse

class AccessTokenMiddleware:
    """Middleware for ensuring that the requests sent to the backend come from authorized users"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        """This method activates each time the middleware is called"""

        # Check that POST, PUT, PATCH and DELETE requests come from authorized users
#        if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
#            token = self.get_token_from_header(request)
#            if not token:
#                return JsonResponse(
#                    {'error': 'Authentication credentials were not provided'},
#                    status=401
#                )
#
#            # Validate the token by calling the Microsoft Graph API
#            if not self.validate_token(token):
#                return JsonResponse({'error': 'Invalid or expired token'}, status=401)

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

        graph_api_url = "https://graph.microsoft.com/v1.0/me"
        headers = {
            "Authorization": f"Bearer {token}"
        }

        # Make a request to the Microsoft Graph API to validate the token
        api_response = requests.get(graph_api_url, headers=headers, timeout=10)

        # If the API responds with a 200 status code, the token is valid
        if api_response.status_code == 200:
            return True

        return False
