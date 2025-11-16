from rest_framework import serializers
from .models import EmergencyAlert, EmergencyReport

class EmergencyReportSerializer(serializers.ModelSerializer):
    media_file = serializers.FileField(required=False, allow_null=True)
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()

    class Meta:
        model = EmergencyReport
        fields = '__all__'

    def create(self, validated_data):
        # If location_text is not a model field, pop it
        validated_data.pop('location_text', None)

        # Optional: ensure lat/lon are floats
        validated_data['latitude'] = float(validated_data.get('latitude', 0.0))
        validated_data['longitude'] = float(validated_data.get('longitude', 0.0))

        # Create instance
        instance = EmergencyReport.objects.create(**validated_data)

        # Optional: compute location_text if it's a model field
        if hasattr(instance, 'location_text'):
            instance.location_text = f"Location ({instance.latitude}, {instance.longitude})"
            instance.save(update_fields=['location_text'])

        return instance

# EmergencyReportPublicSerializer remains unchanged...
class EmergencyReportPublicSerializer(serializers.ModelSerializer):
    alert_message = serializers.SerializerMethodField()
    media_url = serializers.SerializerMethodField()

    INCIDENT_ALERTS = {
        "medical": "Medical emergency reported. Seek help immediately.",
        "security": "Security incident reported. Stay alert and safe.",
        "fire": "Fire reported. Evacuate if necessary.",
        "flood": "Flood reported. Move to higher ground.",
        "earthquake": "Earthquake reported. Follow safety procedures.",
        "other": "Emergency reported. Stay alert.",
    }

    class Meta:
        model = EmergencyReport
        fields = [
            'id',
            'incident_type',
            'location_text',
            'name',
            'status',
            'submitted_at',
            'alert_message',
            'media_file',
            'media_url',
        ]

    def get_alert_message(self, obj):
        return self.INCIDENT_ALERTS.get(obj.incident_type.lower(), "Emergency reported. Stay alert.")

    def get_media_url(self, obj):
        request = self.context.get('request')
        if obj.media_file:
            return request.build_absolute_uri(obj.media_file.url) if request else obj.media_file.url
        return None