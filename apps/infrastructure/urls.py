from rest_framework.routers import DefaultRouter
from .views import SiteViewSet, BuildingViewSet, WingViewSet, RoomViewSet

router = DefaultRouter()
router.register(r"sedes",    SiteViewSet,     basename="site")
router.register(r"edificios",BuildingViewSet, basename="building")
router.register(r"alas",     WingViewSet,     basename="wing")
router.register(r"cuartos",  RoomViewSet,     basename="room")

urlpatterns = router.urls
