from core.domain.models import EvaluationResult, GeneratedText, PracticePreferences
from core.ports.services import PronunciationEvaluatorPort, SpeechToTextPort, TextGeneratorPort


class GeneratePracticeTextUseCase:
    """Orchestrates the generation of an English practice text.

    Depends exclusively on the TextGeneratorPort abstraction; it has no
    knowledge of any concrete provider or transport layer.
    """

    def __init__(self, text_generator: TextGeneratorPort) -> None:
        self._text_generator = text_generator

    async def execute(self, preferences: PracticePreferences) -> GeneratedText:
        """Generate a practice text based on the user's preferences.

        Args:
            preferences: The user's role, interests, and desired text length.

        Returns:
            A GeneratedText instance with a unique ID and the generated content.
        """
        return await self._text_generator.generate_practice_text(preferences)


class EvaluatePronunciationUseCase:
    """Orchestrates the full pronunciation evaluation pipeline.

    Chains SpeechToTextPort and PronunciationEvaluatorPort: first transcribes
    the raw audio, then evaluates the transcription against the original text.
    Has no knowledge of any concrete provider or transport layer.
    """

    def __init__(
        self,
        speech_to_text: SpeechToTextPort,
        pronunciation_evaluator: PronunciationEvaluatorPort,
    ) -> None:
        self._speech_to_text = speech_to_text
        self._pronunciation_evaluator = pronunciation_evaluator

    async def execute(self, audio_bytes: bytes, original_text: str) -> EvaluationResult:
        """Transcribe audio and evaluate its pronunciation quality.

        Args:
            audio_bytes: Raw audio data recorded by the user.
            original_text: The reference text the user was supposed to read.

        Returns:
            An EvaluationResult with an accuracy score and phonetic corrections.
        """
        transcribed_text = await self._speech_to_text.transcribe_audio(audio_bytes)
        return await self._pronunciation_evaluator.evaluate_pronunciation(
            original_text=original_text,
            transcribed_text=transcribed_text,
        )
