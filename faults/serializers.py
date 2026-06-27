from rest_framework import serializers

from .models import Fault


class FaultSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fault
        fields = '__all__'
        read_only_fields = ('is_problem',)
