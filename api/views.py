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

from .models import Worksite, RiskNote, Survey
from .serializers import (
    WorksiteSerializer,
    SurveySerializer,
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
        "worksites_url": reverse("worksite-list", request=request, format=format),
        "surveys_url": reverse("survey-list", request=request, format=format),
    }
    return render(request, 'api/index.html', context)

# <GET, POST, HEAD, OPTIONS> /api/worksites/
class WorksiteList(generics.ListCreateAPIView):
    """Class for WorksiteList"""
    queryset = Worksite.objects.all()
    serializer_class = WorksiteSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

# <GET, PUT, PATCH, DELETE, HEAD, OPTIONS> /api/worksites/<id>/
class WorksiteDetail(generics.RetrieveUpdateDestroyAPIView):
    """Class for WorksiteDetail"""
    queryset = Worksite.objects.all()
    serializer_class = WorksiteSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    lookup_field = 'pk'

# <GET, POST, HEAD, OPTIONS> /api/worksites/<id>/surveys/ or /api/surveys/
class SurveyList(generics.ListCreateAPIView):
    """Class for SurveyList"""
    serializer_class = SurveySerializer

    def get_queryset(self):
        worksite_id = self.kwargs.get('worksite_pk')
        if worksite_id:
            return Survey.objects.filter(worksite_id=worksite_id)
        return Survey.objects.all()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        worksite_id = self.kwargs.get('worksite_pk')
        if worksite_id:
            context['worksite'] = Worksite.objects.get(pk=worksite_id)
        return context

    def perform_create(self, serializer):
        worksite_id = self.kwargs.get('worksite_pk')
        if worksite_id:
            worksite = Worksite.objects.get(pk=worksite_id)
            serializer.save(worksite=worksite)
        else:
            serializer.save()

# <GET, PUT, PATCH, DELETE, HEAD, OPTIONS>
# /api/worksites/<worksite_id>/surveys/<survey_id> or /api/surveys/<id>/
class SurveyDetail(generics.RetrieveUpdateDestroyAPIView):
    """Class for SurveyDetail"""
    queryset = Survey.objects.all()
    serializer_class = SurveySerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    lookup_field = 'pk'

# <GET, POST, HEAD, OPTIONS> /api/surveys/<id>/risk_notes/
# + Supports list of risk_notes as payload
class RiskNoteCreateView(generics.ListCreateAPIView):
    """Class for RiskNoteCreateView"""
    serializer_class = RiskNoteSerializer

    def get_queryset(self):
        survey_id = self.kwargs['survey_id']
        return RiskNote.objects.filter(survey_id=survey_id)

    def get_serializer_context(self):
        # Pass the survey to the serializer context
        context = super().get_serializer_context()
        survey_id = self.kwargs['survey_id']
        context['survey'] = Survey.objects.get(id=survey_id)
        return context

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, many=isinstance(request.data, list))
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

# <GET, HEAD, OPTIONS> /api/risk_notes/
class RiskNoteListView(generics.ListAPIView):
    """Class for RiskNoteListView"""
    queryset = RiskNote.objects.all()
    serializer_class = RiskNoteSerializer

# <PUT/PATCH> /api/risk_notes/<id>/
class RiskNoteUpdateView(generics.UpdateAPIView):
    """Class for RiskNoteUpdateView"""
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
