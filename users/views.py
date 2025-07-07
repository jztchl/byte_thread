from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.exceptions import MethodNotAllowed, PermissionDenied
from rest_framework.mixins import ListModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from .models import Followers, User, Block
from .serializers import (
    FollowSerializer,
    UserDetailForOthersSerializer,
    UserListSerializer,
    UserSerializer,
    BlockSerializer,
    MuteSerializer,
)


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return UserDetailForOthersSerializer
        elif self.action == "list":
            return UserListSerializer
        return UserSerializer

    def get_serializer_context(self):
        return {"request": self.request}

    def create(self, request, *args, **kwargs):
        raise PermissionDenied("You can only create a user through registration")

    def update(self, request, *args, **kwargs):
        if request.user != self.get_object():
            raise PermissionDenied("You can only update your own profile")
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        if request.user != self.get_object():
            raise PermissionDenied("You can only update your own profile")
        return super().partial_update(request, *args, **kwargs)

    @action(detail=False, methods=["get"])
    def me(self, request):
        return Response(UserSerializer(request.user).data)

    @action(detail=False, methods=["post"])
    def block(self, request):
        serializer = BlockSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(blocker=request.user)
        return Response(serializer.data)

    @action(detail=False, methods=["post"])
    def mute(self, request):
        serializer = MuteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(muter=request.user)
        return Response(serializer.data)


    @action(detail=False, methods=["get"])
    def block_list(self, request):
        return Response(BlockSerializer(request.user.blockers.all(), many=True).data)

    @action(detail=False, methods=["get"])
    def mute_list(self, request):
        return Response(MuteSerializer(request.user.muters.all(), many=True).data)


class FollowViewSet(ModelViewSet):
    queryset = Followers.objects.all().select_related("following")
    serializer_class = FollowSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        return {"request": self.request}

    def get_queryset(self):
        return self.queryset.filter(
            follower=self.request.user, unfollowed_at__isnull=True
        )

    def perform_create(self, serializer):
        serializer.save(follower=self.request.user)

    def perform_destroy(self, instance):
        instance.unfollowed_at = timezone.now()
        instance.save()

    def update(self, request, *args, **kwargs):
        raise MethodNotAllowed("You can only create or delete a follow")


class SuggestedUsersView(GenericViewSet, ListModelMixin):
    queryset = User.objects.all()
    serializer_class = UserListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        blocked_user_ids = Block.objects.filter(
            blocker=user, unblocked_at__isnull=True
        ).values_list("blocked_id", flat=True)

        # 1. Users you already follow
        already_following_ids = Followers.objects.filter(
            follower=user, unfollowed_at__isnull=True
        ).values_list("following_id", flat=True)

        # 2. Your followers
        your_followers_ids = Followers.objects.filter(
            following=user, unfollowed_at__isnull=True
        ).values_list("follower_id", flat=True)

        # 3. People your followers are following
        friends_of_friends_ids = (
            Followers.objects.filter(
                follower_id__in=your_followers_ids, unfollowed_at__isnull=True
            )
            .exclude(following_id__in=list(already_following_ids) + [user.id]+list(blocked_user_ids))
            .order_by("?")[:20]
            .values("following_id")
        )
        return User.objects.filter(id__in=friends_of_friends_ids).order_by(
            "-date_joined"
        )
