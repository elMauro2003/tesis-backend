from rest_framework.routers import DefaultRouter
from .views import StudentViewSet, ProfessorViewSet

router = DefaultRouter()
router.register(r"estudiantes", StudentViewSet,  basename="student")
router.register(r"profesores",  ProfessorViewSet, basename="professor")

urlpatterns = router.urls
