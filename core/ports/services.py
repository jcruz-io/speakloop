from abc import ABC, abstractmethod

from core.domain.models import EvaluationResult, GeneratedText, PracticePreferences


class TextGeneratorPort(ABC):
    """Port that defines the contract for any text generation provider.

    Implementations must generate contextually relevant English practice
    texts based on the user's professional role and areas of interest.
    """

    @abstractmethod
    async def generate_practice_text(
        self, preferences: PracticePreferences
    ) -> GeneratedText:
        """Generate an English practice text tailored to the given preferences.

        Args:
            preferences: The user's role, interests, and desired text length.

        Returns:
            A GeneratedText instance containing a unique ID and the content.
        """
        ...


class SpeechToTextPort(ABC):
    """Port that defines the contract for any speech-to-text provider.

    Implementations are responsible for converting raw audio bytes into
    a plain-text transcription string.
    """

    @abstractmethod
    async def transcribe_audio(self, audio_bytes: bytes) -> str:
        """Transcribe raw audio bytes into a plain-text string.

        Args:
            audio_bytes: The raw audio data to be transcribed.

        Returns:
            The transcribed text as a plain string.
        """
        ...


class PronunciationEvaluatorPort(ABC):
    """Port that defines the contract for any pronunciation evaluation provider.

    Implementations must compare the original text against the user's
    transcription and produce phonetic corrections adapted for Spanish speakers.
    """

    @abstractmethod
    async def evaluate_pronunciation(
        self, original_text: str, transcribed_text: str
    ) -> EvaluationResult:
        """Evaluate the pronunciation quality by comparing two texts.

        Args:
            original_text: The reference text the user was supposed to read.
            transcribed_text: The text obtained from the user's audio recording.

        Returns:
            An EvaluationResult with an accuracy score and a list of
            phonetic correction tips tailored for Spanish speakers.
        """
        ...
