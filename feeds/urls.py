from .views import FeedView
from rest_framework.routers import DefaultRouter
router = DefaultRouter()
router.register(r"feeds", FeedView, basename="feeds")
urlpatterns = router.urls
