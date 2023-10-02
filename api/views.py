from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import os
import tempfile
import pika
import openai


video_files = {}

class RabbitMQ:
    """
    Handles connection to RabbitMQL
    """
    def __init__(self):
        self.connection = pika.BlockingConnection(
                pika.ConnectionParameters(host="localhost")
                )
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue="transcriptions")

    def send_to_queue(self, message):
        self.channel.basic_publish(
        exchange="",
        routing_key="transcriptions",
        body=message
        )

    def close_connection(self):
        self.connection.close()


def transcribe_video(video_file):
    """
    Transcribes video to audio
    """
    audio_data = convert_video_to_audio(video_file)

    # send audio data to Whisper API
    whisper_response = openai.Whisper.transcribe(audio_data)

    # process transcripiton result
    transcription = process_whisper_response(whisper_response)

    return transcription


class StartScreenRecording(APIView):
    def post(self, request, format=None):
        """
        Creates video file where chunks will be appended
        """
        video_dir = 'media/videos'

        # create directory if it does not exist
        os.makedirs(video_dir, exist_ok=True)

        try:
            # create a temporary video file
            video_file = tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix='.mp4',
                    dir=video_dir
                    )

            # store file path and file object in a dictionary with a unique key
            video_id = video_file.name
            video_files[video_id] = video_file

            return Response(
                    {'video_id': video_id},
                    status=status.HTTP_201_CREATED
                    )
        except Exception as e:
            return Response(
                    {'message': f'Error: {str(e)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )

class StreamVideo(APIView):
    def post(self, request, video_id, format=None):
        """
        Recieves video in chunks and appends to file
        """
        if video_id not in video_files:
            return Response(
                    {'message': 'Video not found'},
                    status=status.HTTP_404_NOT_FOUND
                    )
        video_file = video_files[video_id]
        chunk = request.data['chunk']

        try:
            # Append chunk to existing video file
            video_file.write(chunk.read())

            # Transcribe video using whisper
            transcription = transcribe_video(video_file.name)

            # Send transcription to RabbitMQ queue
            rabbitmq = RabbitMQ()
            rabbitmq.send_to_queue(transcription)
            rabbitmq.close_connection()

            return Response(
                    {'message': 'Chunk appended successfully'},
                    status=status.HTTP_200_OK
                    )
        except Exception as e:
            return Response(
                    {'message': f'Error: {str(e)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )

class CompleteVideo(APIView):
    def post(self, request, video_id, format=None):
        """
        Once all chunks have been compiled, saves to disk
        """
        if video_id not in video_files:
            return Response(
                    {'message': 'Video not found'},
                    status=status.HTTP_404_NOT_FOUND
                    )

        video_file = video_files[video_id]
        video_file.close()
        del video_files[video_id]

        return Response(
                {'message': 'Video saved to disk'},
                status=status.HTTP_200_OK
                )
