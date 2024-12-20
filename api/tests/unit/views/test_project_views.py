""" api/tests/unit/views/test.project_views.py """
# pylint: disable=attribute-defined-outside-init

import pytest
from django.urls import reverse
from rest_framework import status

pytestmark = pytest.mark.django_db

class TestProjectListView:
    """Tests ProjectList view"""

    def setup_method(self):
        """Setup method"""
        self.url = reverse('project-list')
        self.project_data = {
            'project_id': 'test_project_id',
            'project_name': 'Test Project',
            'data_area_id': 'Test Data Area',
            'dimension_display_value': 'Test Dimension',
            'worker_responsible_personnel_number': '12345',
            'customer_account': 'Test Account'
        }

    def test_project_list(self, client, create_project):
        """Test ProjectList view"""
        response = client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['project_id'] == create_project.project_id
        assert response.data[0]['project_name'] == create_project.project_name
        assert response.data[0]['data_area_id'] == create_project.data_area_id
        assert response.data[0]['dimension_display_value'] == create_project.dimension_display_value
        assert response.data[0]['worker_responsible_personnel_number'] == \
            create_project.worker_responsible_personnel_number
        assert response.data[0]['customer_account'] == create_project.customer_account

    def test_project_create(self, client, create_user):
        """Test ProjectList view with POST request (non-admin user)"""
        client.force_authenticate(user=create_user)
        response = client.post(self.url, self.project_data)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data['detail'] == 'You do not have permission to perform this action.'

    def test_project_create_admin(self, client, create_superuser):
        """Test ProjectList view with POST request (admin user)"""
        client.force_authenticate(user=create_superuser)
        response = client.post(self.url, self.project_data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['project_id'] == 'test_project_id'
        assert response.data['project_name'] == 'Test Project'
        assert response.data['data_area_id'] == 'Test Data Area'
        assert response.data['dimension_display_value'] == 'Test Dimension'
        assert response.data['worker_responsible_personnel_number'] == '12345'
        assert response.data['customer_account'] == 'Test Account'

class TestProjectDetailView:
    """Tests ProjectDetail view"""

    @pytest.fixture(autouse=True)
    def setup_method(self, create_project):
        """Setup method using create_project fixture"""
        self.project = create_project
        self.url = reverse('project-detail', kwargs={'pk': self.project.id})
        self.project_data = {
            'project_id': 'updated_project_id',
            'project_name': 'Updated Project',
            'data_area_id': 'Updated Data Area',
            'dimension_display_value': 'Updated Dimension',
            'worker_responsible_personnel_number': '54321',
            'customer_account': 'Updated Account'
        }

    def test_project_detail(self, client):
        """Test ProjectDetail view (allow any)"""
        response = client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['project_id'] == self.project.project_id
        assert response.data['project_name'] == self.project.project_name
        assert response.data['data_area_id'] == self.project.data_area_id
        assert response.data['dimension_display_value'] == self.project.dimension_display_value
        assert response.data['worker_responsible_personnel_number'] == \
            self.project.worker_responsible_personnel_number
        assert response.data['customer_account'] == self.project.customer_account

    def test_project_detail_not_found(self, client):
        """Test ProjectDetail view with non-existing id"""
        response = client.get(reverse('project-detail', kwargs={'pk': 9999}))
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_project_update(self, client, create_superuser):
        """Test ProjectDetail view with PUT request (admin user)"""
        client.force_authenticate(user=create_superuser)
        response = client.put(self.url, self.project_data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['project_id'] == 'updated_project_id'
        assert response.data['project_name'] == 'Updated Project'
        assert response.data['data_area_id'] == 'Updated Data Area'
        assert response.data['dimension_display_value'] == 'Updated Dimension'
        assert response.data['worker_responsible_personnel_number'] == '54321'
        assert response.data['customer_account'] == 'Updated Account'

    def test_project_delete(self, client, create_superuser):
        """Test ProjectDetail view with DELETE request (admin user)"""
        client.force_authenticate(user=create_superuser)
        response = client.delete(self.url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert response.data is None
