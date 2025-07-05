from rest_framework import serializers

from core.serializers import ImageSerializer

from .models import Followers, User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = [
            "password",
            "is_active",
            "is_staff",
            "is_superuser",
            "last_login",
            "groups",
            "user_permissions",
        ]
        extra_kwargs = {"password": {"write_only": True}}

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        avatar = instance.avatar
        if avatar:
            representation["avatar"] = ImageSerializer(avatar).data
        else:
            representation["avatar"] = None
        return representation


class UserDetailForOthersSerializer(serializers.ModelSerializer):
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "avatar",
            "bio",
            "is_verified",
            "stack",
            "github_url",
            "followers_count",
            "following_count",
        ]

    def get_followers_count(self, obj):
        return obj.followers.filter(unfollowed_at__isnull=True).count()

    def get_following_count(self, obj):
        return obj.following.filter(unfollowed_at__isnull=True).count()

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        avatar = instance.avatar
        if avatar:
            representation["avatar"] = ImageSerializer(avatar).data
        else:
            representation["avatar"] = None
        return representation


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "avatar", "is_verified"]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        avatar = instance.avatar
        if avatar:
            representation["avatar"] = ImageSerializer(avatar).data
        else:
            representation["avatar"] = None
        return representation


class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Followers
        fields = ["id", "following"]

    def validate(self, attrs):
        request = self.context.get("request")
        if request.user == attrs.get("following"):
            raise serializers.ValidationError("You cannot follow yourself")
        if Followers.objects.filter(
            follower=request.user,
            following=attrs.get("following"),
            unfollowed_at__isnull=True,
        ).exists():
            raise serializers.ValidationError("You are already following this user")
        return attrs

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["following"] = UserSerializer(instance.following).data
        return representation
