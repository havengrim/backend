from rest_framework import viewsets, permissions
from rest_framework.response import Response
from .models import BlotterReport
from .serializers import BlotterReportSerializer


class BlotterReportViewSet(viewsets.ModelViewSet):
    serializer_class = BlotterReportSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        role = getattr(user.profile, 'role', None)  # safely get role from profile

        # ✅ Admin and staff can see all blotter reports
        if role in ['admin', 'staff']:
            return BlotterReport.objects.all().order_by('-created_at')

        # ✅ Residents can only see their own
        if role == 'resident':
            return BlotterReport.objects.filter(filed_by=user).order_by('-created_at')

        # Default: return empty queryset if role undefined
        return BlotterReport.objects.none()

    def perform_create(self, serializer):
        serializer.save(filed_by=self.request.user)

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, self.OwnershipPermission]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    class OwnershipPermission(permissions.BasePermission):
        def has_object_permission(self, request, _view, obj):
            user = request.user
            role = getattr(user.profile, 'role', None)
            # ✅ Allow if owner, or admin/staff
            return obj.filed_by == user or role in ['admin', 'staff']

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)
