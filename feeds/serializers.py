from rest_framework import serializers

from core.serializers import ImageSerializer
from threads.models import Thread
from users.serializers import UserListSerializer


class FeedThreadSerializer(serializers.ModelSerializer):
    user = UserListSerializer(read_only=True)
    reactions_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Thread
        fields = [
            "id",
            "title",
            "content",
            "images",
            "created_at",
            "user",
            "reactions_count",
            "comments_count",
        ]

    def get_reactions_count(self, obj):
        return obj.reactions.count()

    def get_comments_count(self, obj):
        return obj.comments.count()

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        images = instance.images.all()
        if images:
            representation["images"] = ImageSerializer(images, many=True).data
        else:
            representation["images"] = None
        return representation
