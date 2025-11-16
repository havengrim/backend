from rest_framework import viewsets, permissions
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from .models import EmergencyReport
from .serializers import EmergencyReportSerializer, EmergencyReportPublicSerializer

class EmergencyReportViewSet(viewsets.ModelViewSet):
    queryset = EmergencyReport.objects.all().order_by('-submitted_at')
    parser_classes = [MultiPartParser, FormParser, JSONParser]  # ✅ Use list instead of tuple

    def get_permissions(self):
        if self.action in ['create', 'list']:
            return [permissions.AllowAny()]  # ✅ Allow listing for public if needed
        return [permissions.IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == "create":
            return EmergencyReportSerializer  # ✅ Always use full serializer for POST
        if self.request.user.is_authenticated:
            return EmergencyReportSerializer
        return EmergencyReportPublicSerializer  # ✅ Public view for GET (unauthenticated)

    def get_queryset(self):
        if self.action == 'create':
            return EmergencyReport.objects.all()  # ✅ Allow create even if unauthenticated
        if not self.request.user.is_authenticated:
            return EmergencyReport.objects.none()
        return super().get_queryset()
