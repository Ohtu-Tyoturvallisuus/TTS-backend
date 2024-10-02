""" api/serializers.py """

# todo/todo_api/serializers.py
from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Project,  RiskNote, Survey

User = get_user_model()

class UserSerializer(serializers.HyperlinkedModelSerializer):
    """Class for UserSerializer"""
    class Meta:
        """Meta class for UserSerializer"""
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class RiskNoteSerializer(serializers.HyperlinkedModelSerializer):
    """
    RiskNoteSerializer is a HyperlinkedModelSerializer for the RiskNote model.
    Attributes:
        Meta (class): Meta class for RiskNoteSerializer.
            model (RiskNote): The model that is being serialized.
            fields (list): List of fields to be included in the serialization.
    Methods:
        create(validated_data):
            Creates and returns a new RiskNote instance, ensuring the survey is passed from the context.
        update(instance, validated_data):
            Updates and returns an existing RiskNote instance with the validated data.
    """
    survey = serializers.ReadOnlyField(source='survey.title')
    
    class Meta:
        """Meta class for RiskNoteSerializer"""
        model = RiskNote
        fields = ['id', 'survey', 'note', 'description', 'status', 'created_at']

class SurveySerializer(serializers.HyperlinkedModelSerializer):
    """Class for SurveySerializer"""
    project = serializers.ReadOnlyField(source='project.project_name')
    risk_notes = RiskNoteSerializer(many=True, read_only=True)

    class Meta:
        model = Survey
        fields = [
            'id', 'project', 'title', 'description', 
            'created_at', 'risk_notes'
        ]

class SurveyNestedSerializer(serializers.ModelSerializer):
    """
    Serializer for nested Survey objects.
    """
    url = serializers.HyperlinkedIdentityField(view_name='survey-detail', read_only=True)

    class Meta:
        """Meta class for SurveySerializer"""
        model = Survey
        fields = ['id', 'url', 'title', 'created_at']

class ProjectSerializer(serializers.HyperlinkedModelSerializer):
    """Class for ProjectSerializer"""
    surveys = SurveyNestedSerializer(many=True, read_only=True)

    class Meta:
        """Meta class for ProjectSerializer"""
        model = Project
        fields = ['id', 'project_id', 'project_name', 'dimension_display_value', 'project_group', 'surveys']

class SignInSerializer(serializers.HyperlinkedModelSerializer):
    """Class for SignInSerializer"""
    username = serializers.CharField()
