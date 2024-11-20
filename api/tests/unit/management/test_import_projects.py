""" Test cases for the import_projects management command """
from unittest.mock import patch, MagicMock
import requests

from django.conf import settings
from django.core.management import call_command
from django.test import TestCase

from api.management.commands.import_projects import get_erp_access_token, fetch_projects_from_erp
from api.models import Project

class GetErpAccessTokenTestCase(TestCase):
    """ Test the get_erp_access_token helper function """

    @patch('api.management.commands.import_projects.requests.post')
    def test_get_erp_access_token_success(self, mock_post):
        """ Test the case where the access token is successfully retrieved """
        # Mock the response to return a successful token
        mock_response = MagicMock()
        mock_response.json.return_value = {'access_token': 'fake_access_token'}
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        resource = 'fake_resource'
        token = get_erp_access_token(resource)
        self.assertEqual(token, 'fake_access_token')
        mock_post.assert_called_once_with(
            f"https://login.microsoftonline.com/{settings.ERP_TENANT_ID}/oauth2/token",
            data={
                'client_id': settings.ERP_CLIENT_ID,
                'client_secret': settings.ERP_CLIENT_SECRET,
                'grant_type': 'client_credentials',
                'resource': resource,
            },
            timeout=30
        )

    @patch('api.management.commands.import_projects.requests.post')
    def test_get_erp_access_token_failure(self, mock_post):
        """ Test the case where getting the access token fails """
        # Mock the response to raise an exception
        mock_post.side_effect = requests.RequestException("Authentication failed")

        resource = 'fake_resource'
        with self.assertRaises(requests.RequestException) as context:
            get_erp_access_token(resource)
        self.assertIn("Authentication failed", str(context.exception))
        mock_post.assert_called_once_with(
            f"https://login.microsoftonline.com/{settings.ERP_TENANT_ID}/oauth2/token",
            data={
                'client_id': settings.ERP_CLIENT_ID,
                'client_secret': settings.ERP_CLIENT_SECRET,
                'grant_type': 'client_credentials',
                'resource': resource,
            },
            timeout=30
        )

class FetchProjectsFromErpTestCase(TestCase):
    """ Test the fetch_projects_from_erp helper function """

    @patch('api.management.commands.import_projects.requests.get')
    def test_fetch_projects_from_erp_success(self, mock_get):
        """ Test the case where projects are successfully fetched """
        # Mock the response to return project data
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'value': [
                {
                    'ProjectID': '123-45-67',
                    'dataAreaId': 'area1',
                    'ProjectName': 'Project 1',
                    'DimensionDisplayValue': 'Dimension 1',
                    'WorkerResponsiblePersonnelNumber': '12345',
                    'CustomerAccount': 'Cust1'
                }
            ]
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        resource = 'fake_resource'
        access_token = 'fake_access_token'
        projects = fetch_projects_from_erp(access_token, resource)
        self.assertEqual(len(projects['value']), 1)
        self.assertEqual(projects['value'][0]['ProjectID'], '123-45-67')
        mock_get.assert_called_once_with(
            f"{resource}/data/Projects?cross-company=true"
            f"&$filter=ProjectStage eq Microsoft.Dynamics.DataEntities.ProjStatus'InProcess'"
            f"&$select=ProjectID,dataAreaId,ProjectName,"
            f"DimensionDisplayValue,WorkerResponsiblePersonnelNumber,"
            f"CustomerAccount",
            headers={
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json',
            },
            timeout=30
        )

    @patch('api.management.commands.import_projects.requests.get')
    def test_fetch_projects_from_erp_failure(self, mock_get):
        """ Test the case where fetching projects fails """
        # Mock the response to raise an exception
        mock_get.side_effect = requests.RequestException("Failed to fetch projects")

        resource = 'fake_resource'
        access_token = 'fake_access_token'
        with self.assertRaises(requests.RequestException) as context:
            fetch_projects_from_erp(access_token, resource)
        self.assertIn("Failed to fetch projects", str(context.exception))
        mock_get.assert_called_once_with(
            f"{resource}/data/Projects?cross-company=true"
            f"&$filter=ProjectStage eq Microsoft.Dynamics.DataEntities.ProjStatus'InProcess'"
            f"&$select=ProjectID,dataAreaId,ProjectName,"
            f"DimensionDisplayValue,WorkerResponsiblePersonnelNumber,"
            f"CustomerAccount",
            headers={
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json',
            },
            timeout=30
        )

