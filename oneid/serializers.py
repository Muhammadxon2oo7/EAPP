from rest_framework import serializers


class CodeSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=255, required=True, allow_blank=False, write_only=True)
