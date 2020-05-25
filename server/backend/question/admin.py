from django.contrib import admin
from django.contrib.auth.models import User
from .models import Report, Answer, Question, Poll, MyUser
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
# Register your models here.
@admin.register(MyUser)
class UserAdmin(admin.ModelAdmin):
    fields = (
        'pk', 'username', 'report_id'
    )
    list_display = (
        'pk', 'username', 'report_id'
    )
    list_filter = (
        'id',
    )
    readonly_fields = (
        'pk', 'id'
    )

admin.site.register(Report)
admin.site.register(Answer)
admin.site.register(Question)
admin.site.register(Poll)