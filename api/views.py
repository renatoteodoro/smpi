from rest_framework import viewsets, mixins
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.authentication import ApiKeyAuthentication


class SmpiViewSet(viewsets.GenericViewSet):
    """Base ViewSet — requires token or API key auth."""
    authentication_classes = [ApiKeyAuthentication]
    permission_classes = [IsAuthenticated]


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_root(request):
    return Response({'status': 'SMPI API v1', 'version': '1.0.0'})


class EquipmentViewSet(SmpiViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    def get_queryset(self):
        from assets.models import Equipment
        return Equipment.objects.prefetch_related('measurement_points').order_by('name')

    def get_serializer_class(self):
        from assets.serializers import EquipmentSerializer
        return EquipmentSerializer


class FaultViewSet(SmpiViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    def get_queryset(self):
        from faults.models import Fault
        return Fault.objects.all()

    def get_serializer_class(self):
        from faults.serializers import FaultSerializer
        return FaultSerializer


class SensorReadingViewSet(
    SmpiViewSet,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
):
    def get_queryset(self):
        from monitoring.models import SensorReading
        qs = SensorReading.objects.select_related('fault', 'measurement_point__equipment')
        status = self.request.query_params.get('status')
        if status:
            qs = qs.filter(status_class=status)
        return qs

    def get_serializer_class(self):
        from monitoring.serializers import SensorReadingSerializer
        return SensorReadingSerializer

    def perform_create(self, serializer):
        from monitoring.preprocessing import extract_features, normalize_features
        obj = serializer.save()
        try:
            raw = extract_features(obj.metrics or {})
            obj.feature_vector = normalize_features(raw)
            obj.save(update_fields=['feature_vector', 'updated_at'])
            from monitoring.tasks import analyse_reading
            analyse_reading.delay(obj.pk)
        except Exception:
            pass


class PrescriptionViewSet(SmpiViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    def get_queryset(self):
        from prescriptions.models import Prescription
        return Prescription.objects.select_related('fault', 'sensor_reading')

    def get_serializer_class(self):
        from prescriptions.serializers import PrescriptionSerializer
        return PrescriptionSerializer


class KnowledgeDocumentViewSet(SmpiViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    def get_queryset(self):
        from knowledge.models import KnowledgeDocument
        return KnowledgeDocument.objects.select_related('fault')

    def get_serializer_class(self):
        from knowledge.serializers import KnowledgeDocumentSerializer
        return KnowledgeDocumentSerializer
