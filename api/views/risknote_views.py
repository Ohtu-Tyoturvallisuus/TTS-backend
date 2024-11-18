""" api/views/risknote_views.py """

from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response

from api.models import RiskNote, Survey
from api.serializers import RiskNoteSerializer

# <GET, POST, HEAD, OPTIONS> /api/surveys/<id>/risk_notes/
# or /api/projects/<project_id>/surveys/<survey_id>/risk_notes/
# + Supports list of risk_notes as payload
class RiskNoteCreate(generics.ListCreateAPIView):
    """
    Handles the creation and listing of RiskNote objects. 
    Supports a list of RiskNote:s as payload.
    """
    serializer_class = RiskNoteSerializer

    def get_queryset(self):
        survey_id = self.kwargs.get('survey_pk') # no need to check if survey_id is None
        return RiskNote.objects.filter(survey_id=survey_id)

    def get_serializer_context(self):
        # Pass the survey to the serializer context
        context = super().get_serializer_context()
        survey_id = self.kwargs.get('survey_pk')
        if survey_id:
            context['survey'] = get_object_or_404(Survey, id=survey_id)
        return context

    def perform_create(self, serializer):
        survey_id = self.kwargs.get('survey_pk') # no need to check if survey_id is None
        survey = get_object_or_404(Survey, pk=survey_id)
        serializer.save(survey=survey)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, many=isinstance(request.data, list))
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

# <GET, PUT, PATCH, DELETE, HEAD, OPTIONS>
# /api/projects/<project_id>/surveys/<survey_id>/risk_notes/<id>/
class RiskNoteDetail(generics.RetrieveUpdateDestroyAPIView):
    """Class for RiskNoteDetail"""
    queryset = RiskNote.objects.all()
    serializer_class = RiskNoteSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    lookup_field = 'pk'
