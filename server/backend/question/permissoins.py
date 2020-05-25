from rest_framework.permissions import BasePermission, IsAuthenticated, SAFE_METHODS
from .models import Report, Poll
from django.db.models import Q

def check_user_field_permission(user_field, data_object:str):
    return user_field == data_object

class ReportIDPermissions(BasePermission):
    def has_permission(self, request, view):
        if request.method == 'POST':
            data = request.data
            user = request.user
            user_report_id = data['user_report_id']
            if user.is_staff:
                return True 
            else:   
                return check_user_field_permission(user.report_id, user_report_id)
        else:
            return False

class ReportCreatePermissions(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        data = request.data

        if user.is_staff: 
            return True

        # One user cannot answer several times
        poll = Poll.objects.get(pk=data['poll'])
        if user.is_anonymous == False: 
            user_report = Report.objects.filter(Q(user_report_id=user.report_id) & Q(poll=poll))
            if len(user_report) != 0:
                return False

        # Security check 
        if 'user_report_id' in data:
            user_report_id = request.data['user_report_id']
            if user.is_anonymous == False: 
                return check_user_field_permission(user.report_id, user_report_id)
            else: 
                if request.data['user_report_id'] is not None: 
                    return False
        else:
            return True   