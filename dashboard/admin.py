from django.contrib import admin
from .models import LogsHolder, error_logs

# Register your models here.
admin.site.register(LogsHolder)
admin.site.register(error_logs)
