from dff.script import RESPONSE, TRANSITIONS, PRE_TRANSITIONS_PROCESSING
from dff.messengers.telegram import (
    telegram_condition,
    TelegramMessage)

from bot.dialog_graph.response import gigacht_response
from bot.api.prompts import INTRO_PROMPT

script = {
    'general_flow': {
        "start_node": {
            RESPONSE: TelegramMessage(),
            TRANSITIONS: {('general_flow', 'say_hi_node'): telegram_condition(commands=["start", "restart"])}
        },

        "say_hi_node": {
            RESPONSE: TelegramMessage(text=INTRO_PROMPT)
        },

        "fallback_node": {
            RESPONSE: gigacht_response
        },
    },
}
