from rest_framework.routers import DefaultRouter

from .views import FollowViewSet, SuggestedUsersView, UserViewSet

router = DefaultRouter()
router.register(r"users", UserViewSet)
router.register(r"follow", FollowViewSet)
router.register(r"suggested-users", SuggestedUsersView, basename="suggested-users")

urlpatterns = router.urls
