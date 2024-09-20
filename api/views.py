from django.shortcuts import render
from rest_framework import generics
from rest_framework.decorators import api_view
from .models import Worksite, RiskNote
from .serializers import *
from django.contrib.auth.models import User

# GET, POST, HEAD, OPTIONS
class WorksiteList(generics.ListCreateAPIView):
    queryset = Worksite.objects.all()
    serializer_class = WorksiteSerializer

# GET, PUT, PATCH, DELETE, HEAD, OPTIONS
class WorksiteDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Worksite.objects.all()
    serializer_class = WorksiteSerializer
    lookup_field = 'pk'

class WorksiteSurveyList(generics.ListAPIView):
    serializer_class = SurveySerializer

    def get_queryset(self):
        worksite_id = self.kwargs['worksite_pk']
        return Survey.objects.filter(worksite_id=worksite_id)

class RiskNoteList(generics.ListCreateAPIView):
    serializer_class = RiskNoteSerializer

    def get_queryset(self):
        survey_id = self.kwargs['survey_pk']
        return RiskNote.objects.filter(survey_id=survey_id)

    def perform_create(self, serializer):
        serializer.save()

class RiskNoteDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = RiskNote.objects.all()
    serializer_class = RiskNoteSerializer
    lookup_field = 'pk'

class SurveyList(generics.ListCreateAPIView):
    queryset = Survey.objects.all()
    serializer_class = SurveySerializer

class SurveyDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Survey.objects.all()
    serializer_class = SurveySerializer
    lookup_field = 'pk'

class UserList(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'pk'

class UserSurveyList(generics.ListAPIView):
    serializer_class = SurveySerializer

    def get_queryset(self):
        user_id = self.kwargs['user_pk']
        return Survey.objects.filter(overseer_id=user_id)