from rest_framework.routers import DefaultRouter

from .views import FollowViewSet, UserViewSet

router = DefaultRouter()
router.register(r"users", UserViewSet)
router.register(r"follow", FollowViewSet)

urlpatterns = router.urls
