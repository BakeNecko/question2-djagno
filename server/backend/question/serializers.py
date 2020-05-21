from django.core.mail import EmailMessage, send_mail
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.http import Http404
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.shortcuts import get_object_or_404

from rest_framework import exceptions, serializers, status
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import (TokenObtainPairSerializer,
                                                  TokenObtainSerializer)
from .models import Report, Answer, Question, Poll

User = get_user_model()


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super(MyTokenObtainPairSerializer, cls).get_token(user)
        token['name'] = user.username
        return token

class QuestionSerializer(serializers.ModelSerializer):
    answer_choices = serializers.JSONField(required=False)

    class Meta:
        model = Question
        fields = [
            'id',
            'text',
            'question_type',
            'answer_choices',
        ]
        extra_kwargs = {
            "text": {"required": True},
            "question_type": {"required": True},
        }
        depth = 1  

class PollSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    name = serializers.CharField(required=True)
    description = serializers.CharField(required=True)
    date_start = serializers.DateField(required=True)
    date_end = serializers.DateField(required=True)

    # Dont get update start_date field
    def update(self, instance, validated_data):
        validated_keys = list((validated_data.keys()))
        if 'name' in validated_keys:
            instance.name = validated_data.get('name', instance.name)
        if 'description' in validated_keys:
            instance.description = validated_data.get('description', instance.description)
        if 'date_end' in validated_keys:
            instance.date_end = validated_data.get('date_end', instance.date_end)
        if 'date_start' in validated_keys:
            raise exceptions.ValidationError(detail='U cant change date_start', code=400)
        instance.save()
        return instance

    class Meta:
        model = Poll
        fields = [
            'id',
            'name',
            'description',
            'date_start',
            'date_end',
            'questions'
        ]
        extra_kwargs = {
            "name": {"required": True},
            "description": {"required": True},
            "date_start": {"required": True},
            "date_end": {"required": True},
            "questions": {"required": False},
        }
        depth = 1


class AnswerSerializer(serializers.ModelSerializer):
    question = QuestionSerializer(many=False, required=False, read_only=True)
    class Meta:
        model = Answer
        fields = [
            'question',
            'answer',
        ]


class ReportSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, read_only=True)
    poll = serializers.HyperlinkedRelatedField(required=False,many=False, read_only=True, view_name='poll_detail')
    
    class Meta:
        model = Report
        fields = [
            'id',
            'poll',
            'answers',
            'user_report_id',
        ]

    
class CreateReportSerializer(serializers.ModelSerializer):
    answers_list = serializers.ListField(child=serializers.JSONField())
    poll_id = serializers.IntegerField(required=True)
   
    class Meta:
        model = Report
        fields = [
            'id',
            'answers_list',
            'poll_id',
            'user_report_id',
        ]

    def create(self, validated_data): 
        data = validated_data.copy()
        answers =  data.pop('answers_list')
        poll_id = data.pop('poll_id')
        poll = get_object_or_404(Poll, pk=poll_id)
        print(data)
        report_model = Report.objects.create(**data, poll=poll)
        for answer in answers:
            question = get_object_or_404(Question, pk=answer['question_id']) 
            answer_serializer = AnswerSerializer(data=answer)
            if answer_serializer.is_valid(raise_exception=True):
                answer_serializer.save(report=report_model, question=question)
        report_model.poll = poll
        report_model.save()
        new_report_model = Report.objects.get(pk=report_model.pk)
        return new_report_model