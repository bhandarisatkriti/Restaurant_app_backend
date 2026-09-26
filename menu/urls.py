from rest_framework.routers import DefaultRouter
from .views import MenuItemViewSet,CategoryViewSet

router = DefaultRouter()
router.register('category', CategoryViewSet , basename='category')
router.register('items', MenuItemViewSet, basename='menuitem')
urlpatterns=router.urls