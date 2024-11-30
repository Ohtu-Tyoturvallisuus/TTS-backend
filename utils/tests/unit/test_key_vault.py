""" utils/tests/unit/test_key_vault.py """

from unittest.mock import MagicMock
import pytest
from azure.core.exceptions import ResourceNotFoundError
from utils.key_vault import AzureKeyVault

def test_get_secret_success():
    """Test the successful retrieval of a secret."""
    # Mock the SecretClient
    mock_secret_client = MagicMock()
    mock_secret_client.get_secret.return_value.value = "mock_secret_value"

    # Patch AzureKeyVault with the mock client
    azure_key_vault = AzureKeyVault(vault_url="https://mock-vault.vault.azure.net")
    azure_key_vault.client = mock_secret_client

    # Retrieve the secret
    secret_value = azure_key_vault.get_secret("SECRET-KEY")

    # Assert the returned value
    assert secret_value == "mock_secret_value"
    mock_secret_client.get_secret.assert_called_with("SECRET-KEY")

def test_get_secret_not_found():
    """Test handling of ResourceNotFoundError."""
    # Mock the SecretClient to raise ResourceNotFoundError
    mock_secret_client = MagicMock()
    mock_secret_client.get_secret.side_effect = ResourceNotFoundError("Secret not found")

    # Patch AzureKeyVault with the mock client
    azure_key_vault = AzureKeyVault(vault_url="https://mock-vault.vault.azure.net")
    azure_key_vault.client = mock_secret_client

    # Attempt to retrieve a nonexistent secret and assert exception
    with pytest.raises(ValueError) as exc_info:
        azure_key_vault.get_secret("NON_EXISTENT_SECRET")

    # Assert the exception message
    assert str(exc_info.value) == "Secret 'NON_EXISTENT_SECRET' not found in Azure Key Vault."
    mock_secret_client.get_secret.assert_called_with("NON_EXISTENT_SECRET")

def test_get_secret_generic_exception():
    """Test handling of a generic exception."""
    # Mock the SecretClient to raise a generic Exception
    mock_secret_client = MagicMock()
    mock_secret_client.get_secret.side_effect = Exception("Unexpected error")

    # Patch AzureKeyVault with the mock client
    azure_key_vault = AzureKeyVault(vault_url="https://mock-vault.vault.azure.net")
    azure_key_vault.client = mock_secret_client

    # Attempt to retrieve a secret and assert exception
    with pytest.raises(RuntimeError) as exc_info:
        azure_key_vault.get_secret("SECRET-KEY")

    # Assert the exception message
    assert "Error retrieving secret 'SECRET-KEY': Unexpected error" in str(exc_info.value)
    mock_secret_client.get_secret.assert_called_with("SECRET-KEY")
