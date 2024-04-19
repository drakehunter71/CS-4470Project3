import spacy
import re
from bs4 import BeautifulSoup


def extract_social_history(xml_text):
    # Load English tokenizer, tagger, parser, NER, and word vectors
    nlp = spacy.load("en_core_web_sm")

    # Remove XML tags
    clean_text = BeautifulSoup(xml_text, "xml").get_text()

    # Process the text with spaCy
    doc = nlp(clean_text)

    # Find social history section
    social_history_text = ""
    found_social_history = False
    for sent in doc.sents:
        # Check if the sentence contains "social history" or similar keywords
        if re.search(r'\b(?:social history|social Hx|social hx)\b', sent.text, re.IGNORECASE):
            found_social_history = True
        elif found_social_history:
            # Check if the sentence contains indicators of the end of the social history section
            if re.search(r'\b(?:family history|past medical history|present illness|physical exam|review of systems)\b', sent.text, re.IGNORECASE):
                break
            else:
                social_history_text += sent.text + "\n"

    return social_history_text.strip()


# Load XML files and extract social history
xml_files = ["../data/255-01.xml"]

for file_name in xml_files:
    with open(file_name, "r") as file:
        xml_text = file.read()
        social_history = extract_social_history(xml_text)
        print(f"Extracted Social History from {file_name}:")
        print(social_history)
        print("="*50)
