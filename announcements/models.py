from django.db import models
from emergency.storages import SupabaseStorage

supabase_storage = SupabaseStorage()

class Announcement(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=50)
    start_date = models.DateField()
    end_date = models.DateField()
    location = models.CharField(max_length=255)
    target_audience = models.CharField(max_length=255)
    image = models.FileField(
    storage=supabase_storage,
    upload_to='announcements/',
    null=True, blank=True
)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
