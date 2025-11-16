from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from datetime import date
import logging

logger = logging.getLogger(__name__)

# --------------------------
# Register Serializer
# --------------------------
class RegisterSerializer(serializers.ModelSerializer):
    name = serializers.CharField(write_only=True)
    contact_number = serializers.CharField(write_only=True)
    address = serializers.CharField(write_only=True)
    houseNum = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    civil_status = serializers.CharField(write_only=True)
    birthdate = serializers.DateField(write_only=True)
    role = serializers.CharField(write_only=True, required=False, default='user')
    image = serializers.FileField(write_only=True, required=False, allow_null=True)  # Updated
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            'name',
            'username',
            'email',
            'password',
            'confirm_password',
            'contact_number',
            'houseNum',
            'address',
            'civil_status',
            'birthdate',
            'role',
            'image',
        )

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Password fields didn't match."})
        validate_password(attrs['password'])
        return attrs

    def create(self, validated_data):
        contact_number = validated_data.pop('contact_number')
        address = validated_data.pop('address')
        houseNum = validated_data.pop('houseNum', None)
        civil_status = validated_data.pop('civil_status')
        birthdate = validated_data.pop('birthdate')
        role = validated_data.pop('role', 'user')
        image = validated_data.pop('image', None)
        validated_data.pop('confirm_password')
        name = validated_data.pop('name')

        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )

        Profile.objects.create(
            user=user,
            name=name,
            contact_number=contact_number,
            address=address,
            houseNum=houseNum,
            civil_status=civil_status,
            birthdate=birthdate,
            role=role,
            image=image
        )

        return user

# --------------------------
# Profile Serializer
# --------------------------
class ProfileSerializer(serializers.ModelSerializer):
    image = serializers.FileField(required=False, allow_null=True)  # Updated

    class Meta:
        model = Profile
        fields = [
            'name',
            'contact_number',
            'address',
            'houseNum',
            'civil_status',
            'birthdate',
            'role',
            'image',
        ]

# --------------------------
# User Serializer
# --------------------------
class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'profile']

    def to_internal_value(self, data):
        # Handle flat dotted keys (e.g., "profile.name") and convert to nested
        nested_data = {}
        profile_data = {}

        for key, value in data.items():
            if key.startswith('profile.'):
                profile_key = key.split('.', 1)[1]
                profile_data[profile_key] = value
            else:
                nested_data[key] = value

        if profile_data:
            nested_data['profile'] = profile_data

        return super().to_internal_value(nested_data)

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', {})
        profile, created = Profile.objects.get_or_create(user=instance)

        # Update user fields
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        instance.save()

        # Update profile fields
        profile.name = profile_data.get('name', profile.name or instance.username)
        profile.contact_number = profile_data.get('contact_number', profile.contact_number or '')
        profile.address = profile_data.get('address', profile.address or '')
        profile.houseNum = profile_data.get('houseNum', profile.houseNum or 0)
        profile.civil_status = profile_data.get('civil_status', profile.civil_status or 'single')
        profile.birthdate = profile_data.get('birthdate', profile.birthdate or date(1900, 1, 1))
        profile.role = profile_data.get('role', profile.role or 'user')

        # Store file or None
        image = profile_data.get('image', None)
        if image is not None:
            logger.info(f"Starting image upload for user {instance.id}: {getattr(image, 'name', 'Unknown')}")
            profile.image = image

        try:
            profile.save()
            logger.info(f"Profile {profile.id} saved successfully for user {instance.id}. File: {profile.image.name if profile.image else 'None'}")
        except Exception as e:
            logger.error(f"Profile save failed for user {instance.id}: {str(e)}", exc_info=True)
            raise serializers.ValidationError({"detail": f"Failed to save profile: {str(e)}"})

        return instance

# --------------------------
# Custom Token Serializer
# --------------------------
class CustomTokenObtainPairSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        users = User.objects.filter(email=email)

        if not users.exists():
            raise serializers.ValidationError({"email": "No user found with this email."})

        if users.count() > 1:
            raise serializers.ValidationError(
                {"email": "Multiple accounts use this email. Please use username instead."}
            )

        user = users.first()
        user = authenticate(username=user.username, password=password)
        if not user:
            raise serializers.ValidationError({"password": "Incorrect password."})

        refresh = TokenObtainPairSerializer.get_token(user)
        profile = getattr(user, "profile", None)

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "profile": {
                    "name": profile.name if profile else None,
                    "contact_number": profile.contact_number if profile else None,
                    "address": profile.address if profile else None,
                    "houseNum": profile.houseNum if profile else None,
                    "civil_status": profile.civil_status if profile else None,
                    "birthdate": profile.birthdate if profile else None,
                    "role": profile.role if profile else None,
                    "image": profile.image.name if profile and profile.image else None,
                } if profile else None,
            },
        }
