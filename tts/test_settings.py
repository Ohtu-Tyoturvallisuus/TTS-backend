"""Settings module for the tests"""
from .settings import * # pylint: disable=wildcard-import, unused-wildcard-import

# Disable the AccessTokenMiddleware for tests
MIDDLEWARE = [
    mw for mw in MIDDLEWARE if mw != "api.middleware.access_token_middleware.AccessTokenMiddleware"
]

# Any other test-specific configurations can go here
