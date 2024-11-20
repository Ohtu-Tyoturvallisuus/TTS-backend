""" api/management/commands/import_projects.py """

import requests
from django.core.management.base import BaseCommand
from django.conf import settings
from api.models import Project

def get_erp_access_token(resource):
    """
    Helper method to get an access token from Azure AD.
    """
    token_url = f"https://login.microsoftonline.com/{settings.ERP_TENANT_ID}/oauth2/token"
    payload = {
        'client_id': settings.ERP_CLIENT_ID,
        'client_secret': settings.ERP_CLIENT_SECRET,
        'grant_type': 'client_credentials',
        'resource': resource,
    }
    try:
        token_response = requests.post(token_url, data=payload, timeout=30)
        token_response.raise_for_status()
        return token_response.json().get('access_token')
    except requests.RequestException as e:
        raise requests.RequestException(f"Authentication failed: {str(e)}") from e

def fetch_projects_from_erp(erp_access_token, resource):
    """
    Helper method to fetch project data from ERP-interface.
    """
    projects_url = (
        f"{resource}/data/Projects?cross-company=true"
        f"&$filter=ProjectStage eq Microsoft.Dynamics.DataEntities.ProjStatus'InProcess'"
        f"&$select=ProjectID,dataAreaId,ProjectName,"
        f"DimensionDisplayValue,WorkerResponsiblePersonnelNumber,"
        f"CustomerAccount"
        # f"&$top=10"
    )

    headers = {
        'Authorization': f'Bearer {erp_access_token}',
        'Content-Type': 'application/json',
    }

    try:
        projects_response = requests.get(projects_url, headers=headers, timeout=30)
        projects_response.raise_for_status()
        return projects_response.json()
    except requests.RequestException as e:
        raise requests.RequestException(f"Failed to fetch projects: {str(e)}") from e

class Command(BaseCommand):
    """Custom Django management command to import projects from Telinekataja ERP interface"""
    help = 'Import projects from Telinekataja ERP interface. Flags: --sandbox'

    def add_arguments(self, parser):
        parser.add_argument(
            '--sandbox',
            action='store_true',
            help='Use the sandbox environment'
        )

    def handle(self, *args, **kwargs):
        # Determine environment (production or sandbox)
        environment = 'sandbox' if kwargs['sandbox'] else 'production'
        resource = (
            settings.ERP_SANDBOX_RESOURCE
            if environment == 'sandbox'
            else settings.ERP_RESOURCE
        )
        self.stdout.write(f'Using {environment} ERP')

        # Step 1: Get access token
        try:
            access_token = get_erp_access_token(resource)
        except requests.RequestException as e:
            self.stdout.write(self.style.ERROR(f'Error getting access token: {str(e)}'))
            return

        # Step 2: Fetch projects using the access token
        try:
            self.stdout.write('Fetching projects...')
            projects_data = fetch_projects_from_erp(access_token, resource)
            projects = projects_data.get('value', [])
            self.import_projects(projects)
            self.stdout.write(self.style.SUCCESS('Projects updated successfully'))
        except requests.RequestException as e:
            self.stdout.write(self.style.ERROR(f'Error fetching projects: {str(e)}'))

    def import_projects(self, projects):
        """
        Import projects from JSON data
        """
        self.stdout.write(f'Going through {len(projects)} projects...')
        self.stdout.write('Importing projects with id format x*-xx-xx')
        created_count = 0
        for item in projects:
            if not isinstance(item, dict):
                self.stdout.write(self.style.ERROR(f'Invalid item format: {item}'))
                continue

            project_id = item.get("ProjectID")
            if project_id is None:
                self.stdout.write(self.style.ERROR(f'Missing ProjectID in item: {item}'))
                continue

            # Only import projects with two hyphens
            if project_id.count('-') == 2:
                # If a project with the given project_id exists:
                # -> update fields with the values in defaults.
                # If no project with the given project_id exists:
                # -> create new project with values in defaults.
                project, created = Project.objects.update_or_create(
                    project_id=project_id,
                    defaults={
                        'data_area_id': item.get('dataAreaId', ''),
                        'project_name': item.get('ProjectName', ''),
                        'dimension_display_value': item.get('DimensionDisplayValue', ''),
                        'worker_responsible_personnel_number': item.get(
                            'WorkerResponsiblePersonnelNumber', ''),
                        'customer_account': item.get(
                            'CustomerAccount', '')
                    }
                )
                if created:
                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Created project {project.project_name} with ID {project.project_id}'
                        )
                    )

        # Retrieve all existing projects from the database
        existing_projects = Project.objects.all()

        # Create a set of ProjectIds from the given projects list
        given_project_ids = {item.get("ProjectID") for item in projects if item.get("ProjectID")}

        # Iterate through the existing projects and delete those not in the given projects list
        deleted_count = 0
        for project in existing_projects:
            if project.project_id not in given_project_ids:
                # project.delete()
                deleted_count += 1

        self.stdout.write(self.style.SUCCESS(f'Created {created_count} new projects'))
        self.stdout.write(self.style.WARNING(f'Found {deleted_count} obsolete projects'))
        self.stdout.write(f'Total projects in database: {Project.objects.count()}')
