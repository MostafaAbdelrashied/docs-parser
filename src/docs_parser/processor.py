import json
import base64
from io import BytesIO
from pathlib import Path
from typing import Dict, List, Optional

import pytesseract # type: ignore
from pdf2image import convert_from_path
from PIL import Image, ImageDraw

from docs_parser.models import DocumentSummary
from docs_parser.openai_client import OpenAIClient


class OCRProcessor:
    def __init__(
        self,
        input_file: Path,
        output_dir: Path,
        lang: str,
    ) -> None:
        self.input_file = Path(input_file)
        self.output_dir = Path(output_dir)
        self.lang = lang

        self.base_name = self.input_file.stem

        self.document_output_dir = self.output_dir / self.base_name.lower()
        self.document_output_dir.mkdir(parents=True, exist_ok=True)

        self.extension = self.input_file.suffix.lower()

        self.openai_client = OpenAIClient()

        self.page_images: Dict[int, Image.Image] = {}

    def process_image(self) -> List[Dict]:
        image = Image.open(self.input_file)
        self.page_images[1] = image.copy()

        data = pytesseract.image_to_data(
            image, lang=self.lang, output_type=pytesseract.Output.DICT
        )

        results = self._extract_text_data(data)

        if results:
            self._create_annotated_image(
                image, results, page_num=1, process_type="ocr", outline_color="red"
            )

        return results

    def process_pdf(self) -> List[Dict]:
        images = convert_from_path(self.input_file, dpi=300)
        all_results: List[Dict] = []

        for page_num, image in enumerate(images, start=1):
            self.page_images[page_num] = image.copy()

            data = pytesseract.image_to_data(
                image, lang=self.lang, output_type=pytesseract.Output.DICT
            )

            page_results = self._extract_text_data(data, all_results, page_num)
            all_results.extend(page_results)

            if page_results:
                self._create_annotated_image(
                    image,
                    page_results,
                    page_num,
                    process_type="ocr",
                    outline_color="red",
                )

        return all_results

    def _extract_text_data(
        self, data: Dict, existing_results: Optional[List] = None, page_num: int = 1
    ) -> List[Dict]:
        results: List[Dict] = []
        start_id = len(existing_results) + 1 if existing_results else 1

        for i in range(len(data["text"])):
            if not data["text"][i].strip():
                continue

            x = data["left"][i]
            y = data["top"][i]
            width = data["width"][i]
            height = data["height"][i]

            result = {
                "id": start_id + len(results),
                "text": data["text"][i],
                "confidence": data["conf"][i],
                "location": {
                    "x": x,
                    "y": y,
                    "width": width,
                    "height": height,
                    "page": page_num,
                },
            }
            results.append(result)

        return results

    def _create_annotated_image(
        self,
        image: Image.Image,
        results: List[Dict],
        page_num: int,
        process_type: str,
        outline_color: str = "red",
    ) -> None:
        annotated_image = image.copy()
        draw = ImageDraw.Draw(annotated_image)

        for result in results:
            location = result.get("location", {})
            x = location.get("x", 0)
            y = location.get("y", 0)
            width = location.get("width", 0)
            height = location.get("height", 0)

            draw.rectangle(
                [x, y, x + width, y + height], outline=outline_color, width=2
            )

        output_path = (
            self.document_output_dir / f"{process_type}_annotated_page_{page_num}.png"
        )
        annotated_image.save(output_path)

    def _create_openai_annotated_images(
        self, document_summary: DocumentSummary
    ) -> None:
        for page in document_summary.pages:
            block_results = [
                {
                    "location": {
                        "x": block.location.x,
                        "y": block.location.y,
                        "width": block.location.width,
                        "height": block.location.height,
                    }
                }
                for block in page.blocks
            ]
            self._create_annotated_image(
                image=self.page_images[page.page_number],
                results=block_results,
                page_num=page.page_number,
                process_type="openai",
                outline_color="blue",
            )

    def _encode_image_to_base64(self, image: Image.Image) -> str:
        buffer = BytesIO()
        image.save(buffer, format=image.format or "PNG")
        return base64.b64encode(buffer.getvalue()).decode("utf-8")

    @property
    def _get_encoded_images(self) -> List[str]:
        return [
            self._encode_image_to_base64(image) for image in self.page_images.values()
        ]

    def _process_ocr(self) -> List[Dict]:
        if self.extension in [".pdf"]:
            return self.process_pdf()
        elif self.extension in [".png", ".jpg", ".jpeg"]:
            return self.process_image()
        else:
            raise ValueError(f"Unsupported file format: {self.extension}")

    def process(self) -> None:
        print("OCR Processing")
        results = self._process_ocr()
        with open(
            self.document_output_dir / "ocr_results.json", "w", encoding="utf-8"
        ) as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print("OpenAI Processing")
        document_summary = self.openai_client.call_llm(
            ocr_results=results, encoded_images=self._get_encoded_images
        )
        with open(
            self.document_output_dir / "openai_results.json", "w", encoding="utf-8"
        ) as f:
            f.write(document_summary.model_dump_json(indent=2))

        self._create_openai_annotated_images(document_summary)
