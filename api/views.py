from rest_framework import generics
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response
from rest_framework import status
from .models import Worksite, RiskNote
from rest_framework import permissions
from .serializers import *
from django.contrib.auth.models import User
from rest_framework.decorators import api_view 
from rest_framework.response import Response
from rest_framework.reverse import reverse 
from django.shortcuts import render


def api_root(request):
    return render(request, 'api/index.html')

# Url-links to the API endpoints
# @api_view(["GET"]) 
# def api_root(request, format=None):
#     return Response(
#         {
#             "worksites": reverse("worksite-list", request=request, format=format),
#             "surveys": reverse("survey-list", request=request, format=format),
#             "risk_notes": reverse("risknote-list", request=request, format=format),
#             "users": reverse("user-list", request=request, format=format),
#         }
#     )

# <GET, POST, HEAD, OPTIONS> /api/worksites/
class WorksiteList(generics.ListCreateAPIView):
    queryset = Worksite.objects.all()
    serializer_class = WorksiteSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

# <GET, PUT, PATCH, DELETE, HEAD, OPTIONS> /api/worksites/<id>/
class WorksiteDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Worksite.objects.all()
    serializer_class = WorksiteSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    lookup_field = 'pk'

# <GET, POST, HEAD, OPTIONS> /api/worksites/<id>/surveys/ or /api/surveys/
class SurveyList(generics.ListCreateAPIView):
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
    queryset = Survey.objects.all()
    serializer_class = SurveySerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    lookup_field = 'pk'

# <GET, POST, HEAD, OPTIONS> /api/surveys/<id>/risk_notes/
# + Supports list of risk_notes as payload
class RiskNoteCreateView(generics.ListCreateAPIView):
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

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, many=isinstance(request.data, list))
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

# <GET, HEAD, OPTIONS> /api/risk_notes/
class RiskNoteListView(generics.ListAPIView):
    queryset = RiskNote.objects.all()
    serializer_class = RiskNoteSerializer

# <PUT/PATCH> /api/risk_notes/<id>/
class RiskNoteUpdateView(generics.UpdateAPIView):
    queryset = RiskNote.objects.all()
    serializer_class = RiskNoteSerializer

# <GET, POST, HEAD, OPTIONS> /api/users/
class UserList(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

# <GET, PUT, PATCH, DELETE, HEAD, OPTIONS> /api/users/<id>/
class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'pk'

# <POST> /api/signin/
class SignIn(generics.CreateAPIView):
    serializer_class = SignInSerializer

    def create(self, request, *args, **kwargs):
        username = request.data.get('username')
        if not username:
            return Response({"error": "Username is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        user, created = User.objects.get_or_create(username=username)
        
        if created:
            message = f"User '{username}' created and signed in successfully"
            status_code = status.HTTP_201_CREATED
        else:
            message = f"User '{username}' signed in successfully"
            status_code = status.HTTP_200_OK
                
        return Response({"message": message}, status=status_code)