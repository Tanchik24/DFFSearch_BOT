import logging
import json
import requests
import os
from typing import Callable
from dff.script import Context
from dff.pipeline import Pipeline
from bot.dialog_graph.consts import (INTENTS, SLOTS, FORM, PERSONAL_INFO,
                                     NAME, QUESTION, CODE, EMAIL, DATE, STORAGE,
                                     TRAINING_PROGRESS, TEST_FLAG)
from NLU.nlu_utils import get_name
from NLU.QuestionCodeExtractor import question_code_extractor
from NLU.SlotIntentJointBertExtractor import slot_intent_extractor
from NLU.EmailExtractor import email_extractor
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

    if TRAINING_PROGRESS not in ctx.misc[SLOTS]:
        with open(os.getenv('TRAINING_PREGRESS'), 'r', encoding='utf-8') as file:
            training_data = json.load(file)
        ctx.misc[SLOTS][TRAINING_PROGRESS] = training_data

    if TEST_FLAG not in ctx.misc[SLOTS]:
        ctx.misc[SLOTS][TEST_FLAG] = False

    if 'test' not in ctx.misc[SLOTS]:
        ctx.misc[SLOTS]['test'] = {}

    logging.info(f'Form for user info: -- {ctx.misc[SLOTS][PERSONAL_INFO]}')
    logging.info(f'Form for mentor query info: -- {ctx.misc[SLOTS][FORM]}')


def extract_names(ctx: Context):
    node = None
    if ctx.last_label is not None:
        node = ctx.last_label[1]

    if node == 'say_hi_node':
        slot_name = PERSONAL_INFO
    elif (node in ['mentor_query_node', 'mentor_name_node']) or (
            ctx.misc[INTENTS][-1] in ['mentor_query']):
        slot_name = FORM
    else:
        return

    name = get_name(ctx.last_request.text)
    logging.info(
        f"Get name for {slot_name} - {name}")
    ctx.misc[SLOTS][slot_name][NAME] = name


def extract_question_code(ctx: Context):
    if ctx.last_label is None:
        return ctx

    intent = ctx.misc[INTENTS][-1]
    if (ctx.last_label[1] in ['mentor_query_node']) or (intent in ['mentor_query']):
        question, code = question_code_extractor.extract_question_code(ctx)

        if question is not None:
            ctx.misc[SLOTS][FORM][QUESTION] = question
        if code is not None:
            ctx.misc[SLOTS][FORM][CODE] = code


def extract_slots(ctx: Context):
    if ctx.last_label is None or ctx.last_request.text is None:
        return ctx

    label = ctx.last_label[1]
    text = ctx.last_request.text

    if label in ['email_node', 'unsuccess_email_node']:
        email = email_extractor.extract_emails(text)
        if not email:
            return ctx
        ctx.misc[SLOTS][PERSONAL_INFO][EMAIL] = email[0]
        logging.info(f'Extracted email from -- {ctx.last_request.text} -- : -- {email[0]}')

    elif label in ['date_node', 'mentor_query_node'] or \
            ctx.misc[INTENTS][-1] in ['mentor_query']:
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
        if (ctx.last_label[1] == 'are_u_sure_node') and (ctx.last_request.text == 'Да'):
            if slot_name in ctx[SLOTS][main_slot_name]:
                del ctx[SLOTS][main_slot_name][slot_name]
        if false_slot:
            if ctx.last_request.text == 'Нет':
                del ctx.misc[SLOTS][main_slot_name][slot_name]
                logging.info(f'Deleted slot -- {slot_name}')
        else:
            if slot_name in ctx.misc[SLOTS][main_slot_name].keys():
                del ctx.misc[SLOTS][main_slot_name][slot_name]
                logging.info(f'Deleted slot -- {slot_name}')
        return ctx

    return del_slot_inner


def change_flag(flag_name, value) -> Callable:
    def change_flag_inner(ctx: Context, _: Pipeline) -> Context:
        ctx.misc[SLOTS][flag_name] = value
        return ctx

    return change_flag_inner


def test_answer_processing() -> Callable:
    def test_answer_processing_inner(ctx: Context, _: Pipeline) -> Context:
        ctx.misc[SLOTS]['test']['user_answers'].append(ctx.last_request.text)
        return ctx

    return test_answer_processing_inner


def clear_intents() -> Callable:
    def clear_intents_inner(ctx: Context, _: Pipeline) -> Context:
        ctx.clear(0)
        return ctx

    return clear_intents_inner


def stats(ctx: Context):
    session_id = ctx.id
    message = ctx.last_request.text
    node_name = ctx.last_label[1]
    intent = ctx.misc[INTENTS][-1]

    url = os.getenv('RAG_URL')
    params = {
        'message': message,
        'session_id': session_id,
        'intent': intent,
        'node_name': node_name,
    }

    response = requests.get(url + 'stats', params=params)
    logging.info(f'Stats was sent with code response {response}')
