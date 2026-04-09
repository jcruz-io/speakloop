import io

from openai import AsyncOpenAI

from core.ports.services import SpeechToTextPort
from infrastructure.config import settings


class OpenAISpeechToText(SpeechToTextPort):
    """SpeechToTextPort implementation backed by OpenAI Whisper.

    Wraps raw audio bytes in an in-memory buffer and submits them to the
    Whisper transcription endpoint. The buffer is named 'audio.webm' so
    the SDK can infer the MIME type; adjust the extension if the client
    sends a different format.
    """

    def __init__(self) -> None:
        self._client = AsyncOpenAI(api_key=settings.openai_api_key)
        self._model = settings.openai_whisper_model

    async def transcribe_audio(self, audio_bytes: bytes) -> str:
        buffer = io.BytesIO(audio_bytes)
        buffer.name = "audio.webm"

        transcription = await self._client.audio.transcriptions.create(
            model=self._model,
            file=buffer,
            response_format="text",
        )

        return transcription.strip() if isinstance(transcription, str) else transcription
