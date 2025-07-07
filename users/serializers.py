from rest_framework import serializers

from core.serializers import ImageSerializer

from .models import Block, Followers, User,Mute
from django.utils import timezone

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
    is_blocked = serializers.SerializerMethodField()
    is_following = serializers.SerializerMethodField()
    is_muted = serializers.SerializerMethodField()


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

    def get_is_blocked(self, obj):
        request = self.context.get("request")
        if Block.objects.filter(blocker=request.user, blocked=obj, unblocked_at__isnull=True).exists():
            return True
        return False

    def get_is_following(self, obj):
        request = self.context.get("request")
        if Followers.objects.filter(follower=request.user, following=obj, unfollowed_at__isnull=True).exists():
            return True
        return False

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


class BlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Block
        fields = ["id", "blocked"]
        read_only_fields = ["id"]

    def validate(self, attrs):
        request = self.context.get("request")
        if request.user == attrs.get("blocked"):
            raise serializers.ValidationError("You cannot block yourself")
        if Block.objects.filter(
            blocker=request.user,
            blocked=attrs.get("blocked"),
            unblocked_at__isnull=True,
        ).exists():
            raise serializers.ValidationError("You are already blocking this user")
        return attrs

    def create(self, validated_data):
        obj=super().create(validated_data)
        blocked_following=Followers.objects.filter(following=obj.blocked, follower=obj.blocker)
        if blocked_following.exists():
            blocked_following.first().update(unfollowed_at=timezone.now())
        return obj

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["blocked"] = UserListSerializer(instance.blocked).data
        return representation


class MuteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mute
        fields = ["id", "muted"]
        read_only_fields = ["id"]

    def validate(self, attrs):
        request = self.context.get("request")
        if request.user == attrs.get("muted"):
            raise serializers.ValidationError("You cannot mute yourself")
        if Mute.objects.filter(
            muter=request.user,
            muted=attrs.get("muted"),
            unmuted_at__isnull=True,
        ).exists():
            raise serializers.ValidationError("You are already muting this user")
        return attrs

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["muted"] = UserListSerializer(instance.muted).data
        return representation
