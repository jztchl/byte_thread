from .views import FeedView, ExploreView
from rest_framework.routers import DefaultRouter
router = DefaultRouter()
router.register(r"feeds", FeedView, basename="feeds")
router.register(r"explore", ExploreView, basename="explore")
urlpatterns = router.urls
