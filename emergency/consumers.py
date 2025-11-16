from channels.generic.websocket import AsyncJsonWebsocketConsumer

class EmergencyConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        await self.accept()
        await self.channel_layer.group_add("emergencies", self.channel_name)

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("emergencies", self.channel_name)

    # Custom handler for emergency updates
    async def emergency_updated(self, event):
        await self.send_json(event["data"])
