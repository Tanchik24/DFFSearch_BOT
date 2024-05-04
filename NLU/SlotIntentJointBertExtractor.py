import os
import re
from typing import Dict
from dotenv import load_dotenv
import logging
import requests

load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class SlotIntentExtractor:
    def __init__(self):
        self.cache: Dict[str, tuple] = {}

    def predict_intent(self, message: str) -> str:
        if message is None:
            return 'out_of_scope'
        if message not in self.cache:
            self.__get_predict_from_jointbert(message)
        intent, proba = self.cache[message][0]
        logging.info(f"The model recognized the intent '{intent}' with a probability of {proba:.2%}")
        return intent if proba > 0.8 else 'out_of_scope'

    def predict_slots(self, message: str) -> dict:
        if message not in self.cache:
            self.__get_predict_from_jointbert(message)
        return self.cache[message][1]

    def __get_predict_from_jointbert(self, message: str):
        url = os.getenv('JOINTBERT_URL')
        if not url:
            raise ValueError("Environment variable JOINTBERT_URL not set")
        try:
            response = requests.post(url, json={'text': message})
            response.raise_for_status()
            data = response.json()
            self.cache[message] = ((data['intent'], data['proba']), data['slots'])
        except requests.RequestException as e:
            logging.error(f"Request failed: {e}")
        except ValueError:
            logging.error("JSON decode error")

    def extract_emails(self, text):
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
        emails = re.findall(email_pattern, text)
        return emails


slot_intent_extractor = SlotIntentExtractor()
