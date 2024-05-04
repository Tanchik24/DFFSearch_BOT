import json
import os

from dff.script import Context
import random
from dff.pipeline import Pipeline
from dff.messengers.telegram import TelegramMessage, TelegramUI, RemoveKeyboard
from dff.script.core.message import Button

from NLU.LLM.gigachat_utils import make_prompt
from NLU.LLM.gigachat import get_gigachat_response
from bot.dialog_graph.consts import SLOTS, PERSONAL_INFO, NAME, QUESTION, FORM, CODE, EMAIL, DATE, TRAINING_PROGRESS, \
    TEST_FLAG
from bot.context.intro import INTRO_PROMPT
from RAG.RAGSystem import rag_system


def gigacht_response(ctx: Context, _: Pipeline) -> TelegramMessage:
    if ctx.validation:
        return TelegramMessage()
    node = ctx.last_label[1]
    prompt = make_prompt(node, ctx)
    text = get_gigachat_response(prompt, os.getenv('MODEL'))
    text = text.replace('"', '')
    return TelegramMessage(text=text, ui=TelegramUI(
        buttons=[
            Button(text="Прогресс"),
            Button(text="Пройти тест"),
        ],
        is_inline=False))


def nice_t_meet_u_response(ctx: Context, _: Pipeline) -> TelegramMessage:
    if ctx.validation:
        return TelegramMessage()
    name = ctx.misc[SLOTS][PERSONAL_INFO][NAME].capitalize()
    text = f'Приятино познакомиться, {name}) \nКак могу сегодня вам помочь?)'
    return TelegramMessage(text=text)


def say_hi_response(ctx: Context, _: Pipeline) -> TelegramMessage:
    if ctx.validation:
        return TelegramMessage()
    if ctx.last_request.text == '/start':
        return TelegramMessage(text=INTRO_PROMPT, parse_mode='HTML', ui=TelegramUI(
            buttons=[
                Button(text="Прогресс"),
                Button(text="Пройти тест"),
            ],
            is_inline=False))
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
                                   row_width=2
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
    return TelegramMessage(text=selected_text, ui=RemoveKeyboard())


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

2) Мария обладает уникальным опытом в NLP и разработке диалоговых систем, сильно акцентируя на использовании последних достижений в области трансформеров и контекстно-зависимых моделей для повышения точности понимания запросов пользователей.

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
            is_inline=False))
    else:
        return TelegramMessage(text='Пожалуйста, предоставьте ваш адрес электронной почты для возможности связи с вами',
                               ui=RemoveKeyboard())


def success_form_response(ctx: Context, _: Pipeline) -> TelegramMessage:
    text = f"""Ваш запрос был успешно принят! Вот детали вашего запроса:
Ментор: {ctx.misc[SLOTS][FORM][NAME]},
Желаемая дата встречи: {ctx.misc[SLOTS][FORM][DATE]},
Контактный email: {ctx.misc[SLOTS][PERSONAL_INFO][EMAIL]},
Вопрос к ментору: {ctx.misc[SLOTS][FORM][QUESTION] if QUESTION in ctx.misc[SLOTS][FORM].keys() else ctx.misc[SLOTS][FORM][CODE]}

Благодарим за ваше обращение! Ваш ментор свяжется с вами в ближайшее время. Мы рады вашему интересу к нашему фреймворку."""

    return TelegramMessage(text=text, ui=TelegramUI(
            buttons=[
                Button(text="Прогресс"),
                Button(text="Пройти тест"),
            ],
            is_inline=False))


def are_u_sure_nod_response(ctx: Context, _: Pipeline) -> TelegramMessage:
    text = 'Вы уверены, что хотите прервать заполнение формы запроса к ментору?'
    return TelegramMessage(text=text, ui=TelegramUI(
        buttons=[
            Button(text="Да"),
            Button(text="Нет"),
        ],
        is_inline=False))


def qa_response(ctx: Context, _: Pipeline) -> TelegramMessage:
    text = rag_system.get_answer(ctx.last_request.text, ctx.id)
    return TelegramMessage(text=text, parse_mode='HTML')


