from rest_framework import serializers

from core.models import Image
from core.serializers import ImageSerializer
from users.serializers import UserListSerializer

from .models import (
    Comment,
    CommentReactions,
    CommentType,
    Reactions,
    Reply,
    ReplyReactions,
    Thread,
    ThreadReactions,
)


class ThreadSerializer(serializers.ModelSerializer):
    images = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Image.objects.all(), required=False
    )

    class Meta:
        model = Thread
        fields = "__all__"
        extra_kwargs = {
            "user": {"read_only": True},
        }

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["images"] = ImageSerializer(
            instance.images.all(), many=True
        ).data
        representation["user"] = UserListSerializer(instance.user).data
        return representation

    def update(self, instance, validated_data):
        images = validated_data.pop("images", None)
        instance = super().update(instance, validated_data)
        if images:
            instance.images.set(images)
        return instance


class ThreadListSerializer(serializers.ModelSerializer):
    cover_image = serializers.PrimaryKeyRelatedField(
        queryset=Image.objects.all(), required=False
    )

    class Meta:
        model = Thread
        fields = ["id", "title", "cover_image"]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["cover_image"] = ImageSerializer(instance.images.first()).data
        return representation


class CommentSerializer(serializers.ModelSerializer):
    content = serializers.CharField(required=False)
    image = serializers.PrimaryKeyRelatedField(
        queryset=Image.objects.all(), required=False
    )

    class Meta:
        model = Comment
        fields = "__all__"
        read_only_fields = ["user", "thread"]

    def validate(self, attrs):
        type = attrs.get("comment_type")
        if type == CommentType.IMAGE:
            attrs["images"] = attrs.pop("images", None)
            if not attrs["images"]:
                raise serializers.ValidationError({"images": "This field is required."})
        elif type == CommentType.TEXT:
            attrs["content"] = attrs.pop("content", None)
            if not attrs["content"]:
                raise serializers.ValidationError(
                    {"content": "This field is required."}
                )
        return super().validate(attrs)

    def update(self, instance, validated_data):
        images = validated_data.pop("images", None)
        instance = super().update(instance, validated_data)
        if images:
            instance.image = images
        instance.save()
        return instance


class ReplySerializer(serializers.ModelSerializer):
    content = serializers.CharField(required=False)
    image = serializers.PrimaryKeyRelatedField(
        queryset=Image.objects.all(), required=False
    )

    class Meta:
        model = Reply
        fields = "__all__"
        read_only_fields = ["user", "comment"]

    def validate(self, attrs):
        type = attrs.get("comment_type")
        if type == CommentType.IMAGE:
            attrs["images"] = attrs.pop("images", None)
            if not attrs["images"]:
                raise serializers.ValidationError({"images": "This field is required."})
        elif type == CommentType.TEXT:
            attrs["content"] = attrs.pop("content", None)
            if not attrs["content"]:
                raise serializers.ValidationError(
                    {"content": "This field is required."}
                )
        return super().validate(attrs)


class ReactionSerializer(serializers.Serializer):
    reaction = serializers.ChoiceField(choices=Reactions.choices, required=True)


class ThreadReactionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ThreadReactions
        fields = ["reaction", "thread", "user"]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["user"] = UserListSerializer(instance.user).data
        return representation


class CommentReactionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentReactions
        fields = ["reaction", "comment", "user"]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["user"] = UserListSerializer(instance.user).data
        return representation


class ReplyReactionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReplyReactions
        fields = ["reaction", "reply", "user"]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["user"] = UserListSerializer(instance.user).data
        return representation
