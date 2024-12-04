""" utils/key_vault.py """

from azure.core.exceptions import ResourceNotFoundError
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

class AzureKeyVault:
    """Class for AzureKeyVault"""
    def __init__(self, vault_url):
        self.vault_url = vault_url
        self.credential = DefaultAzureCredential()
        self.client = SecretClient(vault_url=self.vault_url, credential=self.credential)

    def get_secret(self, secret_name):
        """
        Retrieve the value of a secret from Azure Key Vault.

        Args:
            secret_name (str): The name of the secret to retrieve.

        Returns:
            str: The value of the retrieved secret.
        """
        try:
            secret = self.client.get_secret(secret_name)
            return secret.value
        except ResourceNotFoundError as exc:
            raise ValueError(f"Secret '{secret_name}' not found in Azure Key Vault.") from exc
        except Exception as e:
            raise RuntimeError(f"Error retrieving secret '{secret_name}': {e}") from e
