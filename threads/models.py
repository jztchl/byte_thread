from django.db import models
from users.models import User

class CommentType(models.TextChoices):
   TEXT = "text", "Text"
   IMAGE = "image", "Image"


class Reactions(models.TextChoices):
   LIKE = "like", "Like"
   DISLIKE = "dislike", "Dislike"
   LOVE = "love", "Love"
   HATE = "hate", "Hate"
   WOW = "wow", "Wow"
   SAD = "sad", "Sad"
   ANGRY = "angry", "Angry"
   LAUGH = "laugh", "Laugh"


class Thread(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    content = models.TextField()
    images = models.ManyToManyField("core.Image", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment_type = models.CharField(max_length=10, choices=CommentType.choices)
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    images = models.ForeignKey("core.Image", on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.content

class Reply(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='replies')
    content = models.TextField()
    comment_type = models.CharField(max_length=10, choices=CommentType.choices)
    images = models.ForeignKey("core.Image", on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.content


class ThreadReactions(models.Model):
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name='reactions')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reaction = models.CharField(max_length=10, choices=Reactions.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} {self.reaction} {self.thread}"
    class Meta:
        unique_together = ('thread', 'user')


class CommentReactions(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='reactions')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reaction = models.CharField(max_length=10, choices=Reactions.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} {self.reaction} {self.comment}"
    class Meta:
        unique_together = ('comment', 'user')


class ReplyReactions(models.Model):
    reply = models.ForeignKey(Reply, on_delete=models.CASCADE, related_name='reactions')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reaction = models.CharField(max_length=10, choices=Reactions.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} {self.reaction} {self.reply}"
    class Meta:
        unique_together = ('reply', 'user')
