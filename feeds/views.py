from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from threads.models import Thread
from users.models import Followers
from .serializers import FeedThreadSerializer  # Assume you have a thread list serializer
from rest_framework import viewsets
from rest_framework.mixins import ListModelMixin


class FeedView(viewsets.GenericViewSet, ListModelMixin):
    permission_classes = [IsAuthenticated]
    serializer_class = FeedThreadSerializer
    pagination_class = PageNumberPagination
    page_size = 10

    def get_queryset(self):
        user = self.request.user
        followed_user_ids = Followers.objects.filter(
            follower=user,
            unfollowed_at__isnull=True
        ).values_list("following_id", flat=True)

        return Thread.objects.filter(
            user__in=followed_user_ids
        ).select_related("user").prefetch_related("images","comments","reactions").order_by("-created_at")
