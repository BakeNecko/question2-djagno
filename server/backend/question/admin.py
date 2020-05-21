from django.contrib import admin
from django.contrib.auth.admin import UserAdmin 
from django.contrib.auth.models import User
from .models import Report, Answer, Question, Poll, MyUser

admin.site.register(Report)
admin.site.register(Answer)
admin.site.register(Question)
admin.site.register(Poll)
admin.site.register(MyUser, UserAdmin)