import os

from NLU.LLM.gigachat_utils import make_prompt
from NLU.LLM.gigachat import get_gigachat_response
import re
import logging


class QuestionCodeExtractor:

    def check_question(self, text, ctx):
        if 'вопрос' in text:
            question_match = re.search(r'вопрос: (.*?\?)', text)
            if question_match:
                question_text = question_match.group(1)
                if question_text.lower() != 'нет':
                    logging.info(f'Extracted question from -- {ctx.last_request.text} -- : -- {question_text}')
                    return question_text
        return None

    def check_code(self, text, ctx):
        if 'код' in text:
            code_split = text.split("код: ")
            if len(code_split) > 1:
                code_text = code_split[1].strip()
                if code_text.lower() != 'нет':
                    logging.info(f'Extracted question from -- {ctx.last_request.text} -- : -- {code_text}')
                    return code_text
        return None

    def extract_question_code(self, ctx):
        prompt = make_prompt('mentor_query_node', ctx)
        text = get_gigachat_response(prompt, os.getenv('MODEL_PRO'))
        text = text.replace('"', '').lower()
        question = self.check_question(text, ctx)
        code = self.check_code(text, ctx)
        return question, code


question_code_extractor = QuestionCodeExtractor()
