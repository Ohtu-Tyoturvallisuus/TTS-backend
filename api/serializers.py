# todo/todo_api/serializers.py
from rest_framework import serializers
from .models import Worksite, RiskNote, Survey
from django.contrib.auth.models import User

class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class OverseerSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['username']

class RiskNoteSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
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
    worksite = serializers.ReadOnlyField(source='worksite.name')
    overseer = serializers.ReadOnlyField(source='overseer.username')
    risk_notes = RiskNoteSerializer(many=True, read_only=True)
    risks = serializers.JSONField()

    class Meta:
        model = Survey
        fields = ['id', 'worksite', 'overseer', 'title', 'description',  'created_at', 'risk_notes', 'risks']

class SurveyNestedSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='survey-detail', read_only=True)

    class Meta:
        model = Survey
        fields = ['url', 'id', 'title', 'created_at']

class WorksiteSerializer(serializers.HyperlinkedModelSerializer):
    surveys = SurveyNestedSerializer(many=True, read_only=True)

    class Meta:
        model = Worksite
        fields = ['id', 'name', 'location', 'surveys']

class SignInSerializer(serializers.HyperlinkedModelSerializer):
    username = serializers.CharField()
