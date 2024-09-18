# todo/todo_api/serializers.py
from rest_framework import serializers
from .models import Worksite, RiskNote, RiskSurvey

class RiskNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = RiskNote
        fields = ['id', 'note', 'created_at']
    
    def create(self, validated_data):
        worksite = self.context['worksite']
        risk_note = RiskNote.objects.create(worksite=worksite, **validated_data)
        return risk_note
    
    def update(self, instance, validated_data):
        instance.note = validated_data.get('note', instance.note)
        instance.save()
        return instance

class RiskSurveySerializer(serializers.ModelSerializer):
    risk_notes = RiskNoteSerializer(many=True, read_only=True, source='risknote_set')
    class Meta:
        model = RiskSurvey
        fields = ['id', 'title', 'description', 'created_at', 'risk_notes']

    def create(self, validated_data):
        worksite = self.context['worksite']
        risk_survey = RiskSurvey.objects.create(worksite=worksite, **validated_data)
        return risk_survey

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.save()
        return instance

class WorksiteSerializer(serializers.ModelSerializer):
    risk_surveys = RiskSurveySerializer(many=True, read_only=True, source='risksurvey_set')
    class Meta:
        model = Worksite
        fields = ['id', 'name', 'location', 'risk_surveys']