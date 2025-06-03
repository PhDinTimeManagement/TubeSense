import sys
import re
import spacy

class TranscriptProcessor:
    def __init__(self):
        try:
            self.nlp = spacy.load("en_core_web_sm", disable=["ner"])
        except Exception as e:
            sys.stderr.write(
                "SpaCy model 'en_core_web_sm' not found. Please install it (e.g., `python -m spacy download en_core_web_sm`).\n"
            )
            raise e

    def clean_text(self, text: str) -> str:
        text_no_html = re.sub(r'<.*?>', '', text)

        text_no_brackets = re.sub(r'\[.*?\]', '', text_no_html)

        text_no_brackets = text_no_brackets.lower()

        text_no_brackets = text_no_brackets.replace('\n', ' ')
        text_no_brackets = text_no_brackets.replace('\r', ' ')

        doc = self.nlp(text_no_brackets)
        cleaned_sentences = []
        for sent in doc.sents:
            cleaned_tokens = [
                token.lemma_.lower()
                for token in sent
                if token.is_alpha and not token.is_stop
            ]
            if cleaned_tokens:
                cleaned_sentences.append(" ".join(cleaned_tokens))

        return "\n".join(cleaned_sentences)

    def process_file(self, input_path: str, output_path: str):
        with open(input_path, 'r', encoding='utf-8') as infile:
            content = infile.read()

        start_idx = content.find('---')
        if start_idx != -1:
            newline_idx = content.find('\n', start_idx)
            if newline_idx != -1:
                content = content[newline_idx:]

        disclaimer_idx = content.lower().find('disclaimer:')
        if disclaimer_idx != -1:
            content = content[:disclaimer_idx]

        transcript_text = content.strip()

        cleaned_text = self.clean_text(transcript_text)

        with open(output_path, 'w', encoding='utf-8') as outfile:
            outfile.write(cleaned_text)
        return cleaned_text

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Clean a transcript for BERTopic modeling.")
    parser.add_argument("--input", required=True, help="Path to the input transcript text file")
    parser.add_argument("--output", required=True, help="Path to save the cleaned output text file")
    args = parser.parse_args()

    processor = TranscriptProcessor()
    processor.process_file(args.input, args.output)
    print(f"Cleaned transcript written to {args.output}")
