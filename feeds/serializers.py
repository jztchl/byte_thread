from rest_framework import serializers
from threads.models import Thread
from users.serializers import UserListSerializer

class FeedThreadSerializer(serializers.ModelSerializer):
    user = UserListSerializer(read_only=True)
    reactions_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Thread
        fields = ["id", "title", "content", "created_at", "user", "reactions_count", "comments_count"]

    def get_reactions_count(self, obj):
        return obj.reactions.count()

    def get_comments_count(self, obj):
        return obj.comments.count()
