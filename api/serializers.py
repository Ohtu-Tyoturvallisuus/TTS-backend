# todo/todo_api/serializers.py
from rest_framework import serializers
from .models import Worksite, RiskNote, Survey
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class OverseerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username']


class SignInSerializer(serializers.Serializer):
    username = serializers.CharField()
        
class RiskNoteSerializer(serializers.HyperlinkedModelSerializer):
    def __init__(self, *args, **kwargs):
        many = kwargs.pop('many', True)
        super(RiskNoteSerializer, self).__init__(many=many, *args, **kwargs)

    class Meta:
        model = RiskNote
        fields = ['id', 'note', 'description', 'status', 'created_at']
    
    def create(self, validated_data):
        survey_id = self.context['request'].parser_context['kwargs']['survey_pk']
        validated_data['survey_id'] = survey_id
        return RiskNote.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        instance.note = validated_data.get('note', instance.note)
        instance.description = validated_data.get('description', instance.description)
        instance.status = validated_data.get('status', instance.status)
        instance.save()
        return instance

class SurveySerializer(serializers.HyperlinkedModelSerializer):
    risk_notes = RiskNoteSerializer(many=True, read_only=True, source='risknote_set')
    overseer = OverseerSerializer(read_only=True)

    class Meta:
        model = Survey
        fields = ['id', 'title', 'description', 'overseer', 'created_at', 'risk_notes']

    def create(self, validated_data):
        worksite = self.context['worksite']
        risk_survey = Survey.objects.create(worksite=worksite, **validated_data)
        return risk_survey

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.save()
        return instance

class WorksiteSerializer(serializers.ModelSerializer):
    surveys = SurveySerializer(many=True, read_only=True)
    class Meta:
        model = Worksite
        fields = ['id', 'name', 'location', 'surveys']