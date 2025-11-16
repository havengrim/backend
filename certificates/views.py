from rest_framework import generics, permissions
from .models import CertificateRequest, BusinessPermit
from .serializers import CertificateRequestSerializer, BusinessPermitSerializer
import logging

logger = logging.getLogger(__name__)

class CertificateRequestListView(generics.ListAPIView):
    serializer_class = CertificateRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            # Check the role from the profile model
            if hasattr(user, 'profile') and user.profile.role == 'admin':
                return CertificateRequest.objects.all()
            else:
                return CertificateRequest.objects.filter(user=user)
        return CertificateRequest.objects.none()

class CertificateRequestCreateView(generics.CreateAPIView):
    serializer_class = CertificateRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class CertificateRequestDetailView(generics.RetrieveAPIView):
    serializer_class = CertificateRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        queryset = CertificateRequest.objects.filter(user=self.request.user)
        logger.debug(f"Detail View - User: {self.request.user}, Queryset: {queryset.values('id', 'request_number')}")
        return queryset

class CertificateRequestUpdateView(generics.UpdateAPIView):
    serializer_class = CertificateRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):

        queryset = CertificateRequest.objects.all()
        logger.debug(f"Authenticated User: {self.request.user}, Full Queryset: {queryset.values('id', 'request_number')}")
        return queryset
    
    def patch(self, request, *args, **kwargs):
        """Allow partial updates (e.g. updating only the status field)."""
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

class CertificateRequestDeleteView(generics.DestroyAPIView):
    serializer_class = CertificateRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        user = self.request.user
        role = getattr(user.profile, "role", None)

        if role == "admin":
            return CertificateRequest.objects.all()
        return CertificateRequest.objects.filter(user=user)


class BusinessPermitListCreateView(generics.ListCreateAPIView):
    serializer_class = BusinessPermitSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        role = getattr(user.profile, "role", None)

        logger.debug(f"[BusinessPermitListCreateView] User: {user.username} | Role: {role}")

        # Admins and staff get all permits
        if role in ["admin", "staff"]:
            return BusinessPermit.objects.all()

        # Normal users only get their own
        return BusinessPermit.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class BusinessPermitRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = BusinessPermitSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'pk'

    def get_queryset(self):
        user = self.request.user
        role = getattr(user.profile, "role", None)

        logger.debug(f"[BusinessPermitRetrieveUpdateDestroyView] User: {user.username} | Role: {role}")

        if role in ["admin", "staff"]:
            return BusinessPermit.objects.all()

        return BusinessPermit.objects.filter(user=user)
