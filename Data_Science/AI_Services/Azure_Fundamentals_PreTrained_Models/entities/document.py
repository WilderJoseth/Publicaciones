from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient

class Document:
    def __init__(self, ai_endpoint, ai_key):
        self.__ai_version = "5.3.0"
        self.__ai_library = "azure-ai-textanalytics"
        self.main_language = ""
        self.sentiment = []
        self.phrases = []
        self.entities = []
        self.entities_link = []

        # Client instance
        self.__ai_client = TextAnalyticsClient(
            endpoint = ai_endpoint,
            credential = AzureKeyCredential(ai_key)
        )

    def __str__(self):
        return f"Libray: {self.__ai_library}, Version: {self.__ai_version}"
    
    def read(self, file_path):
        with open(file_path, encoding="utf8") as f:
            self.file_data = f.read()

    def getLanguage(self):
        detectedLanguage = self.__ai_client.detect_language(documents=[self.file_data])[0]
        self.main_language = detectedLanguage.primary_language.name

        print("\nLanguage detection:")
        print(f"Main language: {detectedLanguage.primary_language.name}")
        
    def getSentiment(self):
        result = self.__ai_client.analyze_sentiment(documents=[self.file_data])
        doc_result_ok = [doc for doc in result if not doc.is_error]

        print("\nSentiment detection:")
        for idx, doc in enumerate(doc_result_ok):
            self.sentiment.append(f"DocumentId: {idx + 1}, Overall Sentiment: {doc.sentiment}, Positive score: {doc.confidence_scores.positive}, Neutral score: {doc.confidence_scores.neutral}, Negative score: {doc.confidence_scores.negative}")
            print(f"DocumentId: {idx + 1}, Overall Sentiment: {doc.sentiment}, Positive score: {doc.confidence_scores.positive}, Neutral score: {doc.confidence_scores.neutral}, Negative score: {doc.confidence_scores.negative}")

    def getPhrases(self):
        result = self.__ai_client.extract_key_phrases(documents=[self.file_data])
        doc_result_ok = [doc for doc in result if not doc.is_error]

        print("\nPhrases detection:")
        for idx, doc in enumerate(doc_result_ok):
            print(f"DocumentId: {idx + 1}")

            if len(doc.key_phrases) > 0:
                for phrase in doc.key_phrases:
                    self.phrases.append(f"DocumentId: {idx + 1}, Phrases: {phrase}")
                    print(f"DocumentId: {idx + 1}, Phrases: {phrase}")
            else:
                self.phrases.append("No phrases found")
                print("No phrases found")

    def getEntities(self):
        result = self.__ai_client.recognize_entities(documents=[self.file_data])
        doc_result_ok = [doc for doc in result if not doc.is_error]

        print("\nEntity detection:")
        for idx, doc in enumerate(doc_result_ok):
            print(f"DocumentId: {idx + 1}")

            if len(doc.entities) > 0:
                for entity in doc.entities:
                    self.entities.append(f"DocumentId: {idx + 1}, Entity: {entity.text}, Category: {entity.category}")
                    print(f"Entity: {entity.text}, Category: {entity.category}")
            else:
                self.entities.append("No entities found")
                print("No entities found")

    def getLinkedEntities(self):
        result = self.__ai_client.recognize_linked_entities(documents=[self.file_data])
        doc_result_ok = [doc for doc in result if not doc.is_error]

        print("\nEntity link detection:")
        for idx, doc in enumerate(doc_result_ok):
            print(f"DocumentId: {idx + 1}")

            if len(doc.entities) > 0:
                for entity in doc.entities:
                    self.entities_link.append(f"DocumentId: {idx + 1}, Entity: {entity.name}, Wikipedia link: {entity.url if entity.data_source == 'Wikipedia' else 'No found'}")
                    print(f"DocumentId: {idx + 1}, Entity: {entity.name}, Wikipedia link: {entity.url if entity.data_source == 'Wikipedia' else 'No found'}")
            else:
                self.entities_link.append("No linked entities found")
                print("No linked entities found")