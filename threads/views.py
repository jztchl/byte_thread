# Create your views here.
from rest_framework import viewsets
from .models import Thread, ThreadReactions, Comment, CommentReactions, Reply, ReplyReactions
from .serializers import ThreadSerializer, ThreadListSerializer, CommentSerializer, ReplySerializer, ThreadReactionsSerializer, CommentReactionsSerializer, ReplyReactionsSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count
from rest_framework.mixins import ListModelMixin



def check_permission(user,object):
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

    def get_queryset(self):
        return Thread.objects.filter()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_serializer_context(self):
        return {"request": self.request}

    def update(self, request, *args, **kwargs):
        check_permission(request.user, self.get_object())
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        check_permission(request.user, self.get_object())
        return super().destroy(request, *args, **kwargs)

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def get_queryset(self, *args, **kwargs):
        return Comment.objects.filter(thread=self.kwargs["threads_pk"])


class ReplyViewSet(viewsets.ModelViewSet):
    queryset = Reply.objects.all()
    serializer_class = ReplySerializer

class ThreadReactionsViewSet(ListModelMixin, viewsets.GenericViewSet):
    queryset = ThreadReactions.objects.all()
    serializer_class = ThreadReactionsSerializer
    def get_queryset(self, *args, **kwargs):
        return ThreadReactions.objects.filter(thread=self.kwargs["threads_pk"])
    @action(detail=False, methods=["post"],url_path="react")
    def react(self, request, *args, **kwargs):
        reaction = request.data.get("reaction")
        thread = Thread.objects.get(id=self.kwargs["threads_pk"])
        reaction_obj, created = ThreadReactions.objects.update_or_create(
            thread=thread,
            user=self.request.user,
            defaults={'reaction': reaction}
        )
        return Response({"reaction": reaction})
    @action(detail=False, methods=["get"],url_path="reactions-count")
    def get_reactions_count(self, request, *args, **kwargs):
       reaction_counts = (
            ThreadReactions.objects
            .filter(thread=self.kwargs["threads_pk"])
            .values('reaction')
            .annotate(count=Count('id'))
        )
       return Response(reaction_counts)

class CommentReactionsViewSet(viewsets.ModelViewSet):
    queryset = CommentReactions.objects.all()
    serializer_class = CommentReactionsSerializer

class ReplyReactionsViewSet(viewsets.ModelViewSet):
    queryset = ReplyReactions.objects.all()
    serializer_class = ReplyReactionsSerializer
