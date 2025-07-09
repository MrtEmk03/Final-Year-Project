import re
import langid
from src.genreMapping import GENRE_MAPPING

def detect_language(text):
    """
    Detects language of the input text using signals from genre mapping
    counts how many synonyms from the Turkish and English sections match in the text
    If Turkish synonyms outnumber English ones, it returns 'tr'
    Otherwise, it falls back to using langid (with an additional heuristic for low confidence)

    Args:
        text (str): The text input from the user

    Returns:
        str: 'tr' if Turkish is detected, otherwise 'en'
    """
    text = text.strip()
    if not text:
        return "en"
    
    text_lower = text.lower()

    #Count matches in genre mapping for Turkish and English
    turkish_count = 0
    for genre, details in GENRE_MAPPING.get("tr", {}).items():
        for synonym in details.get("synonyms", []):
            pattern = r'\b' + re.escape(synonym.lower()) + r'\b'
            if re.search(pattern, text_lower):
                turkish_count += 1

    english_count = 0
    for genre, details in GENRE_MAPPING.get("en", {}).items():
        for synonym in details.get("synonyms", []):
            pattern = r'\b' + re.escape(synonym.lower()) + r'\b'
            if re.search(pattern, text_lower):
                english_count += 1

    # Debug print:
    # print(f"Turkish genre matches: {turkish_count}, English genre matches: {english_count}")

    #If Turkish matches are significantly higher than English, decide Turkish
    if turkish_count > english_count:
        return "tr"

    #For very short text, fallback to a simple check for Turkish-specific characters
    if len(text) < 5:
        if any(ch in text for ch in "çğıöşüÇĞİÖŞÜ"):
            return "tr"
        return "en"
    
    #Use langid as fallback
    lang, confidence = langid.classify(text)
    
    #If the confidence low, use extra heuristic based on Turkish character freq
    if confidence < 0.7:
        turkish_chars = "çğıöşü"
        turkish_char_count = sum(text_lower.count(ch) for ch in turkish_chars)
        if len(text_lower) > 0 and (turkish_char_count / len(text_lower)) > 0.05:
            return "tr"
        else:
            return "en"
    
    #Otherwise, trust langid output
    return "tr" if lang == "tr" else "en"
