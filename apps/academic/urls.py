from rest_framework.routers import DefaultRouter
from .views import FacultyViewSet, CareerViewSet, CareerYearViewSet, GroupViewSet

router = DefaultRouter()
router.register(r"facultades",      FacultyViewSet,    basename="faculty")
router.register(r"carreras",        CareerViewSet,     basename="career")
router.register(r"anios-academicos",CareerYearViewSet, basename="career-year")
router.register(r"grupos",          GroupViewSet,      basename="group")

urlpatterns = router.urls
