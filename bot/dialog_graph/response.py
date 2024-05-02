from dff.script import Context
from dff.pipeline import Pipeline
from dff.messengers.telegram import TelegramMessage

from bot.api.api_utils import make_prompt
from bot.api.gigachat import get_gigachat_response


def gigacht_response(ctx: Context, _: Pipeline) -> TelegramMessage:
    if ctx.validation:
        return TelegramMessage()
    node = ctx.last_label[1]
    prompt = make_prompt(node, ctx)
    text = get_gigachat_response(prompt)
    text = text.replace('"', '')
    return TelegramMessage(text=text)
