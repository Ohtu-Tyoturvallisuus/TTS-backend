""" api/urls.py """

from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

""" 
survey/
survey/<id> 
survey/<id>/risks
survey/<id>/risks/
survey/<id>/risks/<risk_id>
"""

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
        'risk_notes/',
        views.RiskNoteList.as_view(),
        name='risknote-list'
    ),
    path(
        'risk_notes/<int:pk>/',
        views.RiskNoteUpdate.as_view(),
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
