import asyncio

from core.domain.models import CorrectionTip, EvaluationResult, GeneratedText, PracticePreferences
from core.ports.services import PronunciationEvaluatorPort, SpeechToTextPort, TextGeneratorPort

_MOCK_TEXT = (
    "In modern software development, building scalable and maintainable systems "
    "requires a deep understanding of design patterns and architectural principles. "
    "Microservices allow teams to deploy independent components, improving fault "
    "tolerance and enabling continuous delivery pipelines."
)

_MOCK_TRANSCRIPTION = (
    "In modern software development, building callable and maintainable systems "
    "requires a deep understanding of design patterns and architectural principles. "
    "Microservices allow teams to deploy independent components, improving fault "
    "tolerance and enabling continuous delivery pipelines."
)


class MockTextGenerator(TextGeneratorPort):
    """Mock implementation of TextGeneratorPort.

    Returns a static English technology-themed practice text without
    calling any external API. Simulates network latency via asyncio.sleep.
    """

    async def generate_practice_text(self, preferences: PracticePreferences) -> GeneratedText:
        await asyncio.sleep(1)
        return GeneratedText(content=_MOCK_TEXT)


class MockSpeechToText(SpeechToTextPort):
    """Mock implementation of SpeechToTextPort.

    Ignores the provided audio bytes and returns a predefined transcription
    string that contains intentional errors for evaluation testing purposes.
    """

    async def transcribe_audio(self, audio_bytes: bytes) -> str:
        await asyncio.sleep(1)
        return _MOCK_TRANSCRIPTION


class MockPronunciationEvaluator(PronunciationEvaluatorPort):
    """Mock implementation of PronunciationEvaluatorPort.

    Returns a static EvaluationResult with a hardcoded accuracy score and
    two CorrectionTip entries adapted for Spanish-speaking learners.
    """

    async def evaluate_pronunciation(
        self, original_text: str, transcribed_text: str
    ) -> EvaluationResult:
        await asyncio.sleep(1)
        corrections = [
            CorrectionTip(
                original_word="scalable",
                transcribed_word="callable",
                phonetic_tip=(
                    "Pronuncia 'scalable' como /ˈskeɪ.lə.bəl/. "
                    "La 'sc' inicial suena como 'sk', no como 'k' sola. "
                    "El acento recae en la primera sílaba: SKEI-la-bul."
                ),
                context_tip=(
                    "'Scalable' describe sistemas que pueden crecer en capacidad. "
                    "No confundir con 'callable', que en Python se refiere a "
                    "objetos que pueden ser invocados como funciones."
                ),
            ),
            CorrectionTip(
                original_word="architectural",
                transcribed_word="arquitectural",
                phonetic_tip=(
                    "Pronuncia 'architectural' como /ˌɑːr.kɪˈtek.tʃər.əl/. "
                    "Evita el calco del español 'arquitectural'. "
                    "El acento fuerte va en la tercera sílaba: ar-ki-TEK-cher-al."
                ),
                context_tip=(
                    "En inglés técnico este adjetivo acompaña frecuentemente a "
                    "'principles', 'patterns' y 'decisions'. "
                    "Practicar la secuencia '-tectural' de forma aislada ayuda a "
                    "automatizar su pronunciación."
                ),
            ),
        ]
        return EvaluationResult(
            transcribed_text=transcribed_text,
            accuracy_score=85.0,
            corrections=corrections,
        )
