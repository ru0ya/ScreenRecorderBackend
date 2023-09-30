from django.contrib.auth.models import Video
from rest_framework import serializers


class VideoSerializer(serializers.Serializer):
    video_id = serializers.IntegerField()
    chunk = serializers.FileField()

    class Meta:
        model = Video
        fields = ['video_id', 'chunk']
