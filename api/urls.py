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
        'worksites/',
        views.WorksiteList.as_view(),
        name='worksite-list'
    ),
    path(
        'worksites/<int:pk>/',
        views.WorksiteDetail.as_view(),
        name='worksite-detail'
    ),
    path(
        'worksites/<int:worksite_pk>/surveys/',
        views.SurveyList.as_view(),
        name='worksite-survey-list'
    ),
    path(
        'worksites/<int:worksite_pk>/surveys/<int:pk>/',
        views.SurveyDetail.as_view(),
        name='worksite-survey-detail'
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
        'surveys/<int:survey_id>/risk_notes/',
        views.RiskNoteCreateView.as_view(),
        name='risknote-create'
    ),

    path(
        'risk_notes/',
        views.RiskNoteListView.as_view(),
        name='risknote-list'
    ),
    path(
        'risk_notes/<int:pk>/',
        views.RiskNoteUpdateView.as_view(),
        name='risknote-update'
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
]

urlpatterns = format_suffix_patterns(urlpatterns)
