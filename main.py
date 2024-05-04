import logging
import os

from dff.pipeline import Pipeline
from dff.script import Context
from bot.dialog_graph.consts import STORAGE, SLOTS, FORM, CODE
from dff.messengers.telegram import (
    PollingTelegramInterface,
)
from dff.utils.testing.common import is_interactive_mode
from bot.dialog_graph.script import script
from bot.dialog_graph.processing import extract_intent, make_all_slots_field, \
    extract_names, extract_question_code, extract_slots, stats
from db_connection import db

token = os.getenv('BOT_TOLEN')
interface = PollingTelegramInterface(token)


def extract_data(ctx: Context, _: Pipeline):
    update = ctx.last_request.update
    if update.content_type is None:
        return

    if not (update.document and update.document.mime_type in ["text/x-python", "text/x-script.phyton"]):
        return

    ctx.misc[STORAGE].append(0 if not ctx.misc[STORAGE] else ctx.misc[STORAGE][-1] + 1)
    ctx.misc[SLOTS][FORM][CODE] = 'attached file'

    python_file = update.document
    file_id = python_file.file_id
    file_info = interface.messenger.get_file(file_id)

    file_data = interface.messenger.download_file(file_info.file_path)
    with open(f"./users_code/{ctx.id}_{ctx.misc[STORAGE][-1]}.py", "wb+") as file:
        file.write(file_data)

    logging.info(f'Downloaded file: -- {file_id} --')


def get_pipeline():
    pipeline = Pipeline.from_script(
        script=script,
        start_label=("general_flow", "start_node"),
        fallback_label=("general_flow", "chitchat_node"),
        messenger_interface=interface,
        context_storage=db,
        pre_services=[make_all_slots_field, extract_intent,
                      extract_data,
                      extract_names, extract_question_code,
                      extract_slots],
        post_services=[stats]
    )
    return pipeline


def main():
    get_pipeline().run()


if __name__ == "__main__" and is_interactive_mode():
    main()
