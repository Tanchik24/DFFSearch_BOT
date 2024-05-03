from dff.script import Context
import random
from dff.pipeline import Pipeline
from dff.messengers.telegram import TelegramMessage, TelegramUI, RemoveKeyboard
from dff.script.core.message import Button

from bot.api.api_utils import make_prompt
from bot.api.gigachat import get_gigachat_response
from bot.dialog_graph.consts import SLOTS, PERSONAL_INFO, NAME, QUESTION, FORM, CODE, EMAIL, DATE
from bot.api.prompts import INTRO_PROMPT


def gigacht_response(ctx: Context, _: Pipeline) -> TelegramMessage:
    if ctx.validation:
        return TelegramMessage()
    node = ctx.last_label[1]
    prompt = make_prompt(node, ctx)
    text = get_gigachat_response(prompt)
    text = text.replace('"', '')
    return TelegramMessage(text=text)


def nice_t_meet_u_response(ctx: Context, _: Pipeline) -> TelegramMessage:
    if ctx.validation:
        return TelegramMessage()
    name = ctx.misc[SLOTS][PERSONAL_INFO][NAME].capitalize()
    text = f'Приятино познакомиться, {name}) \nКак могу сегодня вам помочь?)'
    return TelegramMessage(text=text)


def say_hi_response(ctx: Context, _: Pipeline) -> TelegramMessage:
    if ctx.validation:
        return TelegramMessage()
    if ctx.last_response is None:
        return TelegramMessage(text=INTRO_PROMPT)
    else:
        return TelegramMessage(text='Представтесь, пожалуйста, для начала')


def mentor_query_response(ctx: Context, _: Pipeline) -> TelegramMessage:
    if (QUESTION in ctx.misc[SLOTS][FORM].keys()) or (CODE in ctx.misc[SLOTS][FORM].keys()):
        return TelegramMessage(text=f'Вы хотите узнать: {ctx.misc[SLOTS][FORM][QUESTION]} Все верно?',
                               ui=TelegramUI(
                                   buttons=[
                                       Button(text="Да"),
                                       Button(text="Нет"),
                                   ],
                                   is_inline=False,
                                   row_width=4
                               )
                               )
    responses = [
        'Отправьте файл с кодом на проверку или сформулируйте вопрос',
        'Пожалуйста, присылайте ваш код для анализа или задайте свой вопрос',
        'Загрузите файл с кодом для рецензии или опишите вашу проблему',
        'Отправьте ваш исходный код для оценки или сформулируйте ваш запрос',
        'Передайте код для проверки или изложите вопрос для обсуждения'
    ]
    selected_text = random.choice(responses)
    return TelegramMessage(text=selected_text)


def question_unsuccess_node(ctx: Context, _: Pipeline) -> TelegramMessage:
    if ctx.last_response.text == 'Нет':
        del ctx.misc[SLOTS][FORM][QUESTION]
    return TelegramMessage(
        **{"text": "Задайте вопрос еще раз или отправьте файл с кодом на проверку", "ui": RemoveKeyboard()}
    )


def mentor_name_response(ctx: Context, _: Pipeline) -> TelegramMessage:
    text = """ Выберете ментора, к кому хотели бы обратиться:
    
1) Елена — опытный наставник в области обработки естественного языка (NLP) с фокусом на создании интеллектуальных диалоговых систем. Она владеет глубокими знаниями в машинном обучении и искусственном интеллекте, что позволяет ей разрабатывать высокоэффективные решения для автоматизации коммуникаций.

Технологии: Python, TensorFlow, PyTorch, BERT, GPT-3, spaCy, NLTK, Scikit-learn.

2) Александра обладает уникальным опытом в NLP и разработке диалоговых систем, сильно акцентируя на использовании последних достижений в области трансформеров и контекстно-зависимых моделей для повышения точности понимания запросов пользователей.

Технологии: Python, PyTorch, Transformers, Hugging Face, Dialogflow, TensorFlow.

"""
    return TelegramMessage(text=text, ui=RemoveKeyboard())


def email_response(ctx: Context, _: Pipeline) -> TelegramMessage:
    if EMAIL in ctx.misc[SLOTS][FORM].keys():
        return TelegramMessage(text=f'Это ваша почта: {ctx.misc[SLOTS][FORM][EMAIL]}', ui=TelegramUI(
                                   buttons=[
                                       Button(text="Да"),
                                       Button(text="Нет"),
                                   ],
                                   is_inline=False,
                                   row_width=4))
    else:
        return TelegramMessage(text='Пожалуйста, предоставьте ваш адрес электронной почты для возможности связи с вами', ui=RemoveKeyboard())


def success_form_response(ctx: Context, _: Pipeline) -> TelegramMessage:
    text = f"""Ваш запрос был успешно принят! Вот детали вашего запроса:
Ментор: {ctx.misc[SLOTS][FORM][NAME]},
Желаемая дата встречи: {ctx.misc[SLOTS][FORM][DATE]},
Контактный email: {ctx.misc[SLOTS][PERSONAL_INFO][EMAIL]},
Вопрос к ментору: {ctx.misc[SLOTS][FORM][QUESTION] if QUESTION in ctx.misc[SLOTS][FORM].keys() else ctx.misc[SLOTS][FORM][CODE]}

Благодарим за ваше обращение! Ваш ментор свяжется с вами в ближайшее время. Мы рады вашему интересу к нашему фреймворку."""

    return TelegramMessage(text=text)


def are_u_sure_nod_response(ctx: Context, _: Pipeline) -> TelegramMessage:
    text = 'Вы уверены, что хотите прервать заполнение формы запроса к ментору?'
    return TelegramMessage(text=text, ui=TelegramUI(
        buttons=[
            Button(text="Да"),
            Button(text="Нет"),
        ],
        is_inline=False,
        row_width=4))