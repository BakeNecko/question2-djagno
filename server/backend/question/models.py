from datetime import date

from django.db import models
from django.urls import reverse
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError

import jsonfield


class MyUser(AbstractUser):
    # В обычной ситуации когда нужно создать связь с полем а не с моделью
    # В вторичной модели (Report) в поле user_report_id нужно указать
    # параметр to_field='report_id' но это создаст прямую свзяь с моделью MyUser 
    # Но вы сказали связи с моделью User не должно быть
    report_id = models.BigIntegerField(blank=True,null=True, unique=True)


class PollManger(models.Manager):
    def get_active_poll(self):
        return super(PollManger, self).get_queryset().filter(date_end__gte=date.today()).order_by('date_start')

class Poll(models.Model):
    name = models.CharField(blank=False, max_length=40, null=False)
    description = models.TextField(blank=False, null=False)
    published = models.DateField(auto_now=True)
    date_start = models.DateField(blank=False, null=False)
    date_end = models.DateField(blank=False, null=False)

    objects = PollManger()

    @property
    def is_active(self):
        return date.today() > self.date_end

    def clean(self):
        errors = {}
        today = date.today()
        if self.date_start > self.date_end: 
            errors['start_end_date'] = ValidationError("date_start should be more than date_end")
        if self.date_start < today: 
            errors['date_start'] = ValidationError("date_start should be more than today")
        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Poll'
        verbose_name_plural = 'Polls'


class Question(models.Model):
    TEXT_RESPONSE = 'TEXT_RESPONSE'
    ONE_CHOICE_ANSWER = 'ONE_CHOICE_ANSWER'
    MULTIPLE_CHOICE_ANSWER = 'MULTIPLE_CHOICE_ANSWER'
    state_dict = [
        (TEXT_RESPONSE, 'TEXT_RESPONSE'),
        (ONE_CHOICE_ANSWER, 'ONE_CHOICE_ANSWER'),
        (MULTIPLE_CHOICE_ANSWER, 'MULTIPLE_CHOICE_ANSWER'),
    ]
    poll = models.ForeignKey(Poll, related_name='questions', on_delete=models.CASCADE)
    text  = models.TextField()
    question_type = models.CharField(choices=state_dict, max_length=244)
    answer_choices = jsonfield.JSONField(blank=True, null=True)
    class Meta:
        verbose_name = 'Question'
        verbose_name_plural = 'Questions'
        
    def __str__(self):
        return f'{self.poll.name}-question-{self.pk}'

    def get_absolute_url(self):
        return reverse("question_detail", kwargs={"pk": self.pk})
    

class Report(models.Model):
    user_report_id = models.BigIntegerField(blank=True,null=True, default=None)
    poll = models.ForeignKey(Poll, related_name='reports', on_delete=models.CASCADE)

    @property
    def is_anon_user(self):
        if self.user_report_id != None:
            return False
        else: 
            return True 

    class Meta:
            verbose_name = 'Report'
            verbose_name_plural = 'Report'
            
    def __str__(self):
        return f'report-{self.pk}'

class Answer(models.Model):
    question = models.ForeignKey(Question, related_name='answers', on_delete=models.PROTECT)
    report = models.ForeignKey(Report, related_name='answers', on_delete=models.CASCADE)
    answer = models.TextField()

    class Meta:
        verbose_name = 'Report Answer'
        verbose_name_plural = 'Report Answers'

