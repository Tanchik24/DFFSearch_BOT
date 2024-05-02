from dff.script import Context
from bot.dialog_graph.consts import INTENTS
from NLU.SlotIntentExtractor import slot_intent_extractor


def extract_intent(ctx: Context):
    if INTENTS not in ctx.misc:
        ctx.misc[INTENTS] = []

    intent = slot_intent_extractor.predict_intent(ctx.last_request.text)
    ctx.misc[INTENTS].append(intent)