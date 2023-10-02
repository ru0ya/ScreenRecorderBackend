from django.db import models


class Video(model.Model):
    video_id = models.IntegerField()
    chunk = models.FileField(upload_to='media/videos')
