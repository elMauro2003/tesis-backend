from rest_framework.routers import DefaultRouter
from .views import (
    ComplaintViewSet, EvaluationViewSet, CleaningScheduleViewSet,
    AssignmentViewSet, InformationViewSet, ReportViewSet,
)

router = DefaultRouter()
router.register(r"quejas",        ComplaintViewSet,       basename="complaint")
router.register(r"evaluaciones",  EvaluationViewSet,      basename="evaluation")
router.register(r"cuartelerias",  CleaningScheduleViewSet,basename="cleaning")
router.register(r"asignaciones",  AssignmentViewSet,      basename="assignment")
router.register(r"informaciones", InformationViewSet,     basename="information")
router.register(r"reportes",      ReportViewSet,          basename="report")

urlpatterns = router.urls
