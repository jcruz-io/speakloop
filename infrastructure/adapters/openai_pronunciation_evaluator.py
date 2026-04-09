import json

from openai import AsyncOpenAI

from core.domain.models import CorrectionTip, EvaluationResult
from core.ports.services import PronunciationEvaluatorPort
from infrastructure.config import settings

_SYSTEM_PROMPT = """\
You are an English pronunciation coach specializing in Spanish-speaking learners.
You will receive two texts: the ORIGINAL (what the user was supposed to read) and the \
TRANSCRIPTION (what the user actually said).
Your tasks are:
1. Compute an accuracy_score between 0.0 and 100.0 that reflects how closely the \
user's pronunciation matched the original text.
2. Identify mispronounced words and produce clear phonetic tips in Spanish, \
tailored to common mistakes made by Spanish speakers.

Respond ONLY with a valid JSON object following the structure below, with no extra text:
{
  "accuracy_score": <float>,
  "corrections": [
    {
      "original_word": "<word from the original text>",
      "transcribed_word": "<how the user pronounced it>",
      "phonetic_tip": "<phonetic explanation in Spanish with IPA transcription>",
      "context_tip": "<contextual tip in Spanish to help remember the correct pronunciation>"
    }
  ]
}
If there are no errors, return an empty list for "corrections".\
"""


class OpenAIPronunciationEvaluator(PronunciationEvaluatorPort):
    """PronunciationEvaluatorPort implementation backed by OpenAI Chat Completions.

    Compares the original reference text against the Whisper transcription
    and returns structured phonetic corrections tailored for Spanish speakers.
    Uses JSON mode to guarantee a parseable response.
    """

    def __init__(self) -> None:
        self._client = AsyncOpenAI(api_key=settings.openai_api_key)
        self._model = settings.openai_model

    async def evaluate_pronunciation(
        self, original_text: str, transcribed_text: str
    ) -> EvaluationResult:
        user_message = (
            f"ORIGINAL TEXT:\n{original_text}\n\n"
            f"USER TRANSCRIPTION:\n{transcribed_text}"
        )

        response = await self._client.chat.completions.create(
            model=self._model,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
            temperature=0.3,
        )

        raw = response.choices[0].message.content or "{}"
        data = json.loads(raw)

        corrections = [CorrectionTip(**item) for item in data.get("corrections", [])]
        return EvaluationResult(
            transcribed_text=transcribed_text,
            accuracy_score=float(data.get("accuracy_score", 0.0)),
            corrections=corrections,
        )
