import argparse


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Doc Parser CLI")

    parser.add_argument("--input-file", help="Path to the input image or PDF file")
    parser.add_argument(
        "--output-dir", default="data/output", help="Directory to save results"
    )
    parser.add_argument("--lang", default="eng", help="OCR language")
    args, _ = parser.parse_known_args()

    return args
