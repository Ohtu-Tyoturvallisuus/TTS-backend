""" api/urls.py """

from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from api.views import (
    api_root,
    ProjectList,
    ProjectDetail,
    SurveyList,
    SurveyDetail,
    FilledSurveys,
    RiskNoteCreate,
    RiskNoteDetail,
    UserList,
    UserDetail,
    SignIn,
    TranscribeAudio,
    UploadImages,
    RetrieveImage,
    RetrieveParams,
    TranslateText,
    SurveyByAccessCode,
    JoinSurvey,
    AccountsBySurvey,
)

# .../api/...
urlpatterns = [
    path(
        '',
        api_root,
        name='api-root'
    ),
    path(
        'projects/',
        ProjectList.as_view(),
        name='project-list'
    ),
    path(
        'projects/<int:pk>/',
        ProjectDetail.as_view(),
        name='project-detail'
    ),
    path(
        'projects/<int:project_pk>/surveys/',
        SurveyList.as_view(),
        name='survey-list'
    ),
    path(
        'projects/<int:project_pk>/surveys/<int:pk>/',
        SurveyDetail.as_view(),
        name='survey-detail'
    ),
    path(
        'projects/<int:project_pk>/surveys/<int:survey_pk>/risk_notes/',
        RiskNoteCreate.as_view(),
        name='risknote-create'
    ),
    path(
        'projects/<int:project_pk>/surveys/<int:survey_pk>/risk_notes/<int:pk>/',
        RiskNoteDetail.as_view(),
        name='risknote-detail'
    ),
    path(
        'surveys/',
        SurveyList.as_view(),
        name='survey-list'
    ),
    path(
        'surveys/<int:pk>/',
        SurveyDetail.as_view(),
        name='survey-detail'
    ),
    path(
        'surveys/<int:survey_pk>/risk_notes/',
        RiskNoteCreate.as_view(),
        name='risknote-create'
    ),
    path(
        'users/',
        UserList.as_view(),
        name='user-list'
    ),
    path(
        'users/<int:pk>/',
        UserDetail.as_view(),
        name='user-detail'
    ),
    path(
        'signin/',
        SignIn.as_view(),
        name='signin'
    ),
    path(
        'transcribe/',
        TranscribeAudio.as_view(),
        name='transcribe_audio'
    ),
    path(
        'upload-images/',
        UploadImages.as_view(),
        name='upload_image'
    ),
    path(
        'retrieve-image/',
        RetrieveImage.as_view(),
        name='retrieve_image'
    ),
    path(
        'retrieve-params/',
        RetrieveParams.as_view(),
        name='retrieve_params'
    ),
    path(
        'translate/',
        TranslateText.as_view(),
        name='translate-text'
    ),
    path(
        'filled-surveys/',
        FilledSurveys.as_view(),
        name='filled-surveys'
    ),
    path(
        'surveys/code/<str:access_code>/',
        SurveyByAccessCode.as_view(),
        name='survey-by-code'
    ),
    path(
        'surveys/join/<str:access_code>/',
        JoinSurvey.as_view(),
        name='join-survey'
    ),
    path(
        'survey-accounts/<int:survey_pk>',
        AccountsBySurvey.as_view(),
        name='survey-accounts'
    )
]

urlpatterns = format_suffix_patterns(urlpatterns)
