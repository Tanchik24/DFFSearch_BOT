from dff.pipeline import Pipeline
from dff.messengers.telegram import (
    PollingTelegramInterface,
)
from dff.utils.testing.common import is_interactive_mode
from bot.dialog_graph.script import script
from bot.dialog_graph.processing import extract_intent

token = '7070813843:AAGSGMx98L9l034aCsQ2X54EbLVkWu37RxM'
interface = PollingTelegramInterface(token)

pipeline = Pipeline.from_script(
    script=script,
    start_label=("general_flow", "start_node"),
    fallback_label=("general_flow", "fallback_node"),
    messenger_interface=interface,
    pre_services=[extract_intent]
)


def main():
    pipeline.run()


if __name__ == "__main__" and is_interactive_mode():
    main()