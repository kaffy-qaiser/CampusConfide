from django.contrib import admin
from .models import Report, AdminNote, Notification

# Register your models here.
admin.site.register(Report)
admin.site.register(AdminNote)
admin.site.register(Notification)
