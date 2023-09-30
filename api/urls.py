from .views import StartScreenRecording, StreamVideo, CompleteVideo
from django.urls import path


urlpatterns = [
        path(
            'start_screen_recording/',
            StartScreenRecording.as_view(),
            name='start_screen_recording'
            ),
        path(
            'stream_video/<str:video_id>/',
            StreamVideo.as_view(),
            name='stream_video'
            ),
        path(
            'complete_video/<str:video_id>/',
            CompleteVideo.as_view(),
            name='complete_video'
            )
        ]
