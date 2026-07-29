"""
audio_utils.py
Handles transcription of uploaded/recorded audio (lecture recordings, voice notes)
using OpenAI's Whisper transcription API.

Supported formats: mp3, mp4, mpeg, mpga, m4a, wav, webm (OpenAI Whisper limits apply,
25MB max file size per request).
"""

from openai import OpenAI
import io


def transcribe_audio(uploaded_file, api_key: str) -> str:
    """
    Transcribes an uploaded audio file to text using Whisper.

    Args:
        uploaded_file: File-like object from st.file_uploader or st.audio_input
        api_key: OpenAI API key

    Returns:
        Transcribed text
    """
    client = OpenAI(api_key=api_key)

    # Whisper API needs a named file-like object
    audio_bytes = uploaded_file.read()
    audio_file = io.BytesIO(audio_bytes)
    audio_file.name = getattr(uploaded_file, "name", "recording.wav")

    transcript = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file,
        response_format="text",
    )

    return transcript if isinstance(transcript, str) else transcript.text


def is_supported_audio_format(filename: str) -> bool:
    supported = {".mp3", ".mp4", ".mpeg", ".mpga", ".m4a", ".wav", ".webm"}
    return any(filename.lower().endswith(ext) for ext in supported)
