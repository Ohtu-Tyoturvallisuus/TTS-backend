""" api/urls.py """

from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

# .../api/...
urlpatterns = [
    path(
        '',
        views.api_root,
        name='api-root'
    ),
    path(
        'projects/',
        views.ProjectList.as_view(),
        name='project-list'
    ),
    path(
        'projects/<int:pk>/',
        views.ProjectDetail.as_view(),
        name='project-detail'
    ),
    path(
        'projects/<int:project_pk>/surveys/',
        views.SurveyList.as_view(),
        name='survey-list'
    ),
    path(
        'projects/<int:project_pk>/surveys/<int:pk>/',
        views.SurveyDetail.as_view(),
        name='survey-detail'
    ),
    path(
        'projects/<int:project_pk>/surveys/<int:survey_pk>/risk_notes/',
        views.RiskNoteCreate.as_view(),
        name='risknote-create'
    ),
    path(
        'projects/<int:project_pk>/surveys/<int:survey_pk>/risk_notes/<int:pk>/',
        views.RiskNoteDetail.as_view(),
        name='risknote-detail'
    ),
    path(
        'surveys/',
        views.SurveyList.as_view(),
        name='survey-list'
    ),
    path(
        'surveys/<int:pk>/',
        views.SurveyDetail.as_view(),
        name='survey-detail'
    ),
    path(
        'surveys/<int:survey_pk>/risk_notes/',
        views.RiskNoteCreate.as_view(),
        name='risknote-create'
    ),
    path(
        'users/',
        views.UserList.as_view(),
        name='user-list'
    ),
    path(
        'users/<int:pk>/',
        views.UserDetail.as_view(),
        name='user-detail'
    ),
    path(
        'signin/',
        views.SignIn.as_view(),
        name='signin'
    ),
    path(
        'transcribe/',
        views.TranscribeAudio.as_view(),
        name='transcribe_audio'
    ),
    path(
        'upload-images/',
        views.UploadImages.as_view(),
        name='upload_image'
    ),
    path(
        'retrieve-image/',
        views.RetrieveImage.as_view(),
        name='retrieve_image'
    ),
    path(
        'retrieve-params/',
        views.RetrieveParams.as_view(),
        name='retrieve_params'
    ),
    path(
        'translate/',
        views.TranslateText.as_view(),
        name='translate-text'
    )
]

urlpatterns = format_suffix_patterns(urlpatterns)
