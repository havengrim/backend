from rest_framework import serializers
from .models import Complaint

class ComplaintSerializer(serializers.ModelSerializer):
    evidence = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()

    class Meta:
        model = Complaint
        fields = [
            'id', 'reference_number', 'type', 'fullname', 'contact_number', 'address',
            'email_address', 'subject', 'detailed_description', 'respondent_name',
            'respondent_address', 'latitude', 'longitude', 'date_filed', 'status',
            'priority', 'evidence', 'location'
        ]
        read_only_fields = ['id', 'reference_number', 'date_filed', 'user']
        extra_kwargs = {
            'type': {'required': False, 'allow_blank': True},
            'fullname': {'required': False, 'allow_blank': True},
            'contact_number': {'required': False, 'allow_blank': True},
            'address': {'required': False, 'allow_blank': True},
            'email_address': {'required': False, 'allow_blank': True},
            'subject': {'required': False, 'allow_blank': True},
            'detailed_description': {'required': False, 'allow_blank': True},
            'respondent_name': {'required': False, 'allow_blank': True},
            'respondent_address': {'required': False, 'allow_blank': True},
            'latitude': {'required': False, 'allow_null': True},
            'longitude': {'required': False, 'allow_null': True},
            'status': {'required': False, 'allow_blank': True},
            'priority': {'required': False, 'allow_blank': True},
        }

    def get_evidence(self, obj):
        request = self.context.get('request')
        if obj.evidence and hasattr(obj.evidence, 'url'):
            return {'file_url': request.build_absolute_uri(obj.evidence.url)}
        return None

    def get_location(self, obj):
        return {'lat': float(obj.latitude) if obj.latitude is not None else None, 'lng': float(obj.longitude) if obj.longitude is not None else None}

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user if request and request.user.is_authenticated else None
        if not user:
            raise serializers.ValidationError("User must be authenticated to file a complaint.")

        location = validated_data.pop('location', None)
        if location:
            validated_data['latitude'] = location.get('lat')
            validated_data['longitude'] = location.get('lng')

        validated_data.pop('user', None)
        evidence_file = request.FILES.get('evidence')
        complaint = Complaint.objects.create(user=user, **validated_data)

        if evidence_file:
            complaint.evidence = evidence_file
            complaint.save(update_fields=['evidence'])

        return complaint