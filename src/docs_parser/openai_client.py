from pathlib import Path

from openai import OpenAI

from docs_parser.models import DocumentSummary
from docs_parser.settings import settings


class OpenAIClient:
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai.api_key)

    def generate_summary(self, text: str) -> str:
        response = self.client.beta.chat.completions.parse(
            model=settings.openai.model,
            response_format=DocumentSummary,
            messages=[
                {
                    "role": "system",
                    "content": "You are a document analysis assistant. Provide a concise, focused summary of the text in a JSON object with a single field 'summary'.",
                },
                {
                    "role": "user",
                    "content": f"Provide a concise summary (1-2 sentences at most) of this text: {text}",
                },
            ],
        )

        return response.choices[0].message.parsed

    def save_results(self, document: DocumentSummary, output_path: Path) -> None:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(document.model_dump_json(indent=2))
