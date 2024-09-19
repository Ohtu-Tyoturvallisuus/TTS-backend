from django.urls import path
from . import views
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
  path('worksites/', views.WorksiteList.as_view()),
  path('worksites/<int:pk>/', views.WorksiteDetail.as_view()),
  path('users/', views.UserList.as_view()),
  path('users/<int:pk>/', views.UserDetail.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)