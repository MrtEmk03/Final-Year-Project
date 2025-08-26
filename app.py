import requests
import stanza
import os
from tkinter import Tk
from ui.userInterface import MovieChatbotUI
from src.languageDetection import detect_language
from src.entityRecognition import extract_entities
from src.hybridRecommendation import hybrid_recommendation
from data.responses import response_pools
import random


#Download Stanza models if they haven't been downloaded yet
if not os.path.exists(os.path.expanduser('~/stanza_resources')):
    stanza.download('en')  #English model
    stanza.download('tr')  #Turkish model

API_KEY = ""

def get_dynamic_response(category, language="en"):
    """
    Fetch a dynamic response from the response pool for a given category and language.
    """
    if category not in response_pools:
        print(f"Category '{category}' not found in response_pools.")
        return "I'm sorry, I couldn't process your request."  #Default fallback

    if language in response_pools[category]:
        return random.choice(response_pools[category][language])

    if "en" in response_pools[category]:
        return random.choice(response_pools[category]["en"])

    return "I'm sorry, I couldn't find a suitable response."

def handle_user_input():
    """Handles user input from the UI."""
    user_input = ui.get_user_input()
    if not user_input.strip():
        return  #Ignore empty input

    #Detect language if undetected default to English 
    detected_language = detect_language(user_input)

    #Display the input in the chat
    ui.display_message("You", user_input)

    #proceed with the movie recommendation flow
    fetching_response = get_dynamic_response("fetching", detected_language)
    ui.display_message("ScreenScout ", f"{fetching_response}{user_input}")

    #Extract entities using NLP
    entities = extract_entities(user_input, detected_language)
    print(f"Extracted entities: {entities}")

    #Get movie recommendations based on the extracted entities
    recommendations = hybrid_recommendation(
        user_input=user_input,
        entities=entities,
        api_key=API_KEY,
        num_recommendations=3,#Limit to 3 recommendations
        language= detected_language  
    )
    print(f"Recommendations: {recommendations}")
    if recommendations:
        chatbot_response = get_dynamic_response("recommendation", detected_language)
        ui.display_message("ScreenScout ", chatbot_response)
        for movie in recommendations:
            title = movie["title"]
            overview = movie.get("overview", "No overview available.")

            if detected_language == "tr" and movie.get("original_language") != "tr":
                overview = movie.get("overview", "No overview available.")  #Fallback to English
            ui.display_message("ScreenScout ", f"{title}: {overview}")
    else:
        chatbot_response = get_dynamic_response("unknown", detected_language)
        ui.display_message("ScreenScout ", chatbot_response)

#Init UI
root = Tk()
ui = MovieChatbotUI(root, handle_user_input)
#Start app
root.mainloop()
