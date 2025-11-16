from rest_framework import serializers
from .models import BlotterReport

class BlotterReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlotterReport
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        partial = self.context.get('partial', False)  # check partial in context
        if partial:
            for field in self.fields.values():
                field.required = False
