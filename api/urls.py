from django.urls import path
from . import views
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
  path('worksites/', views.WorksiteList.as_view()),
  path('worksites/<int:pk>/', views.WorksiteDetail.as_view()),
  path('worksites/<int:worksite_pk>/surveys/', views.WorksiteSurveyList.as_view()),
  path('worksites/<int:worksite_pk>/surveys/<int:pk>/', views.SurveyDetail.as_view()),
  path('worksites/<int:worksite_pk>/surveys/<int:survey_pk>/risknotes/', views.RiskNoteList.as_view()),
  path('worksites/<int:worksite_pk>/surveys/<int:survey_pk>/risknotes/<int:pk>/', views.RiskNoteDetail.as_view()),
  path('users/', views.UserList.as_view()),
  path('users/<int:pk>/', views.UserDetail.as_view()),
  path('surveys/', views.SurveyList.as_view()),
  path('users/<int:user_pk>/surveys/', views.UserSurveyList.as_view()),  # Route for user surveys

]

urlpatterns = format_suffix_patterns(urlpatterns)