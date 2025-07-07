# Create your models here.
from users.models import User
from django.db import models
from core.models import SoftDelete, Timestamp


class Conversation(Timestamp, SoftDelete):
    TYPE_CHOICES = [
        ('private', 'Private'),
        ('group', 'Group'),
    ]

    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    name = models.CharField(max_length=100)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_conversations')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.type} chat #{self.id} - {self.name}"

class Participant(Timestamp, SoftDelete):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('member', 'Member'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="participants")
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="participants")
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='member')
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'conversation')

    def __str__(self):
        return f"{self.user} in {self.conversation}"

class Message(Timestamp, SoftDelete):
    MESSAGE_TYPE = [
        ('text', 'Text'),
        ('image', 'Image'),
        ('file', 'File'),
    ]

    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="messages")
    content = models.TextField(blank=True)
    media = models.ForeignKey("core.Image", null=True, blank=True, on_delete=models.SET_NULL)
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPE, default='text')
    reply_to = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username}: {self.content[:20]}"


class MessageStatus(Timestamp, SoftDelete):
    STATUS_CHOICES = [
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('seen', 'Seen'),
    ]

    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='statuses')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='sent')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('message', 'user')

    def __str__(self):
        return f"{self.user} - {self.status} for msg {self.message}"