def load_data(path):
    try:
        with open(path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print("Документ не найден")
        return None


def get_next_section(data, last_progress):
    chapter_index, parag_index, chapter_name, parag_name = last_progress
    chapters = list(data.keys())
    paragraphs = list(data[chapter_name].keys())

    if parag_index + 1 < len(paragraphs):
        next_parag_index = parag_index + 1
        next_parag_name = paragraphs[next_parag_index]
        return chapter_index, next_parag_index, chapter_name, next_parag_name
    elif chapter_index + 1 < len(chapters):
        next_chapter_index = chapter_index + 1
        next_chapter_name = chapters[next_chapter_index]
        next_parag_name = list(data[next_chapter_name].keys())[0]
        return next_chapter_index, 0, next_chapter_name, next_parag_name
    else:
        return None


def training_session_response(ctx: Context, _: Pipeline) -> TelegramMessage:
    path = 'content/documenation.json'
    data = load_data(path)
    if data is None:
        return TelegramMessage(text="Ошибка: обновите меня, пожалуйста")
    last_progress = ctx.misc[SLOTS][TRAINING_PROGRESS]['last']

    if not last_progress:
        text = f'{data["getting_started"]["Installation"]}'
        ctx.misc[SLOTS][TRAINING_PROGRESS]['getting_started']['Installation'] = True
        ctx.misc[SLOTS][TRAINING_PROGRESS]['last'] = (0, 0, 'getting_started', 'Installation')
    else:
        next_section = get_next_section(data, last_progress)
        if next_section:
            chapter_index, parag_index, chapter_name, parag_name = next_section
            text = f'Сегодня мы разбираем: {chapter_name}, {parag_name} \n\n {data[chapter_name][parag_name]}'
            ctx.misc[SLOTS][TRAINING_PROGRESS]['last'] = next_section
            ctx.misc[SLOTS][TRAINING_PROGRESS][chapter_name][parag_name] = True
        else:
            text = "Вы завершили все разделы обучения."
    return TelegramMessage(text=text, parse_mode='HTML', ui=TelegramUI(
        buttons=[
            Button(text="Дальше"),
            Button(text="Закончить обучение"),
        ],
        is_inline=False))


def generate_progress_response(ctx: Context, _: Pipeline) -> TelegramMessage:
    message = "<b>Ваш прогресс по курсу:</b>\n\n"
    progress = ctx.misc[SLOTS][TRAINING_PROGRESS]
    for section, chapters in progress.items():
        if type(chapters) is dict:
            message += f"\n<b>{section}:</b>\n"
            for chapter, completed in chapters.items():
                status = "✅ Пройдено" if completed else "❌ Не пройдено"
                message += f"- {chapter}: {status}\n"
    return TelegramMessage(text=message, parse_mode='HTML')


def list_fully_completed_chapters(progress_dict):
    completed_chapters = []
    for section, chapters in progress_dict.items():
        if isinstance(chapters, dict):
            if all(chapters.values()):
                completed_chapters.append(section)
    return completed_chapters


def test_start_response(ctx: Context, _: Pipeline) -> TelegramMessage:
    completed_chapters = list_fully_completed_chapters(ctx.misc[SLOTS][TRAINING_PROGRESS])
    if not completed_chapters:
        return TelegramMessage(text='Извините, но сейчас вам не доступен ни один тест. Вы не прошли ни одной главы')
    buttons = [Button(text=chapter) for chapter in completed_chapters]
    return TelegramMessage(
        text="Сейчас вы пожете пройти тест по следующим параграфам:",
        parse_mode='HTML',
        ui=TelegramUI(
            buttons=buttons,
            is_inline=False,
            row_width=2
        )
    )


def process_test_response(ctx: Context, _: Pipeline) -> TelegramMessage:
    if 'test_info' not in ctx.misc[SLOTS]['test']:
        data = load_data('content/test.json')
        if ctx.last_request.text in data:
            data = data[ctx.last_request.text]
            ctx.misc[SLOTS]['test']['test_info'] = data
        else:
            return TelegramMessage()

    if len(ctx.misc[SLOTS]['test']['test_info']) == 0:
        ctx.misc[SLOTS][TEST_FLAG] = False
        return TelegramMessage(text='Тест окончен, проверяем результаты! Готовы узнать, результаты?',
                               ui=RemoveKeyboard())

    question = ctx.misc[SLOTS]['test']['test_info'][0]['формулировка вопроса']
    answers = ctx.misc[SLOTS]['test']['test_info'][0]['варианты ответа']
    true_answer = ctx.misc[SLOTS]['test']['test_info'][0]['правильный ответ']

    if 'user_answers' not in ctx.misc[SLOTS]['test']:
        ctx.misc[SLOTS]['test']['user_answers'] = []
    if 'test_answers' not in ctx.misc[SLOTS]:
        ctx.misc[SLOTS]['test']['test_answers'] = []

    ctx.misc[SLOTS]['test']['test_answers'].append(true_answer)

    ctx.misc[SLOTS]['test']['test_info'].pop(0)

    buttons = [Button(text=answer) for answer in answers]

    return TelegramMessage(
        text=f"<b>Вопрос:</b>\n{question}",
        parse_mode='HTML',
        ui=TelegramUI(
            buttons=buttons,
            is_inline=False,
        )
    )


def result_node_response(ctx: Context, _: Pipeline) -> TelegramMessage:
    correct_answers = ctx.misc[SLOTS]['test']['test_answers']
    user_answers = ctx.misc[SLOTS]['test']['user_answers']

    correct_count = 0
    result_display = "Ваши ответы и правильные ответы:\n\n"

    for question_index, correct_answer in enumerate(correct_answers, start=1):
        user_answer = user_answers[question_index - 1]
        if correct_answer == user_answer:
            correct_count += 1
        result_display += f"Вопрос {question_index}:\nВаш ответ: {user_answer}\nПравильный ответ: {correct_answer}\n\n"

    result_display += f"Итог: Вы ответили правильно на {correct_count} из {len(correct_answers)} вопросов."
    return TelegramMessage(result_display)
