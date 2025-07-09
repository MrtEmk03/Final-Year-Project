import re 
import stanza
from src.genreMapping import GENRE_MAPPING
from src.synonymMapping import SYNONYM_MAPPING
from src.peopleMapping import KNOWN_PEOPLE 
from rapidfuzz import process, fuzz
from sentence_transformers import SentenceTransformer, util

def turkish_lower(text):
    """
    Converts text to lowercase using Turkish-specific rules
    Maps 'I' to 'ı' and 'İ' to 'i' using a translation table,
    then applies the standard lower() for the rest of the text
    """
    mapping = str.maketrans({"I": "ı", "İ": "i"})
    return text.translate(mapping).lower()

#Initialize Stanza Pipelines
english_nlp = stanza.Pipeline(lang="en", processors="tokenize,ner,pos,lemma", verbose=False)
turkish_nlp = stanza.Pipeline(lang="tr", processors="tokenize,ner,pos,lemma", verbose=False)

#Use a multilingual SentenceTransformer model for semantic similarity
semantic_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

def extract_entities(user_input, language):
    #Select the appropriate NLP pipeline
    nlp = english_nlp if language == "en" else turkish_nlp

    #Normalize Input
    if language == "tr":
        normalized_input = turkish_lower(user_input)
        corrected_input = user_input  #Preserve original casing for proper names
    else:
        normalized_input = user_input.lower()
        corrected_input = user_input.lower().title()

    #Fuzzy Matching for Actors and Directors
    #Build normalized mappings using our custom lowercasing for Turkish
    if language == "tr":
        actors_mapping = {turkish_lower(actor): actor for actor in KNOWN_PEOPLE["actors"]}
        directors_mapping = {turkish_lower(director): director for director in KNOWN_PEOPLE["directors"]}
    else:
        actors_mapping = {actor.lower(): actor for actor in KNOWN_PEOPLE["actors"]}
        directors_mapping = {director.lower(): director for director in KNOWN_PEOPLE["directors"]}

    words = normalized_input.split()
    temp_replacements = []

    for size in range(1, len(words) + 1):
        for i in range(len(words) - size + 1):
            combined_words = " ".join(words[i:i + size])
            #Use token_set_ratio for better multi-token comparison
            actor_match = process.extractOne(
                combined_words, list(actors_mapping.keys()), scorer=fuzz.token_set_ratio
            )
            if actor_match and actor_match[1] > 70:
                temp_replacements.append((combined_words, actors_mapping[actor_match[0]]))
            
            director_match = process.extractOne(
                combined_words, list(directors_mapping.keys()), scorer=fuzz.token_set_ratio
            )
            if director_match and director_match[1] > 70:
                temp_replacements.append((combined_words, directors_mapping[director_match[0]]))

    #Replace detected substrings case insensitive replacement
    for original, replacement in temp_replacements:
        corrected_input = re.sub(re.escape(original), replacement, corrected_input, flags=re.IGNORECASE)

    print(f"Corrected Input After Fuzzy Matching: {corrected_input}")

    #Run NER on Corrected Input
    doc = nlp(corrected_input)
    ner_candidates = [ent.text for ent in doc.ents]

    entities = {
        "actors": [],
        "directors": [],
        "genres": [],
        "release_year": None,
        "release_year_range": None,
        "budget": None,
        "production_companies": [],
        "runtime": None,
        "keywords": [],
        "popularity": None,
        "sort_by": None,
        "exclude": [],
    }

    def match_candidate(candidate, mapping):
        """
        Match the normalized candidate against the mapping of known names
        Uses fuzz.token_set_ratio
        adjusts the threshold if token counts differ
        """
        if language == "tr":
            candidate_norm = turkish_lower(candidate)
        else:
            candidate_norm = candidate.lower()
        best_match, score, _ = process.extractOne(
            candidate_norm, list(mapping.keys()), scorer=fuzz.token_set_ratio, score_cutoff=0
        ) or (None, 0, None)
    
        if not best_match:
            return None

        candidate_tokens = candidate_norm.split()
        known_tokens = best_match.split()
        threshold = 80
        if len(candidate_tokens) != len(known_tokens):
            threshold = 90  #Higher threshold if token counts differ
    
        if score >= threshold:
            return mapping[best_match]
        return None

    for candidate in ner_candidates:
        actor_name = match_candidate(candidate, actors_mapping)
        if actor_name and actor_name not in entities["actors"]:
            entities["actors"].append(actor_name)
        director_name = match_candidate(candidate, directors_mapping)
        if director_name and director_name not in entities["directors"]:
            entities["directors"].append(director_name)

    print(f"NER Detected Entities: {ner_candidates}")
    print(f"Matched Actors After NER: {entities['actors']}")
    print(f"Matched Directors After NER: {entities['directors']}")

    #Extract Genres 
    genre_found = False
    lower_corrected = corrected_input.lower()
    for genre, details in GENRE_MAPPING[language].items():
        if any(word in lower_corrected.split() for word in details["synonyms"]):
            entities["genres"].append(details["id"])
            genre_found = True
            break

    if not genre_found:
        genre_candidates = [details["synonyms"] for details in GENRE_MAPPING[language].values()]
        flattened_candidates = [item for sublist in genre_candidates for item in sublist]
        embeddings1 = semantic_model.encode([user_input], convert_to_tensor=True)
        embeddings2 = semantic_model.encode(flattened_candidates, convert_to_tensor=True)
        cosine_scores = util.cos_sim(embeddings1, embeddings2)
        best_match_idx = cosine_scores.argmax().item()
        if best_match_idx < len(flattened_candidates):
            best_genre = flattened_candidates[best_match_idx]
            for genre, details in GENRE_MAPPING[language].items():
                if best_genre in details["synonyms"]:
                    entities["genres"].append(details["id"])
                    break

    #Extract Sorting Preference
    for sort_key, sort_value in SYNONYM_MAPPING["sort_by"].items():
        if sort_key in corrected_input.lower():
            entities["sort_by"] = sort_value
            break

    #Extract Year Information
    if language == "tr":
        year_pattern = re.compile(r"\b(\d{4})\b")
        decade_pattern = re.compile(r"\b(\d{2,4})'?lar\b", re.IGNORECASE)
    else:
        year_pattern = re.compile(r"(?:in|from|came out in)?\s*(\d{4})", re.IGNORECASE)
        decade_pattern = re.compile(r"(\d{4})s", re.IGNORECASE)
    
    year_match = year_pattern.search(corrected_input)
    if year_match:
        year = int(year_match.group(1))
        if 1900 <= year <= 2100:
            entities["release_year"] = year

    decade_match = decade_pattern.search(corrected_input)
    if decade_match and not entities["release_year_range"]:
        decade_val = decade_match.group(1)
        if len(decade_val) == 2:
            start_year = 1900 + int(decade_val)
        else:
            start_year = int(decade_val)
        end_year = start_year + 9
        if 1900 <= start_year <= 2100:
            entities["release_year_range"] = (start_year, end_year)

    for budget_key, budget_range in SYNONYM_MAPPING["budget"].items():
        if budget_key in corrected_input.lower():
            entities["budget"] = budget_range
            break
    
    for exclude_key in SYNONYM_MAPPING.get("exclude", {}).keys():
        if exclude_key in corrected_input.lower():
            entities["exclude"].append(exclude_key)

    print("Extracted Entities:", entities)
    return entities
