from django.urls import path
from . import views

urlpatterns = [
  path("worksites/", 
       views.WorksiteListCreate.as_view(), 
       name="worksites-view-create"
       ),
  path("worksites/<int:pk>/", 
       views.WorksiteRetrieveUpdateDestroy.as_view(), 
       name="worksites-view-update-delete"
       ),
]