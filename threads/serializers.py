from rest_framework import serializers

from users.serializers import UserListSerializer
from .models import Thread, ThreadReactions, Comment, CommentReactions, Reply, ReplyReactions
from core.serializers import ImageSerializer
from core.models import Image


class ThreadSerializer(serializers.ModelSerializer):
    images = serializers.PrimaryKeyRelatedField(many=True, queryset=Image.objects.all(), required=False)
    class Meta:
        model = Thread
        fields = '__all__'
        extra_kwargs = {
            "user": {"read_only": True},
        }

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["images"] = ImageSerializer(instance.images.all(), many=True).data
        representation["user"] = UserListSerializer(instance.user).data
        return representation


    def update(self, instance, validated_data):
        images = validated_data.pop("images", None)
        instance = super().update(instance, validated_data)
        if images:
            instance.images.set(images)
        return instance

class ThreadListSerializer(serializers.ModelSerializer):
    cover_image = serializers.PrimaryKeyRelatedField(queryset=Image.objects.all(), required=False)
    class Meta:
        model = Thread
        fields = ['id', 'title', 'cover_image']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["cover_image"] = ImageSerializer(instance.images.first()).data
        return representation

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'


class ReplySerializer(serializers.ModelSerializer):
    class Meta:
        model = Reply
        fields = '__all__'

class ThreadReactionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ThreadReactions
        fields = ['reaction','thread','user']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["user"] = UserListSerializer(instance.user).data
        return representation

class CommentReactionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentReactions
        fields = '__all__'

class ReplyReactionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReplyReactions
        fields = '__all__'
