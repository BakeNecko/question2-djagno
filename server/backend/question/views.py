from datetime import date

from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404, render
from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes

from .models import Answer, Poll, Question, Report
from .serializers import (AnswerSerializer, CreateReportSerializer,
                          PollSerializer, QuestionSerializer, ReportSerializer,
                          CreatePollSerializer)
from .permissoins import ReportIDPermissions, ReportCreatePermissions

# Move create-logic ReportViewSet в Serializer
class ReportViewSet(viewsets.ModelViewSet):
    serializer_class = ReportSerializer
    permission_classes = [permissions.AllowAny, ReportCreatePermissions] 

    def get_queryset(self):
        user = self.request.user
        if user.is_anonymous != True:
            if user.is_staff:
                return Report.objects.all()
            else: 
                return Report.objects.filter(user_report_id=user.report_id)
        else:
            return None

    def create(self, request):
        data = request.data.copy()
        self.check_permissions    
        serializer = CreateReportSerializer(data=data)

        if serializer.is_valid(raise_exception=True):
            if 'user_report_id' in data:
                model = serializer.save()
            else: 
                if request.user.is_anonymous == False: 
                    model = serializer.save(user_report_id=request.user.report_id)
                elif request.user.is_anonymous == True: 
                    model = serializer.save()

        serializer = ReportSerializer(model, context={'request': request})
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)


class QuestionViewSet(viewsets.ModelViewSet):
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAdminUser, ] 
    queryset = Question.objects.all()
    lookup_url_kwarg = 'pk'

    def create(self, request):
        self.check_permissions
        data = request.data
        poll_id = data['poll_id']
        poll = get_object_or_404(Poll, pk=poll_id)
        question_serializer = QuestionSerializer(data=data)
        if question_serializer.is_valid(raise_exception=True):
            question_serializer.save(poll=poll)
        return Response(question_serializer.data, status=status.HTTP_201_CREATED)

    
class PollViewSet(viewsets.ModelViewSet):
    serializer_class = PollSerializer
    permission_classes = [permissions.IsAdminUser, ]

    def create(self, request):
        self.check_permissions(self.request)
        data = request.data
        poll_serializer = CreatePollSerializer(data=data)
        if poll_serializer.is_valid(raise_exception=True):
            model = poll_serializer.save()
        poll_serializer = self.serializer_class(model)
        return Response(data=poll_serializer.data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, pk=None):
        self.check_permissions
        poll = self.get_object()
        serializer = PollSerializer(poll, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def get_queryset(self):
        self.check_permissions
        queryset = Poll.objects.get_active_poll()  # Check PollManger in models.py
        return queryset

    def get_permissions(self):
        # Врено объеденил проверки я пытался их согласовать через or это было ошибкой 
        if self.action in ['list','retrieve']:
            permission_classes = [permissions.AllowAny,]
        else:
            permission_classes = [permissions.IsAdminUser,]
        return [permission() for permission in permission_classes]


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, ReportIDPermissions])
def user_report_id(request):
    data = request.data
    user_report_id = data['user_report_id']
    reports = Report.objects.filter(user_report_id=user_report_id)
    report_data = ReportSerializer(reports, many=True, context={'request': request}).data
    return Response(data=report_data, status=status.HTTP_200_OK)
