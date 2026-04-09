from openai import AsyncOpenAI

from core.domain.models import GeneratedText, PracticePreferences
from core.ports.services import TextGeneratorPort
from infrastructure.config import settings


class OpenAITextGenerator(TextGeneratorPort):
    """TextGeneratorPort implementation backed by OpenAI Chat Completions.

    Uses the model defined in settings (default: gpt-4o-mini) to produce
    contextually relevant English practice texts based on the user's
    professional role and areas of interest.
    """

    def __init__(self) -> None:
        self._client = AsyncOpenAI(api_key=settings.openai_api_key)
        self._model = settings.openai_model

    async def generate_practice_text(self, preferences: PracticePreferences) -> GeneratedText:
        interests_str = ", ".join(preferences.interests)
        prompt = (
            f"You are an English language coach specializing in professional communication.\n"
            f"Generate a single, cohesive English paragraph of approximately "
            f"{preferences.target_length} words for a {preferences.role} "
            f"who wants to practice pronunciation in these areas: {interests_str}.\n"
            f"The text must use vocabulary and concepts relevant to the user's field.\n"
            f"Output only the paragraph, no titles or extra commentary."
        )

        response = await self._client.chat.completions.create(
            model=self._model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )

        content = response.choices[0].message.content or ""
        return GeneratedText(content=content.strip())
