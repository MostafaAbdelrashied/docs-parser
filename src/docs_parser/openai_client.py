from typing import Dict, List

from openai import OpenAI

from docs_parser.models import DocumentSummary
from docs_parser.settings import settings


class OpenAIClient:
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai.api_key)

    def call_llm(
        self, ocr_results: List[Dict[str, str]], encoded_images: List[str]
    ) -> DocumentSummary:
        content = [{"type": "text", "text": str(ocr_results)}]

        for base64_image in encoded_images:
            content.append(
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}, # type: ignore
                }
            )

        response = self.client.beta.chat.completions.parse(
            model=settings.openai.model,
            response_format=DocumentSummary,
            messages=[
                {
                    "role": "system",
                    "content": self._system_prompt,
                },
                {"role": "user", "content": content},
            ],
        )

        return response.choices[0].message.parsed

    @property
    def _system_prompt(self) -> str:
        return (
            "# Document Classification Task\n\n"
            "## Objective\n"
            "Analyze the provided document using both the base64-encoded images and OCR text extraction to classify document elements into two categories: 'paragraph' or 'heading' and organize them into a structured DocumentSummary.\n\n"
            "## Required Analysis\n"
            "1. Examine the visual layout and formatting in the images\n"
            "2. Cross-reference with the OCR text extraction provided\n"
            "3. Classify each text block as either a paragraph or heading based on:\n"
            "   - Font size and weight\n"
            "   - Position in document hierarchy\n"
            "   - Content length and structure\n"
            "   - Surrounding whitespace\n\n"
        )
