from datetime import date

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.mail import EmailMessage, send_mail
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions, serializers, status
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import (TokenObtainPairSerializer,
                                                  TokenObtainSerializer)

from .models import Answer, Poll, Question, Report, Answer

User = get_user_model()


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    
    @classmethod
    def get_token(cls, user):
        token = super(MyTokenObtainPairSerializer, cls).get_token(user)
        token['name'] = user.username
        return token

class QuestionSerializer(serializers.ModelSerializer):
    
    question_type_constants = ['TEXT_RESPONSE', 'ONE_CHOICE_ANSWER', 'MULTIPLE_CHOICE_ANSWER']
    poll = serializers.PrimaryKeyRelatedField(required=False, queryset=Poll.objects.all())
    answer_choices = serializers.JSONField(required=False)
    question_type = serializers.ChoiceField(choices=question_type_constants)

    class Meta:
        model = Question
        fields = [
            'id',
            'text',
            'question_type',
            'answer_choices',
            'poll',
        ]
        extra_kwargs = {
            "text": {"required": True},
            "question_type": {"required": True},
            "answer_choices": {"required": False},
        }
    
    def validate(self, validated_data):
        if validated_data['question_type'] in ["MULTIPLE_CHOICE_ANSWER",  "ONE_CHOICE_ANSWER"]:
            if  'answer_choices' not in validated_data or len(validated_data['answer_choices']) == 0: 
                raise serializers.ValidationError(detail='put answer_choices in question', code=400)
        return  validated_data

class PollSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    
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
            'published',
            'date_start',
            'date_end',
            'questions',
        ]
        extra_kwargs = {
            "name": {"required": True},
            "description": {"required": True},
            "date_start": {"required": True},
            "date_end": {"required": True},
            "questions": {"required": False},
            "published": {"read_only": True},
        }
        depth = 1

class CreatePollSerializer(serializers.ModelSerializer):
    questions_list = serializers.ListField(child=serializers.JSONField())

    class Meta:
        model = Poll
        fields = [
            'id',
            'name',
            'description',
            'date_start',
            'date_end',
            'questions_list',
        ]
        extra_kwargs = {
            "name": {"required": True},
            "description": {"required": True},
            "date_start": {"required": True},
            "date_end": {"required": True},
            "questions_list": {"required": True},
        }
   
    # Эту проверку можно внести в validate но я решил использовать 
    # шаблон validate_<field name> для проверки конкретного поля для разнообразия
    def validate_questions_list(self, value):
        if len(value) == 0:
            raise serializers.ValidationError('pute some question to questoins_list')
        return value

    def validate(self, data):
        if data['date_start'] < date.today(): 
            raise serializers.ValidationError('Create correct start data', code=400)
        elif data['date_start'] > data['date_end']:
            raise serializers.ValidationError('Create correct start/end data', code=400)
        return data

    def create(self, validated_data):
        data = validated_data.copy()
        question_list = data.pop('questions_list')
        poll_serializer = PollSerializer(data=data) 
        if poll_serializer.is_valid(raise_exception=True):
            poll_model = poll_serializer.save()
        # associate questoins and poll model
        for question in question_list:  # TODO: Как добавить инкапсуляцию на уровне свзанных моделей 
            # Лучше использовать Serializer чем objects т.к Srializer проверяет входящие данные.
            question_serializer = QuestionSerializer(data=question)
            if question_serializer.is_valid(raise_exception=True):
                question_serializer.save(poll=poll_model)
        updated_poll_model = Poll.objects.get(pk=poll_model.pk)
        return updated_poll_model

class AnswerSerializer(serializers.ModelSerializer):
    question = serializers.PrimaryKeyRelatedField(required=True, queryset=Question.objects.all())
    class Meta:
        model = Answer
        fields = [
            'question',
            'answer',
        ]


class ReportSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, read_only=True)
    poll = serializers.PrimaryKeyRelatedField(required=True, queryset=Poll.objects.all())
    
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
    poll = serializers.PrimaryKeyRelatedField(required=True, queryset=Poll.objects.all())

    class Meta:
        model = Report
        fields = [
            'id',
            'answers_list',
            'poll',
            'user_report_id',
        ]

    def create(self, validated_data):
        data = validated_data.copy()
        answers_list = data.pop('answers_list')
        report_model = Report.objects.create(**data)

        for ans in answers_list: 
            ans_serializer = AnswerSerializer(data=ans)
            if ans_serializer.is_valid(raise_exception=True):
                ans_serializer.save(report=report_model)
        return report_model