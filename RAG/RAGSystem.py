import requests


class RAGSystem:
    def __init__(self):
        self.url = 'http://127.0.0.1:8081/message'

    def format_to_html(self, text):
        print(text)
        formatted_text = text.replace("\n\n1", "<br><br>")
        formatted_text = formatted_text.replace("\n", "<br>")
        print(formatted_text)
        return formatted_text

    def get_answer(self, text, context_id, intent, node):
        params = {
            'question': text,
            'session_id': context_id,
            'intent': intent,
            'node_name': node
        }
        print(text)
        response = requests.get(self.url, params=params)
        print(response.status_code)
        print(response.text)

        if response.status_code == 200:
            text = response.text.replace('"', '')
            return self.format_to_html(text)


rag_system = RAGSystem()
