from django.db.models import Count
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import viewsets
from rest_framework.mixins import ListModelMixin
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated

from threads.models import Thread
from users.models import Followers

from .serializers import (
    FeedThreadSerializer,
)  # Assume you have a thread list serializer


class FeedPagination(PageNumberPagination):
    page_size = 10
    page_query_param = "page"


@method_decorator(cache_page(10), name="list")
class FeedView(viewsets.GenericViewSet, ListModelMixin):
    permission_classes = [IsAuthenticated]
    serializer_class = FeedThreadSerializer
    pagination_class = FeedPagination

    def get_queryset(self):
        user = self.request.user
        sort = self.request.query_params.get("sort")
        followed_user_ids = Followers.objects.filter(
            follower=user, unfollowed_at__isnull=True
        ).values_list("following_id", flat=True)
        list_of_ids = list(followed_user_ids) + [user.id]

        # make table to mute and block users

        qs = (
            Thread.objects.filter(user__in=list_of_ids)
            .select_related("user")
            .prefetch_related("images", "comments", "reactions")
            .order_by("-created_at")
        )

        if sort == "comments":
            qs = qs.annotate(comments_count=Count("comments")).order_by(
                "-comments_count", "-created_at"
            )
            return qs
        elif sort == "reactions":
            qs = qs.annotate(reactions_count=Count("reactions")).order_by(
                "-reactions_count", "-created_at"
            )
            return qs
        elif sort == "old":
            qs = qs.order_by("created_at")
            return qs
        return qs


@method_decorator(cache_page(10), name="list")
class ExploreView(viewsets.GenericViewSet, ListModelMixin):
    permission_classes = [AllowAny]
    serializer_class = FeedThreadSerializer
    pagination_class = FeedPagination

    def get_queryset(self):
        return Thread.objects.annotate(
            hot_score=Count("reactions") + Count("comments")
        ).order_by("-hot_score", "-created_at")
