from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework_simplejwt import views as jwt_views

from .tokens import ObtainTokenPair
from .views import PollViewSet, QuestionViewSet, ReportViewSet, user_report_id

pool = PollViewSet.as_view({
  'get': 'list',
  'post': 'create',
})
pool_detail = PollViewSet.as_view({
  'get': 'retrieve',
  'delete': 'destroy',
  'put': 'partial_update',
})
question_detail = QuestionViewSet.as_view({
  'get': 'retrieve',
  'delete': 'destroy',
  'put': 'partial_update',
})
report = ReportViewSet.as_view({
  'get': 'list',
  'post': 'create'
})
report_detail = ReportViewSet.as_view({
  'get': 'retrieve',
})

urlpatterns = [
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(),  name='token_refresh'), 
    path('log_in/', ObtainTokenPair.as_view(), name='login'), 
    # Poll logic
    path('poll/', pool, name='poll' ), # OK 
    path('poll/<int:pk>/', pool_detail, name='poll_detail' ), # OK
    # Question logic
    path('question/', QuestionViewSet.as_view({'post': 'create'}), name='question'), # OK 
    path('question/<int:pk>/', question_detail, name='question_detail' ), # OK
    # Report login 
    path('report/', report, name = 'report'),
    path('report/<int:pk>/', report_detail, name = 'retrieve'),
    path('report/user_report_id/', user_report_id, name='user_report_id')
]
