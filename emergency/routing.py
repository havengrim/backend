from django.urls import re_path
from .consumers import EmergencyConsumer

websocket_urlpatterns = [
    re_path(r"ws/emergencies/$", EmergencyConsumer.as_asgi()),
]
