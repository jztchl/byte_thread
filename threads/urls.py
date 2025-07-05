from rest_framework_nested.routers import DefaultRouter, NestedDefaultRouter
from .views import ThreadViewSet, CommentViewSet, ReplyViewSet, CommentReactionsViewSet, ReplyReactionsViewSet

router = DefaultRouter()
router.register("threads", ThreadViewSet)
nested_thread_router = NestedDefaultRouter(router, r"threads", lookup="threads")
nested_thread_router.register("comments", CommentViewSet)
nested_thread_router.register("replies", ReplyViewSet)

nested_thread_router.register("comment-reactions", CommentReactionsViewSet)
nested_thread_router.register("reply-reactions", ReplyReactionsViewSet)

urlpatterns = router.urls + nested_thread_router.urls
