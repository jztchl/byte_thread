from rest_framework.mixins import (
    CreateModelMixin,
    DestroyModelMixin,
    RetrieveModelMixin,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from .models import Image
from .serializers import ImageSerializer


class ImageViewSet(
    CreateModelMixin, DestroyModelMixin, RetrieveModelMixin, GenericViewSet
):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.request.user.images.all()

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
