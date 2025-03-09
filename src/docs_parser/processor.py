import json
from pathlib import Path
from typing import Dict, List, Optional

import pytesseract
from pdf2image import convert_from_path
from PIL import Image, ImageDraw


class OCRProcessor:
    def __init__(
        self,
        input_file: Path,
        output_dir: Path,
        lang: str,
    ) -> None:
        # Ensure paths are Path objects
        self.input_file = Path(input_file)
        self.output_dir = Path(output_dir)
        self.lang = lang

        # Extract base name without extension
        self.base_name = self.input_file.stem

        # Create output directory structure: output_dir/base_name/
        self.document_output_dir = self.output_dir / self.base_name.lower()
        self.document_output_dir.mkdir(parents=True, exist_ok=True)

        # Store file extension
        self.extension = self.input_file.suffix.lower()

    def process_image(self) -> List[Dict]:
        """Process a single image file."""
        image = Image.open(self.input_file)
        data = pytesseract.image_to_data(
            image, lang=self.lang, output_type=pytesseract.Output.DICT
        )

        results = self._extract_text_data(data)

        if results:
            self._create_annotated_image(image, results, page_num=1)

        return results

    def process_pdf(self) -> List[Dict]:
        """Process a PDF file by converting to images and applying OCR."""
        images = convert_from_path(self.input_file, dpi=300)
        all_results: List[Dict] = []

        for page_num, image in enumerate(images, start=1):
            data = pytesseract.image_to_data(
                image, lang=self.lang, output_type=pytesseract.Output.DICT
            )

            # Extract data with page number
            page_results = self._extract_text_data(data, all_results, page_num)
            all_results.extend(page_results)

            # Create and save annotated image
            if page_results:
                self._create_annotated_image(image, page_results, page_num)

        return all_results

    def _extract_text_data(
        self, data: Dict, existing_results: Optional[List] = None, page_num: int = 1
    ) -> List[Dict]:
        """Extract text and location data from OCR results."""
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
    ) -> None:
        """Create an annotated image with bounding boxes and IDs."""
        annotated_image = image.copy()
        draw = ImageDraw.Draw(annotated_image)

        # Draw bounding boxes and IDs
        for result in results:
            x = result["location"]["x"]
            y = result["location"]["y"]
            width = result["location"]["width"]
            height = result["location"]["height"]

            # Draw rectangle around text
            draw.rectangle([x, y, x + width, y + height], outline="red", width=2)

        output_path = self.document_output_dir / f"annotated_page_{page_num}.png"

        annotated_image.save(output_path)
        print(f"Saved annotated image to {output_path}")

    def _save_results(self, results: List[Dict]) -> None:
        """Save OCR results to JSON file."""
        output_path = self.document_output_dir / f"{self.base_name}_ocr.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(f"Results saved to {output_path}")

    def _process_file(self) -> List[Dict]:
        """Process the input file based on its extension."""
        if self.extension in [".pdf"]:
            return self.process_pdf()
        elif self.extension in [".png", ".jpg", ".jpeg"]:
            return self.process_image()
        else:
            raise ValueError(f"Unsupported file format: {self.extension}")

    def process(self) -> None:
        """Main processing method."""
        results = self._process_file()
        self._save_results(results)
