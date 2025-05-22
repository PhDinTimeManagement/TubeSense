import sys
import re
import spacy

class TranscriptProcessor:
    def __init__(self):
        # Load English spaCy model for tokenization, stopword detection, and lemmatization
        try:
            # Disable NER for efficiency, keep parser for sentence splitting and POS tagging
            self.nlp = spacy.load("en_core_web_sm", disable=["ner"])
        except Exception as e:
            sys.stderr.write(
                "SpaCy model 'en_core_web_sm' not found. Please install it (e.g., `python -m spacy download en_core_web_sm`).\n"
            )
            raise e

    # Clean transcript text for topic modeling with BERTopic
    def clean_text(self, text: str) -> str:
        # Remove HTML tags
        text_no_html = re.sub(r'<.*?>', '', text)

        # Remove content inside square brackets (e.g., timestamps, stage directions)
        text_no_brackets = re.sub(r'\[.*?\]', '', text_no_html)

        # Lowercase the text
        text_no_brackets = text_no_brackets.lower()

        # Replace newlines/carriage returns with space to prevent false sentence breaks
        text_no_brackets = text_no_brackets.replace('\n', ' ')
        text_no_brackets = text_no_brackets.replace('\r', ' ')

        # Process text with spaCy (tokenization, stopword removal, lemmatization)
        doc = self.nlp(text_no_brackets)
        cleaned_sentences = []
        for sent in doc.sents:  # iterate over sentences
            # Filter tokens: keep alphabetic words, drop stopwords, then lemmatize
            cleaned_tokens = [
                token.lemma_.lower()
                for token in sent
                if token.is_alpha and not token.is_stop
            ]
            if cleaned_tokens:
                cleaned_sentences.append(" ".join(cleaned_tokens))

        # Join sentences with newline to form the final cleaned text
        return "\n".join(cleaned_sentences)

    # Process the input file to clean the transcript
    def process_file(self, input_path: str, output_path: str):
        # Read the entire file content
        with open(input_path, 'r', encoding='utf-8') as infile:
            content = infile.read()

        # Find the start of actual transcript (after dashed separator line)
        start_idx = content.find('---')
        if start_idx != -1:
            # Move index to end of the dashed line (the newline after the dashes)
            newline_idx = content.find('\n', start_idx)
            if newline_idx != -1:
                content = content[newline_idx:]  # keep content after the dashed line

        # Remove the disclaimer section and anything following it
        disclaimer_idx = content.lower().find('disclaimer:')
        if disclaimer_idx != -1:
            content = content[:disclaimer_idx]

        # Trim any leading whitespace from the extracted transcript
        transcript_text = content.strip()

        # Clean the transcript text using the preprocessing steps
        cleaned_text = self.clean_text(transcript_text)

        # Write the cleaned text to the output file
        with open(output_path, 'w', encoding='utf-8') as outfile:
            outfile.write(cleaned_text)
        return cleaned_text  # also return the cleaned text if needed by caller

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Clean a transcript for BERTopic modeling.")
    parser.add_argument("--input", required=True, help="Path to the input transcript text file")
    parser.add_argument("--output", required=True, help="Path to save the cleaned output text file")
    args = parser.parse_args()

    processor = TranscriptProcessor()
    processor.process_file(args.input, args.output)
    print(f"Cleaned transcript written to {args.output}")
