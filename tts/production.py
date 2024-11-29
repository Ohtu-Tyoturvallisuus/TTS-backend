""" tts/production.py """

import os
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from .settings import * # pylint: disable=wildcard-import, unused-wildcard-import

# Initialize the Key Vault client
key_vault_name = os.getenv('KEY_VAULT_NAME')
key_vault_uri = f"https://{key_vault_name}.vault.azure.net"
credential = DefaultAzureCredential()
client = SecretClient(vault_url=key_vault_uri, credential=credential)

def get_secret(secret_name):
    """
    Retrieve the value of a secret from Azure Key Vault.

    Args:
        secret_name (str): The name of the secret to retrieve.

    Returns:
        str: The value of the retrieved secret.
    """
    return client.get_secret(secret_name).value

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

SECRET_KEY = get_secret('SECRET-KEY')

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'

SPEECH_KEY = get_secret('SPEECH-KEY')
SPEECH_SERVICE_REGION = get_secret('SPEECH-SERVICE-REGION')

AZURE_STORAGE_ACCOUNT_NAME = get_secret('AZURE-STORAGE-ACCOUNT-NAME')
AZURE_STORAGE_ACCOUNT_KEY = get_secret('AZURE-STORAGE-ACCOUNT-KEY')
AZURE_CONTAINER_NAME = get_secret('AZURE-CONTAINER-NAME')

TRANSLATOR_KEY = get_secret('TRANSLATOR-KEY')
TRANSLATOR_SERVICE_REGION = get_secret('TRANSLATOR-SERVICE-REGION')
TRANSLATOR_ENDPOINT = get_secret('TRANSLATOR-ENDPOINT')

CLIENT_ID = get_secret('CLIENT-ID')
TENANT_ID = get_secret('TENANT-ID')

ERP_CLIENT_ID = get_secret('ERP-CLIENT-ID')
ERP_CLIENT_SECRET = get_secret('ERP-CLIENT-SECRET')
ERP_TENANT_ID = get_secret('ERP-TENANT-ID')
ERP_RESOURCE = get_secret('ERP-RESOURCE')
ERP_SANDBOX_RESOURCE = get_secret('ERP-SANDBOX-RESOURCE')

conn_str = get_secret('AZURE-POSTGRESQL-CONNECTIONSTRING')
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
