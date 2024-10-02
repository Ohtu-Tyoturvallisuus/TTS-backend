import json
from django.core.management.base import BaseCommand
from api.models import Project  # Ensure the correct import path for your Project model

class Command(BaseCommand):
    help = 'Import projects from a local JSON file'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='The path to the JSON file')

    def handle(self, *args, **kwargs):
        file_path = kwargs['file_path']
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                self.import_projects(data)
                self.stdout.write(self.style.SUCCESS('Projects imported successfully'))
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'File not found: {file_path}'))
        except json.JSONDecodeError:
            self.stdout.write(self.style.ERROR(f'Error decoding JSON from {file_path}'))

    def import_projects(self, data):
        imported_count = 0
        projects = data.get("Projekti", [])
        for item in projects:
            if not isinstance(item, dict):
                self.stdout.write(self.style.ERROR(f'Invalid item format: {item}'))
                continue

            project_id = item.get("ProjectId")
            if project_id is None:
                self.stdout.write(self.style.ERROR(f'Missing ProjectId in item: {item}'))
                continue

            # Only import projects with two hyphens
            if project_id.count('-') == 2:
                # Update or create projects
                project, created = Project.objects.update_or_create(
                    project_id=project_id,
                    defaults={
                        'project_name': item.get('ProjectName', ''),
                        'dimension_display_value': item.get('DimensionDisplayValue', ''),
                        'project_group': item.get('ProjectGroup', '')
                    }
                )
                imported_count += 1
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Created project {project.project_name}'))
                else:
                    self.stdout.write(self.style.SUCCESS(f'Updated project {project.project_name}'))
            else:
                self.stdout.write(self.style.WARNING(f'Skipped project with ID {project_id} (does not contain exactly two hyphens)'))
        self.stdout.write(self.style.SUCCESS(f'Imported {imported_count} projects'))