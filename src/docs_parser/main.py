from pathlib import Path

from docs_parser.cli import parse_args
from docs_parser.processor import OCRProcessor


def main() -> None:
    parsed_args = parse_args()
    input_file = Path(parsed_args.input_file)
    if not input_file.exists():
        raise FileNotFoundError
    output_dir = Path(parsed_args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    language = parsed_args.lang
    print(f"Processing {input_file}")
    OCRProcessor(input_file, output_dir,language).process()
    print("Processing complete")


if __name__ == "__main__":
    main()
