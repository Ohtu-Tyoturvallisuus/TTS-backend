""" api/serializers.py """

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import serializers
from .models import Project, RiskNote, Survey

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
            Creates and returns a new RiskNote instance,
            ensuring the survey is passed from the context.
        update(instance, validated_data):
            Updates and returns an existing RiskNote instance with the validated data.
    """
    survey_id = serializers.ReadOnlyField(source='survey.id')

    class Meta:
        """Meta class for RiskNoteSerializer"""
        model = RiskNote
        fields = [
            'id', 'survey_id', 'note', 'description', 'status', 
            'risk_type', 'images', 'created_at'
        ]

class SurveySerializer(serializers.HyperlinkedModelSerializer):
    """Class for SurveySerializer"""
    project_name = serializers.ReadOnlyField(source='project.project_name')
    risk_notes = RiskNoteSerializer(many=True, read_only=True)
    project_id = serializers.ReadOnlyField(source='project.project_id')

    class Meta:
        model = Survey
        fields = [
            'id', 'project_name', 'project_id', 'description',
            'task', 'scaffold_type', 'created_at', 'risk_notes'
        ]

    def to_internal_value(self, data):
        # Ensure JSONField-specific errors are handled gracefully
        try:
            return super().to_internal_value(data)
        except serializers.ValidationError as exc:
            errors = exc.detail
            if 'task' in errors:
                errors['task'] = ["Task must be a non-empty list."]
            if 'scaffold_type' in errors:
                errors['scaffold_type'] = ["Scaffolding type must be a non-empty list."]
            raise serializers.ValidationError(errors)

    def validate_task(self, value):
        """Method to validate the task field"""
        if not isinstance(value, list) or not value:
            raise serializers.ValidationError("Task must be a non-empty list.")
        return value

    def validate_scaffold_type(self, value):
        """Method to validate the scaffold_type field"""
        if not isinstance(value, list) or not value:
            raise serializers.ValidationError("Scaffolding type must be a non-empty list.")
        return value

class SurveyNestedSerializer(serializers.ModelSerializer):
    """
    Serializer for nested Survey objects. Contains url field for full detail view.
    """
    url = serializers.SerializerMethodField()

    class Meta:
        """Meta class for SurveySerializer"""
        model = Survey
        fields = ['id', 'url', 'task', 'scaffold_type', 'created_at']

    def get_url(self, obj):
        """Method to get the URL of the survey"""
        request = self.context.get('request')
        project_id = obj.project.id
        survey_id = obj.id
        relative_url = reverse(
            'survey-detail',
            kwargs={'project_pk': project_id, 'pk': survey_id}
        )
        return request.build_absolute_uri(relative_url)

class ProjectSerializer(serializers.HyperlinkedModelSerializer):
    """Class for ProjectSerializer"""
    surveys = SurveyNestedSerializer(many=True, read_only=True)

    class Meta:
        """Meta class for ProjectSerializer"""
        model = Project
        fields = ['id', 'project_id', 'project_name', 'data_area_id',
                  'dimension_display_value', 'worker_responsible_personnel_number', 
                  'customer_account', 'surveys']

class ProjectListSerializer(serializers.HyperlinkedModelSerializer):
    """Class for ProjectListSerializer"""
    url = serializers.HyperlinkedIdentityField(view_name='project-detail')
    last_survey_date = serializers.SerializerMethodField()

    class Meta:
        """Meta class for ProjectListSerializer"""
        model = Project
        fields = ['id', 'url', 'project_id', 'project_name', 'data_area_id',
                  'dimension_display_value', 'worker_responsible_personnel_number',
                  'customer_account', 'last_survey_date']

    def get_last_survey_date(self, obj):
        """Method to get the last survey date"""
        last_survey = obj.surveys.order_by('-created_at').first()
        if last_survey:
            return last_survey.created_at
        return None

class SignInSerializer(serializers.HyperlinkedModelSerializer):
    """Class for SignInSerializer"""
    username = serializers.CharField()

    class Meta:
        """Meta class for SignInSerializer"""
        model = User
        fields = ['username']

class AudioUploadSerializer(serializers.Serializer): # pylint: disable=abstract-method
    """Serializer for audio file upload."""
    audio = serializers.FileField(required=True)
