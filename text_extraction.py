import sys
import os
import argparse
import requests
import re
from bs4 import BeautifulSoup
from pypdf import PdfReader

OUTPUT_DIR = "outputs"  

class TibetanTextProcessor:
    @staticmethod
    def clean_tibetan_text(text: str) -> str:
        """Clean and normalize text."""
        if not text:
            return None
        text = text.encode('utf-8', errors='ignore').decode('utf-8')  # Force UTF-8
        text = re.sub(r'\s+', ' ', text.strip())
        # text = re.sub(r'\s+','',text.strip())
        
        if text.startswith("www.") or text.startswith("https"):
            print(f"Rejected (link): {text[:50]}...")
            return None

        if len(text) < 20:
        #     print("CHECKING LEN...")
        #     print(f"Rejected (word count): {text[:5]}...")
            return None
        
        if not text.endswith('།'):
            text += '།'
        # text = UNICODE NORMALIZE 
        return text


    @staticmethod
    def is_tibetan_sentence(text):
        """Check if sentence has Tibetan. word_count bounds: 5 to 30 words."""
        if not text:
            return False
        
        has_tibetan = bool(re.search(r'[\u0F00-\u0FFF]', text))
        if not has_tibetan:
            print(f"Rejected (no Tibetan): {text[:50]}...")
            return False
    
        return True

    @staticmethod
    def extract_sentences(blocks) -> list[str]:
        """Extracts sentences from paragraphs/pages. Returns sentences."""
        # DECLARE CONNECTORS (removed shad because text was split upon shad.)
        CONNECTORS = {"དང་", "ཡིན་ན", "ན", "རུང་", "ཡིན", "ག་"}

        sentences = []
        seen_sentences = set()
        current_sentence = ""

        for b in blocks:
            text = b.get_text(separator=' ', strip=True).replace('\xa0', ' ')
            if not text:
                continue

            raw_sentences = [s.strip() for s in text.split('།') if s.strip()]

            for raw_sent in raw_sentences:
                if any (raw_sent.endswith(connector) for connector in CONNECTORS):
                    print("RAW_SENT ENDS WITH CONNECTOR")
                    current_sentence += raw_sent + "། "
                else:
                    if current_sentence:
                        print("CURRENT_SENTENCE EXISTS.")
                        full_sentence = current_sentence + raw_sent
                        current_sentence = ""
                    else:
                        full_sentence = raw_sent

                    if TibetanTextProcessor.is_tibetan_sentence(full_sentence):
                        cleaned = TibetanTextProcessor.clean_tibetan_text(full_sentence)
                        if cleaned is not None and cleaned not in seen_sentences:
                            sentences.append(cleaned)
                            seen_sentences.add(cleaned)
        return sentences

class InputAccessTester:
    @staticmethod
    def is_url_accessible(url):
        try:
            response = requests.head(url, allow_redirects=True, timeout=5)
            return response.status_code == 200
        except (requests.RequestException, requests.Timeout):
            return False

    @staticmethod
    def is_pdf_accessible(filepath):
        if not os.path.exists(filepath):
            return False
        if not filepath.lower().endswith('.pdf'):
            return False
        try:
            with open(filepath, 'rb') as f:
                # Check if the file starts with PDF magic number "%PDF"
                return f.read(4) == b'%PDF'
        except IOError:
            return False
    

def extract_from_web(url) -> list[str]:
    """
    Takes web url and returns sentences.
    """
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')
    
        main_content = soup.select_one('article, .article-content, .post-content, .entry-content, .l-content')
        if not main_content:
            main_content = soup.body
        
        
        paragraphs = main_content.select('p, h1, h2, h3, h4, h5, h6, div')
        print(f"Found {len(paragraphs)} paragraphs.")

        sentences = TibetanTextProcessor.extract_sentences(paragraphs)

    except Exception as e:
        print(f"Error processing {url}: {str(e).encode('utf-8', errors='replace').decode('utf-8')}", file=sys.stderr)
        return []
    
    return sentences


def extract_from_pdf(filename) -> list[str]:
    reader = PdfReader(filename)
    number_of_pages = len(reader.pages)
    print(f"Found {number_of_pages} pages.")

    sentences = TibetanTextProcessor.extract_sentences(reader.pages)

    return

def run(parser, args):
    """Extract sentences from url link, write to out file."""
    input_path=args.input_path
    # output_path=args.output_path
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    module_path = os.path.dirname(os.path.realpath(__file__))
    # output_file = os.path.join(module_path, output_path)
    output_file = os.path.join(
        OUTPUT_DIR,
        os.path.basename(args.output_path)
    )

    with open(output_file, 'w', encoding='utf-8') as fout:
        print("RUN")

        if args.url:
            print("URL format was specified")
            extracted_sentences = extract_from_web(input_path)
        elif args.pdf:
            input_path = os.path.join(module_path, 'input_file')
            print("PDF format was specified")
            extracted_sentences = extract_from_pdf(input_path)
        else:
            print("No format flag was specified, using default behavior")
            parser.error("You must specify either --url or --pdf")

        for s in extracted_sentences:
            fout.write(s + '\n')
        print(f"Extracted {len(extracted_sentences)} sentences to {output_file}")


def run_pdf(input_path, output_path):
    """Extract sentences from pdf path, write to out file."""
    with open(output_path, 'w', encoding='utf-8') as fout:
        print("RUN PDF")
        extracted_sentences = extract_from_pdf(input_path)
        for s in extracted_sentences:
            fout.write(s + '\n')
        print(f"Extracted {len(extracted_sentences)} sentences to {output_path}")


def main():
    """
    ARGS:
        - input file format
        - input url / file path
        - output file path

    EXAMPLE: python scripts/text_extraction.py --url https://tibet.net/covid-19/?p=140 test0.out
    """
    parser = argparse.ArgumentParser(description="Get Tibetan source texts.")

    format_group = parser.add_mutually_exclusive_group()
    format_group.add_argument("--url", action="store_true",
                        help="Input in url format.")
    format_group.add_argument("--pdf", action="store_true",
                        help="Input in pdf format.")
    parser.add_argument("input_path", type=str, default="",
                        help="Link/file path for chosen mode.")
    parser.add_argument("output_path", help="Path to output file.")

    args = parser.parse_args()

    run(parser=parser, args=args)


if __name__ == "__main__":
    main()