import os
from dotenv import load_dotenv

from entities.document import Document

def analyzeText(file_path):
    # Get Configuration Settings
    load_dotenv()
    ai_endpoint = os.getenv("AI_SERVICE_ENDPOINT_LG")
    ai_key = os.getenv("AI_SERVICE_KEY_LG")

    # To store results
    result = {}

    document = Document(ai_endpoint, ai_key)
    document.read(file_path)
    document.getLanguage()
    document.getSentiment()
    document.getPhrases()
    document.getEntities()
    document.getLinkedEntities()

    result["language"] = document.main_language
    result["sentiment"] = document.sentiment
    result["phrases"] = document.phrases
    result["entities"] = document.entities
    result["entities_link"] = document.entities_link

    return result

def getChatBotKey():
    load_dotenv()
    return os.getenv("AI_SERVICE_KEY_CHAT")