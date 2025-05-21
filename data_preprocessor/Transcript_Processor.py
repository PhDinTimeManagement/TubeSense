import re
from bs4 import BeautifulSoup

class TranscriptProcessor:
    """
    Extract and clean transcript from raw transcript files.
    """
    def __init__(self):
        # Regex to strip bracketed timestamps or metadata
        self.bracket_pattern = re.compile(r"\[.*?\]")

    def extract_transcript(self, raw_lines):
        """
        Given a list of lines from a raw transcript file, extract the real transcript
        between the dashed separator and the 'DISCLAIMER:' marker.
        """
        start_idx = None
        end_idx = None
        for i, line in enumerate(raw_lines):
            if line.strip().startswith('-') and set(line.strip()) == {'-'}:
                # Found a line comprised solely of dashes
                start_idx = i + 1
                break
        for j, line in enumerate(raw_lines):
            if line.strip().upper().startswith('DISCLAIMER'):
                end_idx = j
                break
        if start_idx is None or end_idx is None or end_idx <= start_idx:
            raise ValueError("Could not find transcript boundaries in file.")
        return raw_lines[start_idx:end_idx]

    def clean_transcript(self, lines):
        """
        Clean transcript lines: remove HTML tags, bracketed text, and normalize whitespace.
        """
        # Join lines into a single string
        text = ' '.join(line.strip() for line in lines)
        # Strip HTML tags
        text = BeautifulSoup(text, 'html.parser').get_text(separator=' ')
        # Remove bracketed timestamps/metadata
        text = self.bracket_pattern.sub('', text)
        # Normalize whitespace
        text = re.sub(r"\s+", ' ', text).strip()
        return text

    def process_file(self, input_path: str, output_path: str):
        """
        Read a raw transcript text file, extract the transcript, clean it,
        and write the cleaned text to an output file.
        """
        with open(input_path, 'r', encoding='utf-8') as fin:
            raw_lines = fin.readlines()

        # Extract the relevant transcript
        transcript_lines = self.extract_transcript(raw_lines)
        # Clean the transcript
        cleaned_text = self.clean_transcript(transcript_lines)

        # Save cleaned transcript
        with open(output_path, 'w', encoding='utf-8') as fout:
            fout.write(cleaned_text)

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Extract and clean YouTube transcript')
    parser.add_argument('--input', required=True, help='Raw transcript file path')
    parser.add_argument('--output', required=True, help='Cleaned transcript output path')
    args = parser.parse_args()

    processor = TranscriptProcessor()
    processor.process_file(args.input, args.output)
    print(f"Cleaned transcript written to {args.output}")
