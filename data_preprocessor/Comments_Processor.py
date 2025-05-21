import re
import csv
from bs4 import BeautifulSoup
from langdetect import detect, DetectorFactory

# Ensure reproducibility in langdetect
DetectorFactory.seed = 0

class CommentsProcessor:
    def __init__(self):
        # Regex to keep only alphabetic tokens
        self.alpha_pattern = re.compile(r"^[A-Za-z]+$")

    def clean_comment(self, text: str) -> str:
        """
        Clean a single comment:
        1. Remove encoding errors
        2. Strip HTML tags
        3. Normalize whitespace
        4. Keep only English language
        5. Filter out non-alphabetic tokens
        """
        # 1. Remove encoding errors by re-encoding
        try:
            text = text.encode('utf-8', errors='ignore').decode('utf-8')
        except Exception:
            text = text.encode('ascii', errors='ignore').decode('ascii', errors='ignore')

        # 2. Strip HTML tags
        text = BeautifulSoup(text, 'html.parser').get_text(separator=' ')

        # 3. Normalize whitespace
        text = re.sub(r"\s+", ' ', text).strip()

        # 4. Language detection: keep only English
        try:
            lang = detect(text)
        except Exception:
            return ''
        if lang != 'en':
            return ''

        # 5. Filter tokens to alphabetic only
        tokens = text.split()
        filtered = [tok for tok in tokens if self.alpha_pattern.match(tok)]
        return ' '.join(filtered)

    def process_file(self, input_path: str, output_path: str, delimiter=','):
        """
        Read raw comments CSV, clean each comment, and write output CSV
        with columns: comment (cleaned), num_of_likes, reply_count
        """
        with open(input_path, 'r', newline='', encoding='utf-8') as fin, \
             open(output_path, 'w', newline='', encoding='utf-8') as fout:
            reader = csv.DictReader(fin, delimiter=delimiter)
            # Define output columns: cleaned comment replaces original 'comment'
            fieldnames = ['comment', 'num_of_likes', 'reply_count']
            writer = csv.DictWriter(fout, fieldnames=fieldnames, delimiter=delimiter)
            writer.writeheader()

            for row in reader:
                raw = row.get('comment', '')
                cleaned = self.clean_comment(raw)
                if not cleaned:
                    continue  # skip empty or non-English comments

                # Write only cleaned comment and relevant counts
                writer.writerow({
                    'comment': cleaned,
                    'num_of_likes': row.get('num_of_likes', ''),
                    'reply_count': row.get('reply_count', ''),
                })

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Clean YouTube comments')
    parser.add_argument('--input', required=True, help='Path to raw comments CSV')
    parser.add_argument('--output', required=True, help='Path to save cleaned comments CSV')
    args = parser.parse_args()

    processor = CommentsProcessor()
    processor.process_file(args.input, args.output)
    print(f"Cleaned comments written to {args.output}")
