""" tts/production.py """

import os
from .settings import * # pylint: disable=wildcard-import, unused-wildcard-import

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Configure the domain name using the environment variable
# that Azure automatically creates for us.
ALLOWED_HOSTS = [
  os.environ['WEBSITE_HOSTNAME'],
#  os.environ['ADDITIONAL_ALLOWED_HOSTS'],
  '169.254.131.10',
  '169.254.131.7',
  '169.254.131',
  '20.105.232.53'
  ]

SECRET_KEY = os.environ['SECRET_KEY']

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'

SPEECH_KEY = os.environ['SPEECH_KEY']
SPEECH_SERVICE_REGION = os.environ['SPEECH_SERVICE_REGION']

AZURE_STORAGE_ACCOUNT_NAME = os.environ['AZURE_STORAGE_ACCOUNT_NAME']
AZURE_STORAGE_ACCOUNT_KEY = os.environ['AZURE_STORAGE_ACCOUNT_KEY']
AZURE_CONTAINER_NAME = os.environ['AZURE_CONTAINER_NAME']

TRANSLATOR_KEY = os.environ['TRANSLATOR_KEY']
TRANSLATOR_SERVICE_REGION = os.environ['TRANSLATOR_SERVICE_REGION']
TRANSLATOR_ENDPOINT = os.environ['TRANSLATOR_ENDPOINT']

CLIENT_ID = os.environ['CLIENT_ID']
TENANT_ID = os.environ['TENANT_ID']

conn_str = os.environ['AZURE_POSTGRESQL_CONNECTIONSTRING']
conn_str_params = {pair.split('=')[0]: pair.split('=')[1] for pair in conn_str.split(' ')}
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': conn_str_params['dbname'],
        'HOST': conn_str_params['host'],
        'USER': conn_str_params['user'],
        'PASSWORD': conn_str_params['password'],
    }
}

SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_HSTS_SECONDS = 3600
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True

# Cross-Origin-Opener-Policy header
SECURE_CROSS_ORIGIN_OPENER_POLICY = 'same-origin'
