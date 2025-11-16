from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from .models import Announcement
from .serializers import AnnouncementSerializer


# ✅ Helper: check if user is admin or staff
def is_admin_or_staff(user):
    profile = getattr(user, "profile", None)
    if profile:
        return profile.role in ["admin", "staff"]
    return False


# -----------------------------
# CREATE ANNOUNCEMENT (admin/staff only)
# -----------------------------
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_announcement(request):
    if not is_admin_or_staff(request.user):
        return Response(
            {"detail": "Forbidden: Only admin or staff can create announcements."},
            status=status.HTTP_403_FORBIDDEN
        )

    serializer = AnnouncementSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# -----------------------------
# LIST ANNOUNCEMENTS (public)
# -----------------------------
@api_view(['GET'])
@permission_classes([AllowAny])
def list_announcements(request):
    announcements = Announcement.objects.all().order_by('-created_at')
    serializer = AnnouncementSerializer(announcements, many=True)
    return Response(serializer.data)


# -----------------------------
# GET SINGLE ANNOUNCEMENT (public)
# -----------------------------
@api_view(['GET'])
@permission_classes([AllowAny])
def get_announcement(request, pk):
    try:
        announcement = Announcement.objects.get(pk=pk)
    except Announcement.DoesNotExist:
        return Response({'detail': 'Announcement not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = AnnouncementSerializer(announcement)
    return Response(serializer.data)


# -----------------------------
# EDIT ANNOUNCEMENT (admin/staff only)
# -----------------------------
@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def edit_announcement(request, pk):
    try:
        announcement = Announcement.objects.get(pk=pk)
    except Announcement.DoesNotExist:
        return Response({'detail': 'Announcement not found'}, status=status.HTTP_404_NOT_FOUND)

    if not is_admin_or_staff(request.user):
        return Response(
            {"detail": "Forbidden: Only admin or staff can edit announcements."},
            status=status.HTTP_403_FORBIDDEN
        )

    serializer = AnnouncementSerializer(announcement, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# -----------------------------
# DELETE ANNOUNCEMENT (admin/staff only)
# -----------------------------
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_announcement(request, pk):
    try:
        announcement = Announcement.objects.get(pk=pk)
    except Announcement.DoesNotExist:
        return Response({'detail': 'Announcement not found'}, status=status.HTTP_404_NOT_FOUND)

    if not is_admin_or_staff(request.user):
        return Response(
            {"detail": "Forbidden: Only admin or staff can delete announcements."},
            status=status.HTTP_403_FORBIDDEN
        )

    announcement.delete()
    return Response({'detail': 'Announcement deleted'}, status=status.HTTP_204_NO_CONTENT)
