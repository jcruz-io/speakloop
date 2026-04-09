from core.application.use_cases import EvaluatePronunciationUseCase, GeneratePracticeTextUseCase
from infrastructure.adapters.mock_services import (
    MockPronunciationEvaluator,
    MockSpeechToText,
    MockTextGenerator,
)
from infrastructure.adapters.openai_pronunciation_evaluator import OpenAIPronunciationEvaluator
from infrastructure.adapters.openai_speech_to_text import OpenAISpeechToText
from infrastructure.adapters.openai_text_generator import OpenAITextGenerator
from infrastructure.config import settings


def get_generate_practice_text_use_case() -> GeneratePracticeTextUseCase:
    text_generator = MockTextGenerator() if settings.use_mocks else OpenAITextGenerator()
    return GeneratePracticeTextUseCase(text_generator=text_generator)


def get_evaluate_pronunciation_use_case() -> EvaluatePronunciationUseCase:
    if settings.use_mocks:
        stt = MockSpeechToText()
        evaluator = MockPronunciationEvaluator()
    else:
        stt = OpenAISpeechToText()
        evaluator = OpenAIPronunciationEvaluator()
    return EvaluatePronunciationUseCase(speech_to_text=stt, pronunciation_evaluator=evaluator)
