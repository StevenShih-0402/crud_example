from rest_framework.routers import DefaultRouter

from app.book.views.book_view import BookViewSet

router = DefaultRouter()
router.register(r'books', BookViewSet, basename='book')

urlpatterns = router.urls
