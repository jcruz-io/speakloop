from uuid import uuid4, UUID

from pydantic import BaseModel, Field


class PracticePreferences(BaseModel):
    """Represents the user's preferences for generating practice content."""

    role: str
    interests: list[str]
    target_length: int


class GeneratedText(BaseModel):
    """Represents a piece of text generated for pronunciation practice."""

    id: UUID = Field(default_factory=uuid4)
    content: str


class CorrectionTip(BaseModel):
    """Represents a single phonetic correction with contextual guidance."""

    original_word: str
    transcribed_word: str
    phonetic_tip: str
    context_tip: str


class EvaluationResult(BaseModel):
    """Represents the full result of a pronunciation evaluation session."""

    transcribed_text: str
    accuracy_score: float | int
    corrections: list[CorrectionTip]
