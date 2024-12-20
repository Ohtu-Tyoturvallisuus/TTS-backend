""" api/views/survey_views.py """

import jwt
from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import (
    generics,
    permissions,
    serializers,
    status
)
from rest_framework.response import Response
from rest_framework.views import APIView

from api.models import Account, AccountSurvey, Project, Survey
from api.serializers import SurveySerializer, AccountSurveySerializer


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
        auth_header = self.request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            raise serializers.ValidationError(
                {"error": "Authorization header is required"}
            )
        token = auth_header.split(' ')[1]
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user_id = payload.get('user_id')
        except jwt.ExpiredSignatureError as exc:
            raise serializers.ValidationError({"error": "Token has expired"}) from exc
        except jwt.InvalidTokenError as exc:
            raise serializers.ValidationError({"error": "Invalid token"}) from exc

        project_id = self.kwargs.get('project_pk')
        if not project_id:
            raise serializers.ValidationError(
                {"project": "A project is required to create a survey."}
            )

        account = get_object_or_404(Account, user_id=user_id)
        project = get_object_or_404(Project, pk=project_id)

        survey = serializer.save(project=project, creator=account)
        AccountSurvey.objects.create(account=account, survey=survey)

# <GET, PUT, PATCH, DELETE, HEAD, OPTIONS>
# /api/projects/<project_id>/surveys/<survey_id> or /api/surveys/<id>/
class SurveyDetail(generics.RetrieveUpdateDestroyAPIView):
    """Class for SurveyDetail"""
    queryset = Survey.objects.all()
    serializer_class = SurveySerializer
    lookup_field = 'pk'

    # survey_views.py
    def patch(self, request, *args, **kwargs):
        """Handle partial updates for survey completion and participant count"""
        survey = self.get_object()

        if 'is_completed' in request.data:
            survey.is_completed = request.data['is_completed']
        if 'number_of_participants' in request.data:
            survey.number_of_participants = request.data['number_of_participants']

        survey.save()
        serializer = self.get_serializer(survey)
        return Response(serializer.data)

# <GET> /api/filled-surveys/
class FilledSurveys(APIView):
    """View to retrieve all surveys filled by the currently signed-in account"""

    def get(self, request):
        """Retrieve all surveys filled by the currently signed-in account"""
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return Response(
                {"error": "Authorization header is required"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        try:
            token = auth_header.split(' ')[1]
            decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user_id = decoded_token['user_id']

            account = Account.objects.get(user_id=user_id)

            account_surveys = AccountSurvey.objects.filter(
                account=account
            ).select_related('survey').order_by('-filled_at')

            filled_surveys_data = []
            for account_survey in account_surveys:
                survey = account_survey.survey
                serializer = SurveySerializer(survey)
                filled_surveys_data.append(serializer.data)

            return Response({"filled_surveys": filled_surveys_data}, status=status.HTTP_200_OK)

        except jwt.ExpiredSignatureError:
            return Response({"error": "Token has expired"}, status=status.HTTP_401_UNAUTHORIZED)
        except jwt.InvalidTokenError:
            return Response({"error": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)
        except Account.DoesNotExist:
            return Response({"error": "Account not found"}, status=status.HTTP_404_NOT_FOUND)

# <GET, HEAD, OPTIONS> /api/surveys/code/<access_code>/
class SurveyByAccessCode(generics.RetrieveAPIView):
    """Class for retrieving Survey by access code"""
    serializer_class = SurveySerializer
    permission_classes = (permissions.AllowAny,)
    lookup_field = 'access_code'
    queryset = Survey.objects.all()

# <POST> /api/surveys/validate/<access_code>/
class ValidateSurvey(APIView):
    """Class for validating a survey using access code"""

    def post(self, request, access_code, *args, **kwargs):
        """Link the user's account to a survey"""
        survey = get_object_or_404(Survey, access_code=access_code)

        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return Response({"error": "Authorization header is required."}, status=400)

        token = auth_header.split(' ')[1]
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user_id = payload.get('user_id')
        except jwt.ExpiredSignatureError:
            return Response({"error": "Token has expired."}, status=401)
        except jwt.InvalidTokenError:
            return Response({"error": "Invalid token."}, status=401)

        account = get_object_or_404(Account, user_id=user_id)

        _, created = AccountSurvey.objects.get_or_create(account=account, survey=survey)

        if not created:
            return Response({"detail": "The user has already validated this survey."}, status=200)

        return Response({"detail": "The user has successfully validated the survey."}, status=201)

# <GET> /api/survey-accounts/<survey_id>/
class AccountsBySurvey(APIView):
    """Class for retrieving accounts that are connected to a survey"""

    def get(self, request, *args, **kwargs):
        """Get all accounts connected to a survey by survey id"""
        survey_id = kwargs['survey_pk']
        survey = get_object_or_404(Survey, id=survey_id)

        survey_accounts = AccountSurvey.objects.filter(
            survey=survey
        ).select_related('account').order_by('filled_at')

        serialized_data = AccountSurveySerializer(survey_accounts, many=True).data

        return Response({'accounts': serialized_data}, status=200)
