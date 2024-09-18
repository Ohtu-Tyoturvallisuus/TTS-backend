from django.shortcuts import render
from rest_framework import generics
from .models import Worksite, RiskNote
from .serializers import *

class WorksiteListCreate(generics.ListCreateAPIView):
    queryset = Worksite.objects.all()
    serializer_class = WorksiteSerializer

        
class WorksiteRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Worksite.objects.all()
    serializer_class = WorksiteSerializer
    lookup_field = 'pk'
