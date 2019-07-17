from django.db import models

class LogsHolder(models.Model):
    remoteAddr = models.CharField(max_length=100)
    remoteUser = models.CharField(max_length=10000)
    timeLocal = models.DateTimeField()
    request = models.CharField(max_length=10000)
    status = models.CharField(max_length=100)
    bodyBytesSent = models.CharField(max_length=100)
    httpReferer = models.CharField(max_length=1000)
    httpUserAgent = models.CharField(max_length=100000)
    authorizedUser = models.BooleanField()

class error_logs(models.Model):
    date = models.DateField()
    time = models.TimeField()
    level = models.CharField(max_length=40)
    pid = models.CharField(max_length=15)
    tid = models.CharField(max_length=50)
    message = models.CharField(max_length=100000)
    client = models.CharField(max_length=590)
    request = models.CharField(max_length=100000)