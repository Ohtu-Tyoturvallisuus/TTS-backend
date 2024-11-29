""" api/views/project_views.py """

from rest_framework import filters, generics, permissions
from rest_framework.permissions import IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend

from api.filters import ProjectFilter
from api.models import Project
from api.serializers import ProjectSerializer, ProjectListSerializer

# <GET, POST, HEAD, OPTIONS> /api/projects/
class ProjectList(generics.ListCreateAPIView):
    """Class for ProjectList"""
    queryset = Project.objects.all()
    serializer_class = ProjectListSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = ProjectFilter
    search_fields = ['project_name', 'project_id']

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [IsAdminUser()]

# <GET, PUT, PATCH, DELETE, HEAD, OPTIONS> /api/projects/<id>/
class ProjectDetail(generics.RetrieveUpdateDestroyAPIView):
    """Class for ProjectDetail"""
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = (IsAdminUser,)
    lookup_field = 'pk'

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [IsAdminUser()]
