import requests
from src.genreMapping import GENRE_MAPPING
from sentence_transformers import SentenceTransformer, util

#Load the Sentence Transformer model for semantic similarity ranking
semantic_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

def hybrid_recommendation(user_input, entities, api_key, language, num_recommendations=3):
    base_url = "https://api.themoviedb.org/3/discover/movie"

    #Resolve actor and director IDs with error handling
    def get_person_id(name):
        search_url = "https://api.themoviedb.org/3/search/person"
        params = {"api_key": api_key, "query": name}
        try:
            response = requests.get(search_url, params=params)
            if response.status_code == 200:
                results = response.json().get("results", [])
                if results:
                    return results[0]["id"]
        except requests.RequestException as e:
            print(f"Error resolving TMDB ID for {name}: {e}")
        return None

    #Resolve actor and director IDs
    actor_ids = [str(get_person_id(actor)) for actor in entities.get("actors", []) if get_person_id(actor)]
    director_ids = [str(get_person_id(director)) for director in entities.get("directors", []) if get_person_id(director)]

    #Build query parameters
    params = {
        "api_key": api_key,
        "language": "tr" if language == "tr" else "en-US",
        "sort_by": entities.get("sort_by", "popularity.desc"),
        "with_genres": ",".join(str(genre) for genre in entities.get("genres", [])),
        "without_genres": ",".join(
            str(GENRE_MAPPING[language].get(g, {}).get("id")) for g in entities.get("exclude", []) if g in GENRE_MAPPING[language]
        ),
        "with_cast": ",".join(actor_ids),
        "with_crew": ",".join(director_ids),
        "vote_average.gte": entities.get("vote_average", 5),
        "with_runtime.lte": entities.get("runtime"),
        "with_budget.gte": entities.get("budget") if entities.get("budget") else None,
        "append_to_response": "translations"
    }

    #Handle release year range
    if entities.get("release_year_range"):
        start_year, end_year = entities["release_year_range"]
        params["primary_release_date.gte"] = f"{start_year}-01-01"
        params["primary_release_date.lte"] = f"{end_year}-12-31"
    elif entities.get("release_year"):
        year = entities["release_year"]
        params["primary_release_date.gte"] = f"{year}-01-01"
        params["primary_release_date.lte"] = f"{year}-12-31"

    #Remove empty parameters
    params = {k: v for k, v in params.items() if v not  in [None, ""]}

    #Debug Print API parameters
    print("API Parameters:", params)

    #Send API request
    response = requests.get(base_url, params=params)
    if response.status_code != 200:
        print(f"Error with TMDB API: {response.status_code}")
        print("Response Content:", response.text)
        return []

    #Parse API results
    results = response.json().get("results", [])
    
    #If no results, return empty list
    if not results:
        return []

    #Convert user query to embedding
    query_embedding = semantic_model.encode(user_input, convert_to_tensor=True)

    #Rank movies using cosine similarity
    ranked_movies = []
    for movie in results:
        overview = movie.get("overview", "No overview available.")
        #If the lang Turkish, check for a Turkish translation
        if language == "tr" and "translations" in movie:
            translations = movie["translations"].get("translations", [])
            for trans in translations:
                if trans.get("iso_639_1") == "tr":
                    tr_overview = trans.get("data", {}).get("overview")
                    if tr_overview:
                        print("\n here \n")
                        overview = tr_overview
                        break
        movie_embedding = semantic_model.encode(overview, convert_to_tensor=True)
        similarity_score = util.cos_sim(query_embedding, movie_embedding).item()

        ranked_movies.append({
            "title": movie.get("title", "Unknown Title"),
            "overview": overview,
            "similarity": similarity_score
        })

    #Sort movies based on similarity score
    ranked_movies.sort(key=lambda x: x["similarity"], reverse=True)

    return ranked_movies[:num_recommendations]
