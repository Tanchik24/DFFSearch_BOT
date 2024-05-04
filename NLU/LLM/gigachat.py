import os
from dotenv import load_dotenv
import json
import uuid
import requests
import logging

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def get_token():
    url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"

    payload = 'scope=GIGACHAT_API_PERS'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json',
        'RqUID': str(uuid.uuid4()),
        'Authorization': os.getenv('AUTHORIZATION')
    }

    response = requests.post(url, headers=headers, data=payload, verify=False)
    response = json.loads(response.text)
    token = response["access_token"]
    os.environ['TOKEN'] = f'Bearer {token}'


def send_request(url, headers, payload, prompt):
    try:
        response = requests.request("POST", url, headers=headers, data=payload, verify=False)
        response_data = json.loads(response.text)
        if 'choices' not in list(response_data.keys()):
            if response_data['message'] == 'Token has expired':
                get_token()
                url, headers, payload = prepare_data(prompt)
                response = requests.request("POST", url, headers=headers, data=payload, verify=False)
                response_data = json.loads(response.text)
        return response_data['choices'][0]['message']['content']
    except Exception as e:
        logging.error(f"Request failed: {e}")
        return None


def prepare_data(prompt):
    url = os.getenv('GIGACHATURL')
    payload = json.dumps({
        "model": "GigaChat",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": float(os.getenv('TEMPERATURE')),
        "top_p": float(os.getenv('TOP_P')),
        "n": int(os.getenv('N')),
        "stream": False,
        "max_tokens": int(os.getenv('MAX_TOKENS')),
        "repetition_penalty": 1
    })
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': os.getenv('TOKEN')
    }
    return url, headers, payload


def get_gigachat_response(prompt):
    url, headers, payload = prepare_data(prompt)
    response = send_request(url, headers, payload, prompt)
    if response is None:
        logging.info("Retrying request...")
        response = send_request(url, headers, payload, prompt)
        if response is None:
            return "Возникла ошибка"
    return response
