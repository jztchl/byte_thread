from rest_framework_nested.routers import DefaultRouter, NestedDefaultRouter

from .views import CommentViewSet, ReplyViewSet, ThreadViewSet

router = DefaultRouter()
router.register("threads", ThreadViewSet)
nested_thread_router = NestedDefaultRouter(router, r"threads", lookup="threads")
nested_thread_router.register("comments", CommentViewSet)
nested_comment_router = NestedDefaultRouter(
    nested_thread_router, r"comments", lookup="comments"
)
nested_comment_router.register("replies", ReplyViewSet)
urlpatterns = router.urls + nested_thread_router.urls + nested_comment_router.urls
