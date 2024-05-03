import logging
import re
from typing import Callable
from dff.script import Context
from dff.pipeline import Pipeline
import pymorphy2
from bot.dialog_graph.consts import (INTENTS, SLOTS, FORM, PERSONAL_INFO,
                                     NAME, QUESTION, CODE, EMAIL, DATE, STORAGE)
from NLU.nlu_utils import get_name
from bot.api.api_utils import make_prompt
from bot.api.gigachat import get_gigachat_response
from NLU.SlotIntentExtractor import slot_intent_extractor
from NLU.DateExtractor import date_extractor


def extract_intent(ctx: Context):
    if INTENTS not in ctx.misc:
        ctx.misc[INTENTS] = []

    intent = slot_intent_extractor.predict_intent(ctx.last_request.text)
    ctx.misc[INTENTS].append(intent)


def make_all_slots_field(ctx: Context):
    if STORAGE not in ctx.misc:
        ctx.misc[STORAGE] = []

    if SLOTS not in ctx.misc:
        ctx.misc[SLOTS] = {}

    if FORM not in ctx.misc[SLOTS]:
        ctx.misc[SLOTS][FORM] = {}

    if PERSONAL_INFO not in ctx.misc[SLOTS]:
        ctx.misc[SLOTS][PERSONAL_INFO] = {}

    logging.info(f'Form for user info: -- {ctx.misc[SLOTS][PERSONAL_INFO]}')
    logging.info(f'Form for mentor query info: -- {ctx.misc[SLOTS][FORM]}')


def extract_names(ctx: Context):
    morph = pymorphy2.MorphAnalyzer()
    node = None
    if ctx.last_label is not None:
        node = ctx.last_label[1]

    if node == 'say_hi_node':
        slot_name = PERSONAL_INFO
    elif (node in ['mentor_query_question_node', 'mentor_query_code_node', 'mentor_query_node',
                   'mentor_name_node']) or (
            ctx.misc[INTENTS][-1] in ['mentor_query_question', 'mentor_query_code', 'mentor_query']):
        slot_name = FORM
    else:
        return

    name = get_name(ctx.last_request.text)
    if name is not None:
        name = morph.parse(name)[0]
        name = name.normal_form
        name = name.capitalize()
    logging.info(
        f"Get name for {slot_name} - {name}")
    ctx.misc[SLOTS][slot_name][NAME] = name


def extract_question_code(ctx: Context):
    if ctx.last_label is None:
        return ctx

    intent = ctx.misc[INTENTS][-1]

    if (ctx.last_label[1] in ['mentor_query_node', 'mentor_query_question_node',
                              'mentor_query_code_node']) or intent in ['mentor_query',
                                                                       'mentor_query_question',
                                                                       'mentor_query_code']:

        prompt = make_prompt('mentor_query', ctx)
        text = get_gigachat_response(prompt)
        text = text.replace('"', '').lower()

        if 'вопрос' in text:
            question_match = re.search(r'вопрос: (.*?\?)', text)
            if question_match:
                question_text = question_match.group(1)
                if question_text.lower() != 'нет':
                    ctx.misc[SLOTS][FORM][QUESTION] = question_text

                    logging.info(f'Extracted question from -- {ctx.last_request.text} -- : -- {question_text}')

        if 'код' in text:
            code_split = text.split("код: ")
            if len(code_split) > 1:
                code_text = code_split[1].strip()
                if code_text.lower() != 'нет':
                    ctx.misc[SLOTS][FORM][CODE] = code_text

                    logging.info(f'Extracted question from -- {ctx.last_request.text} -- : -- {code_text}')


def extract_slots(ctx: Context):
    if ctx.last_label is None or ctx.last_request.text is None:
        return ctx

    label = ctx.last_label[1]
    text = ctx.last_request.text

    if label in ['email_node', 'unsuccess_email_node']:
        email = slot_intent_extractor.extract_emails(text)
        ctx.misc[SLOTS][PERSONAL_INFO][EMAIL] = email[0]
        logging.info(f'Extracted email from -- {ctx.last_request.text} -- : -- {email[0]}')

    elif label in ['date_node', 'mentor_query_node', 'mentor_query_question_node', 'mentor_query_code_node'] or \
            ctx.misc[INTENTS][-1] in ['mentor_query', 'mentor_query_question', 'mentor_query_code']:
        slots = slot_intent_extractor.predict_slots(text)
        date = None
        if not slots:
            dates = date_extractor.extract_date(text)
            if dates:
                date = dates[0]
                ctx.misc[SLOTS][FORM][DATE] = date

        for slot in slots:
            if slot[1] == 'DATE':
                date = slot[0]
                ctx.misc[SLOTS][FORM][DATE] = date

        logging.info(f'Extracted date from -- {ctx.last_request.text} -- : -- {date}')

    return ctx


def del_slot(main_slot_name: str, slot_name: str, false_slot: bool) -> Callable:
    def del_slot_inner(ctx: Context, _: Pipeline) -> Context:
        if false_slot:
            if ctx.last_request.text == 'Нет':
                del ctx.misc[SLOTS][main_slot_name][slot_name]
                logging.info(f'Deleted slot -- {slot_name}')
        else:
            if slot_name not in ctx.misc[SLOTS][main_slot_name].keys():
                del ctx.misc[SLOTS][main_slot_name][slot_name]
                logging.info(f'Deleted slot -- {slot_name}')
        return ctx

    return del_slot_inner
