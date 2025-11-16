from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from .serializer import RegisterSerializer, UserSerializer, CustomTokenObtainPairSerializer
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import MultiPartParser, FormParser
from datetime import timedelta
from django.conf import settings

# ✅ Helper function to check roles
def is_admin_or_staff(user):
    # if you’re using a related profile with role, adjust to user.profile.role
    role = getattr(user, "profile", None)
    if role:
        return role.role in ["admin", "staff"]
    return False


# -----------------------------
# REGISTER (public)
# -----------------------------
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "User created successfully"}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# -----------------------------
# GET ALL USERS (admin/staff only)
# -----------------------------
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_users(request):
    if not is_admin_or_staff(request.user):
        return Response(
            {"detail": "Forbidden: Only admin or staff can access this endpoint."},
            status=status.HTTP_403_FORBIDDEN
        )

    users = User.objects.all()
    serializer = UserSerializer(users, many=True, context={'request': request})
    return Response(serializer.data)


# -----------------------------
# CURRENT LOGGED-IN USER (/current-user/)
# -----------------------------
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
    user = request.user
    profile = getattr(user, 'profile', None)

    if profile is None:
        profile_data = {
            "name": "",
            "contact_number": "",
            "address": "",
            "civil_status": "",
            "birthdate": None,
            "role": "",
            "image": None,
        }
    else:
        profile_data = {
            "name": profile.name,
            "contact_number": profile.contact_number,
            "address": profile.address,
            "civil_status": profile.civil_status,
            "birthdate": profile.birthdate,
            "role": profile.role,
            "image": profile.image.url if profile.image else None,
        }

    data = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "profile": profile_data,
    }
    return Response(data)


# -----------------------------
# USER DETAIL (self or admin/staff only)
# -----------------------------
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def user_detail(request, user_id):
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    # ✅ Access control: only owner or admin/staff can access
    if request.user.id != user.id and not is_admin_or_staff(request.user):
        return Response(
            {"detail": "Forbidden: You can only access your own account or be an admin/staff."},
            status=status.HTTP_403_FORBIDDEN
        )

    # ----- GET -----
    if request.method == 'GET':
        serializer = UserSerializer(user, context={'request': request})
        return Response(serializer.data)

    # ----- PUT -----
    elif request.method == 'PUT':
        serializer = UserSerializer(user, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            # Ensure user has a profile before update
            if not hasattr(user, 'profile'):
                from accounts.models import Profile
                Profile.objects.create(
                    user=user,
                    name=user.username,
                    contact_number='',
                    address='',
                    civil_status='',
                    birthdate='1900-01-01',
                    role='user',
                )
                user.refresh_from_db()
            serializer.save()
            return Response({"message": "User updated successfully", "user": serializer.data})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # ----- DELETE -----
    elif request.method == 'DELETE':
        user.delete()
        return Response({"message": "User deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


# -----------------------------
# LOGIN (with HttpOnly cookies)
# -----------------------------
class CustomEmailLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = CustomTokenObtainPairSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            secure_cookie = not settings.DEBUG  # Only True in production

            response = Response({
                "message": "Login successful",
                "access": data["access"],
                "user": data["user"]
            }, status=status.HTTP_200_OK)

            access_lifetime = settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds()
            refresh_lifetime = settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds()

            response.set_cookie(
                key='access_token',
                value=data["access"],
                httponly=True,
                secure=secure_cookie,
                samesite='Lax',
                max_age=access_lifetime,
                path='/',
            )
            response.set_cookie(
                key='refresh_token',
                value=data["refresh"],
                httponly=True,
                secure=secure_cookie,
                samesite='Lax',
                max_age=refresh_lifetime,
                path='/',
            )
            return response

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# -----------------------------
# TOKEN REFRESH
# -----------------------------
class TokenRefreshView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.COOKIES.get('refresh_token')

        if not refresh_token:
            return Response({"refresh": ["This field is required."]}, status=status.HTTP_400_BAD_REQUEST)

        try:
            refresh = RefreshToken(refresh_token)
            new_access_token = str(refresh.access_token)
            new_refresh_token = str(refresh)

            secure_cookie = not settings.DEBUG

            response = Response({
                "access": new_access_token,
                "message": "Token refreshed"
            }, status=status.HTTP_200_OK)

            access_lifetime = settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds()
            refresh_lifetime = settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds()

            response.set_cookie(
                key='access_token',
                value=new_access_token,
                httponly=True,
                secure=secure_cookie,
                samesite='Lax',
                max_age=access_lifetime,
                path='/',
            )
            response.set_cookie(
                key='refresh_token',
                value=new_refresh_token,
                httponly=True,
                secure=secure_cookie,
                samesite='Lax',
                max_age=refresh_lifetime,
                path='/',
            )
            return response

        except TokenError:
            return Response({"detail": "Invalid refresh token"}, status=status.HTTP_401_UNAUTHORIZED)


# -----------------------------
# LOGOUT
# -----------------------------
@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    refresh_token = request.COOKIES.get('refresh_token')
    if refresh_token:
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception:
            pass

    response = Response({"message": "Successfully logged out"}, status=status.HTTP_205_RESET_CONTENT)
    response.delete_cookie('access_token', path='/')
    response.delete_cookie('refresh_token', path='/')
    return response
