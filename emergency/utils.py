from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

def notify_emergency_update(emergency_instance):
    channel_layer = get_channel_layer()
    data = {
        "id": str(emergency_instance.id),
        "name": emergency_instance.name,
        "incident_type": emergency_instance.incident_type,
        "status": emergency_instance.status,
        "location_text": emergency_instance.location_text,
        "latitude": emergency_instance.latitude,
        "longitude": emergency_instance.longitude,
        "submitted_at": emergency_instance.submitted_at.isoformat(),
        # add other fields you want to send
    }
    async_to_sync(channel_layer.group_send)(
        "emergencies",
        {
            "type": "emergency.updated",
            "data": data,
        }
    )
