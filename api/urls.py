from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'equipment', views.EquipmentViewSet, basename='equipment')
router.register(r'faults', views.FaultViewSet, basename='fault')
router.register(r'readings', views.SensorReadingViewSet, basename='reading')
router.register(r'prescriptions', views.PrescriptionViewSet, basename='prescription')
router.register(r'knowledge', views.KnowledgeDocumentViewSet, basename='knowledge')

app_name = 'api'
urlpatterns = [
    path('', views.api_root, name='root'),
    path('', include(router.urls)),
]
