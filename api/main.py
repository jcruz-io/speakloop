from fastapi import Depends, FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from core.application.use_cases import EvaluatePronunciationUseCase, GeneratePracticeTextUseCase
from core.domain.models import EvaluationResult, GeneratedText, PracticePreferences
from infrastructure.adapters.mock_services import (
    MockPronunciationEvaluator,
    MockSpeechToText,
    MockTextGenerator,
)

app = FastAPI(title="SpeakLoop API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_generate_practice_text_use_case() -> GeneratePracticeTextUseCase:
    return GeneratePracticeTextUseCase(text_generator=MockTextGenerator())


def get_evaluate_pronunciation_use_case() -> EvaluatePronunciationUseCase:
    return EvaluatePronunciationUseCase(
        speech_to_text=MockSpeechToText(),
        pronunciation_evaluator=MockPronunciationEvaluator(),
    )


@app.post("/api/v1/practice-texts", response_model=GeneratedText)
async def generate_practice_text(
    preferences: PracticePreferences,
    use_case: GeneratePracticeTextUseCase = Depends(get_generate_practice_text_use_case),
) -> GeneratedText:
    return await use_case.execute(preferences)


@app.post("/api/v1/evaluations", response_model=EvaluationResult)
async def evaluate_pronunciation(
    original_text: str = Form(...),
    audio_file: UploadFile = File(...),
    use_case: EvaluatePronunciationUseCase = Depends(get_evaluate_pronunciation_use_case),
) -> EvaluationResult:
    audio_bytes = await audio_file.read()
    return await use_case.execute(audio_bytes=audio_bytes, original_text=original_text)
