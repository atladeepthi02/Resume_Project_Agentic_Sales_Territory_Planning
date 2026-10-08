import os


class LLMService:
    def __init__(self, model: str | None = None):
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    def generate(self, prompt: str, *args, **kwargs) -> str:
        return f"Grounded response generated for model {self.model}."
