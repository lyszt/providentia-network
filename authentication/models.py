from django.db import models

class AuthorizedApps(models.Model):
    app_name = models.CharField(max_length=255)
    api_key = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)