from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    github_url = models.URLField(blank=True, null=True)
    stack = models.JSONField(default=list)
    avatar = models.ForeignKey("core.Image", on_delete=models.SET_NULL, null=True)
    bio = models.TextField(blank=True)
    is_verified = models.BooleanField(default=False)


class Followers(models.Model):
    follower = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="following"
    )
    following = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="followers"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    unfollowed_at = models.DateTimeField(default=None, null=True)

    def __str__(self):
        return f"{self.follower} → {self.following}"
