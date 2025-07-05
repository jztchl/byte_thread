from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    github_url = models.URLField(blank=True, null=True)
    stack = models.JSONField(default=list)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    bio = models.TextField(blank=True)
    is_verified = models.BooleanField(default=False)
