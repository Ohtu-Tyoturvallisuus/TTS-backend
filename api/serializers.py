""" api/serializers.py """

# todo/todo_api/serializers.py
from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Worksite, RiskNote, Survey

User = get_user_model()

class UserSerializer(serializers.HyperlinkedModelSerializer):
    """Class for UserSerializer"""
    class Meta:
        """Meta class for UserSerializer"""
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class OverseerSerializer(serializers.HyperlinkedModelSerializer):
    """Class for OverseerSerializer"""
    class Meta:
        """Meta class for OverseerSerializer"""
        model = User
        fields = ['username']

class RiskNoteSerializer(serializers.HyperlinkedModelSerializer):
    """Class for RiskNoteSerializer"""
    class Meta:
        """Meta class for RiskNoteSerializer"""
        model = RiskNote
        fields = ['id', 'note', 'description', 'status', 'created_at']

    def create(self, validated_data):
        # Ensure the survey is passed to the RiskNote from the context
        survey = self.context.get('survey')
        return RiskNote.objects.create(survey=survey, **validated_data)

    def update(self, instance, validated_data):
        # Standard update operation
        instance.note = validated_data.get('note', instance.note)
        instance.description = validated_data.get('description', instance.description)
        instance.status = validated_data.get('status', instance.status)
        instance.save()
        return instance

class SurveySerializer(serializers.HyperlinkedModelSerializer):
    """Class for SurveySerializer"""
    worksite = serializers.ReadOnlyField(source='worksite.name')
    overseer = serializers.ReadOnlyField(source='overseer.username')
    risk_notes = RiskNoteSerializer(many=True, read_only=True)

    class Meta:
        """Meta class for SurveySerializer"""
        model = Survey
        fields = ['id', 'worksite', 'overseer', 'title', 'description',  'created_at', 'risk_notes']

class WorksiteSerializer(serializers.HyperlinkedModelSerializer):
    """Class for WorksiteSerializer"""
    surveys = serializers.HyperlinkedRelatedField(
        many=True, view_name='survey-detail', read_only=True
    )

    class Meta:
        """Meta class for WorksiteSerializer"""
        model = Worksite
        fields = ['id', 'name', 'location', 'surveys']

class SignInSerializer(serializers.HyperlinkedModelSerializer):
    """Class for SignInSerializer"""
    username = serializers.CharField()
