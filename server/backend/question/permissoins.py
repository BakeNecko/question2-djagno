from rest_framework.permissions import BasePermission, IsAuthenticated, SAFE_METHODS
from .models import Report

class ReportIDPermissions(BasePermission):
    def has_permission(self, request, view):
        if request.method == 'POST':
            data = request.data
            user = request.user
            user_report_id = data['user_report_id']
            if user.is_staff:
              return True 
            else: 
              return user.report_id == user_report_id
        else:
            return False

class ReportCreatePermissions(BasePermission):
    def has_permission(self, request, view):
      data = request.data
      if 'user_report_id' in data:
          if request.user.is_anonymous == False: 
              if request.user.is_staff: 
                  return True
              else: 
                  return request.user.report_id == request.data['user_report_id']
          else: 
              if request.data['user_report_id'] is not None: 
                  return False
      else:
        print('this')
        return True   