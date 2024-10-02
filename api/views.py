""" api/views.py """
# pylint: disable=redefined-builtin

from rest_framework import generics
from rest_framework import status
from rest_framework import permissions
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from django.shortcuts import render
from django.contrib.auth import get_user_model

from .models import Project, RiskNote, Survey
from rest_framework.permissions import IsAdminUser
from .serializers import (
    ProjectSerializer,
    ProjectListSerializer,
    SurveySerializer,
    SurveyNestedSerializer,
    RiskNoteSerializer,
    UserSerializer,
    SignInSerializer
)

User = get_user_model()

# Url-links to the API endpoints
@api_view(["GET"])
def api_root(request, format=None):
    """ API root view """
    context = {
        "projects_url": reverse("project-list", request=request, format=format),
        "surveys_url": reverse("survey-list", request=request, format=format),
    }
    return render(request, 'api/index.html', context)

# <GET, POST, HEAD, OPTIONS> /api/projects/
class ProjectList(generics.ListCreateAPIView):
    """Class for ProjectList"""
    queryset = Project.objects.all()
    serializer_class = ProjectListSerializer

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

# <GET, POST, HEAD, OPTIONS> /api/projects/<id>/surveys/ or /api/surveys/
class SurveyList(generics.ListCreateAPIView):
    """Class for SurveyList"""
    serializer_class = SurveySerializer

    def get_queryset(self):
        project_id = self.kwargs.get('project_pk')
        if project_id:
            return Survey.objects.filter(project_id=project_id)
        return Survey.objects.all()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        project_id = self.kwargs.get('project_pk')
        if project_id:
            context['project'] = Project.objects.get(pk=project_id)
        return context

    def perform_create(self, serializer):
        project_id = self.kwargs.get('project_pk')
        if project_id:
            project = Project.objects.get(pk=project_id)
            serializer.save(project=project)
        else:
            serializer.save()

# <GET, PUT, PATCH, DELETE, HEAD, OPTIONS>
# /api/projects/<project_id>/surveys/<survey_id> or /api/surveys/<id>/
class SurveyDetail(generics.RetrieveUpdateDestroyAPIView):
    """Class for SurveyDetail"""
    queryset = Survey.objects.all()
    serializer_class = SurveySerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    lookup_field = 'pk'

# <GET, POST, HEAD, OPTIONS> /api/surveys/<id>/risk_notes/
# + Supports list of risk_notes as payload
class RiskNoteCreate(generics.ListCreateAPIView):
    """
    Handles the creation and listing of RiskNote objects. 
    Supports a list of RiskNote:s as payload.
    """
    serializer_class = RiskNoteSerializer

    def get_queryset(self):
        survey_id = self.kwargs.get('survey_pk')
        if survey_id:
            return RiskNote.objects.filter(survey_id=survey_id)
        return RiskNote.objects.all()

    def get_serializer_context(self):
        # Pass the survey to the serializer context
        context = super().get_serializer_context()
        survey_id = self.kwargs.get('survey_pk')
        if survey_id:
            context['survey'] = Survey.objects.get(id=survey_id)
        return context
    
    def perform_create(self, serializer):
        survey_id = self.kwargs.get('survey_pk')
        if survey_id:
            survey = Survey.objects.get(pk=survey_id)
            serializer.save(survey=survey)
        else:
            serializer.save()

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, many=isinstance(request.data, list))
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class RiskNoteDetail(generics.RetrieveUpdateDestroyAPIView):
    """Class for RiskNoteDetail"""
    queryset = RiskNote.objects.all()
    serializer_class = RiskNoteSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    lookup_field = 'pk'

# <GET, HEAD, OPTIONS> /api/risk_notes/
class RiskNoteList(generics.ListAPIView):
    """Class for RiskNoteList"""
    queryset = RiskNote.objects.all()
    serializer_class = RiskNoteSerializer

# <PUT/PATCH> /api/risk_notes/<id>/
class RiskNoteUpdate(generics.UpdateAPIView):
    """Class for RiskNoteUpdate"""
    queryset = RiskNote.objects.all()
    serializer_class = RiskNoteSerializer

# <GET, POST, HEAD, OPTIONS> /api/users/
class UserList(generics.ListCreateAPIView):
    """Class for UserList"""
    queryset = User.objects.all()
    serializer_class = UserSerializer

# <GET, PUT, PATCH, DELETE, HEAD, OPTIONS> /api/users/<id>/
class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    """Class for UserDetail"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'pk'

# <POST> /api/signin/
class SignIn(generics.CreateAPIView):
    """Class for SignIn"""
    serializer_class = SignInSerializer

    def create(self, request, *args, **kwargs):
        username = request.data.get('username')
        if not username:
            return Response({"error": "Username is required"}, status=status.HTTP_400_BAD_REQUEST)

        _, created = User.objects.get_or_create(username=username)

        if created:
            message = f"User '{username}' created and signed in successfully"
            status_code = status.HTTP_201_CREATED
        else:
            message = f"User '{username}' signed in successfully"
            status_code = status.HTTP_200_OK

        return Response({"message": message}, status=status_code)
