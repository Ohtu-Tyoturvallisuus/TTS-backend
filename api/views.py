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

class SurveyList(generics.ListCreateAPIView):
    queryset = Survey.objects.all()
    serializer_class = SurveySerializer

class UserList(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'pk'