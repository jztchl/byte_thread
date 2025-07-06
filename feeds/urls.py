from rest_framework.routers import DefaultRouter

from .views import ExploreView, FeedView

router = DefaultRouter()
router.register(r"feeds", FeedView, basename="feeds")
router.register(r"explore", ExploreView, basename="explore")
urlpatterns = router.urls
