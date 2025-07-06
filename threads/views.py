# Create your views here.
from django.db.models import Count
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import (
    Comment,
    CommentReactions,
    Reply,
    ReplyReactions,
    Thread,
    ThreadReactions,
)
from .serializers import (
    CommentReactionsSerializer,
    CommentSerializer,
    ReactionSerializer,
    ReplyReactionsSerializer,
    ReplySerializer,
    ThreadListSerializer,
    ThreadReactionsSerializer,
    ThreadSerializer,
)


def check_permission(user, object):
    if user == object.user:
        return True
    raise PermissionDenied("You are not allowed to perform this action")


class ThreadViewSet(viewsets.ModelViewSet):
    queryset = Thread.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "list":
            return ThreadListSerializer
        return ThreadSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def update(self, request, *args, **kwargs):
        check_permission(request.user, self.get_object())
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        check_permission(request.user, self.get_object())
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=["get"], url_path="reactions")
    def get_reactions(self, *args, **kwargs):
        results = ThreadReactions.objects.filter(thread=self.get_object())
        return Response(ThreadReactionsSerializer(results, many=True).data)

    @action(detail=True, methods=["post"], url_path="react")
    def react(self, request, *args, **kwargs):
        reaction = ReactionSerializer(data=request.data)
        if not reaction.is_valid():
            raise PermissionDenied("reaction is required")
        thread = self.get_object()
        reaction_obj, created = ThreadReactions.objects.update_or_create(
            thread=thread,
            user=self.request.user,
            defaults={"reaction": reaction.validated_data["reaction"]},
        )
        return Response({"reaction": reaction.validated_data["reaction"]})

    @action(detail=True, methods=["get"], url_path="reactions-count")
    def get_reactions_count(self, request, *args, **kwargs):
        reaction_counts = (
            ThreadReactions.objects.filter(thread=self.get_object())
            .values("reaction")
            .annotate(count=Count("id"))
        )
        return Response(reaction_counts)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_thread(self):
        try:
            return Thread.objects.get(id=self.kwargs["threads_pk"])
        except Thread.DoesNotExist:
            raise PermissionDenied("Thread not found")

    def get_queryset(self, *args, **kwargs):
        return Comment.objects.filter(thread=self.get_thread())

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, thread=self.get_thread())

    def update(self, request, *args, **kwargs):
        check_permission(request.user, self.get_object())
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        check_permission(request.user, self.get_object())
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=["get"], url_path="reactions")
    def get_reactions(self, *args, **kwargs):
        results = CommentReactions.objects.filter(comment=self.get_object())
        return Response(CommentReactionsSerializer(results, many=True).data)

    @action(detail=True, methods=["post"], url_path="react")
    def react(self, request, *args, **kwargs):
        reaction = ReactionSerializer(data=request.data)
        if not reaction.is_valid():
            raise PermissionDenied("reaction is required")
        comment = self.get_object()
        reaction_obj, created = CommentReactions.objects.update_or_create(
            comment=comment,
            user=self.request.user,
            defaults={"reaction": reaction.validated_data["reaction"]},
        )
        return Response({"reaction": reaction.validated_data["reaction"]})

    @action(detail=True, methods=["get"], url_path="reactions-count")
    def get_reactions_count(self, request, *args, **kwargs):
        reaction_counts = (
            CommentReactions.objects.filter(comment=self.get_object())
            .values("reaction")
            .annotate(count=Count("id"))
        )
        return Response(reaction_counts)


class ReplyViewSet(viewsets.ModelViewSet):
    queryset = Reply.objects.all()
    serializer_class = ReplySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self, *args, **kwargs):
        return Reply.objects.filter(comment=self.get_comment())

    def get_comment(self):
        try:
            return Comment.objects.get(id=self.kwargs["comments_pk"])
        except Comment.DoesNotExist:
            raise PermissionDenied("Comment not found")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, comment=self.get_comment())

    def update(self, request, *args, **kwargs):
        check_permission(request.user, self.get_object())
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        check_permission(request.user, self.get_object())
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=["get"], url_path="reactions")
    def get_reactions(self, *args, **kwargs):
        results = ReplyReactions.objects.filter(reply=self.get_object())
        return Response(ReplyReactionsSerializer(results, many=True).data)

    @action(detail=True, methods=["post"], url_path="react")
    def react(self, request, *args, **kwargs):
        reaction = ReactionSerializer(data=request.data)
        if not reaction.is_valid():
            raise PermissionDenied("reaction is required")
        reply = self.get_object()
        reaction_obj, created = ReplyReactions.objects.update_or_create(
            reply=reply,
            user=self.request.user,
            defaults={"reaction": reaction.validated_data["reaction"]},
        )
        return Response({"reaction": reaction.validated_data["reaction"]})

    @action(detail=True, methods=["get"], url_path="reactions-count")
    def get_reactions_count(self, request, *args, **kwargs):
        reaction_counts = (
            ReplyReactions.objects.filter(reply=self.get_object())
            .values("reaction")
            .annotate(count=Count("id"))
        )
        return Response(reaction_counts)