class ImportProjectsTestCase(TestCase):
    """ Test the import_projects management command """

    @patch('api.management.commands.import_projects.get_erp_access_token')
    @patch('api.management.commands.import_projects.fetch_projects_from_erp')
    def test_import_projects(self, mock_fetch_projects, mock_get_token):
        """ Test the case where projects are successfully imported """
        # Mock the access token
        mock_get_token.return_value = 'fake_access_token'

        # Mock the projects data
        mock_projects_data = {
            'value': [
                {
                    'ProjectID': '123-45-67',
                    'dataAreaId': 'area1',
                    'ProjectName': 'Project 1',
                    'DimensionDisplayValue': 'Dimension 1',
                    'WorkerResponsiblePersonnelNumber': '12345',
                    'CustomerAccount': 'Cust1'
                },
                {
                    'ProjectID': '234-56-78',
                    'dataAreaId': 'area2',
                    'ProjectName': 'Project 2',
                    'DimensionDisplayValue': 'Dimension 2',
                    'WorkerResponsiblePersonnelNumber': '67890',
                    'CustomerAccount': 'Cust2'
                }
            ]
        }
        mock_fetch_projects.return_value = mock_projects_data

        # Call the management command
        call_command('import_projects')

        # Check that the projects were imported
        self.assertEqual(Project.objects.count(), 2)
        project1 = Project.objects.get(project_id='123-45-67')
        self.assertEqual(project1.project_name, 'Project 1')
        self.assertEqual(project1.data_area_id, 'area1')
        self.assertEqual(project1.dimension_display_value, 'Dimension 1')
        self.assertEqual(project1.worker_responsible_personnel_number, '12345')
        self.assertEqual(project1.customer_account, 'Cust1')

        project2 = Project.objects.get(project_id='234-56-78')
        self.assertEqual(project2.project_name, 'Project 2')
        self.assertEqual(project2.data_area_id, 'area2')
        self.assertEqual(project2.dimension_display_value, 'Dimension 2')
        self.assertEqual(project2.worker_responsible_personnel_number, '67890')
        self.assertEqual(project2.customer_account, 'Cust2')

    @patch('api.management.commands.import_projects.get_erp_access_token')
    @patch('api.management.commands.import_projects.fetch_projects_from_erp')
    def test_import_projects_invalid_item_format(self, mock_fetch_projects, mock_get_token):
        """ Test the case where a project has an invalid item format """
        # Mock the access token
        mock_get_token.return_value = 'fake_access_token'

        # Mock the projects data with an invalid item format
        mock_projects_data = {
            'value': [
                'invalid_item'
            ]
        }
        mock_fetch_projects.return_value = mock_projects_data

        # Call the management command
        call_command('import_projects')

        # Check that no projects were imported
        self.assertEqual(Project.objects.count(), 0)

    @patch('api.management.commands.import_projects.get_erp_access_token')
    @patch('api.management.commands.import_projects.fetch_projects_from_erp')
    def test_import_projects_missing_project_id(self, mock_fetch_projects, mock_get_token):
        """ Test the case where a project is missing the ProjectID """
        # Mock the access token
        mock_get_token.return_value = 'fake_access_token'

        # Mock the projects data with a missing ProjectID
        mock_projects_data = {
            'value': [
                {
                    'dataAreaId': 'area1',
                    'ProjectName': 'Project 1',
                    'DimensionDisplayValue': 'Dimension 1',
                    'WorkerResponsiblePersonnelNumber': '12345',
                    'CustomerAccount': 'Cust1'
                }
            ]
        }
        mock_fetch_projects.return_value = mock_projects_data

        # Call the management command
        call_command('import_projects')

        # Check that no projects were imported
        self.assertEqual(Project.objects.count(), 0)

    @patch('api.management.commands.import_projects.get_erp_access_token')
    @patch('api.management.commands.import_projects.fetch_projects_from_erp')
    def test_handle_access_token_failure(self, mock_fetch_projects, mock_get_token): # pylint: disable=unused-argument
        """ Test the case where the access token cannot be retrieved """
        # Mock the access token to raise an exception
        mock_get_token.side_effect = requests.RequestException("Error getting access token")

        # Call the management command
        call_command('import_projects')

        # Check that no projects were imported
        self.assertEqual(Project.objects.count(), 0)

    @patch('api.management.commands.import_projects.get_erp_access_token')
    @patch('api.management.commands.import_projects.fetch_projects_from_erp')
    def test_handle_fetch_projects_failure(self, mock_fetch_projects, mock_get_token):
        """ Test the case where fetching projects fails """
        # Mock the access token
        mock_get_token.return_value = 'fake_access_token'

        # Mock the fetch projects to raise an exception
        mock_fetch_projects.side_effect = requests.RequestException("Error fetching projects")

        # Call the management command
        call_command('import_projects')

        # Check that no projects were imported
        self.assertEqual(Project.objects.count(), 0)
