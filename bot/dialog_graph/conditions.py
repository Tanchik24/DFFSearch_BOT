from typing import Callable
from bot.dialog_graph.consts import INTENTS, SLOTS, NAME, FORM
from dff.script import Context
from dff.pipeline import Pipeline


def is_intent_match(true_intents: list) -> Callable:
    def is_intent_match_inner(ctx: Context, _: Pipeline) -> bool:
        intent = ctx.misc[INTENTS][-1]
        return intent in true_intents

    return is_intent_match_inner


def is_slots_filled(slot_field: str, slot_name: str) -> Callable:
    def is_slots_filled_inner(ctx: Context, _: Pipeline) -> bool:
        if ctx.validation:
            return False
        if slot_name not in ctx.misc[SLOTS][slot_field]:
            return False
        slot = ctx.misc[SLOTS][slot_field][slot_name]
        return slot is not None

    return is_slots_filled_inner


def is_name_exist() -> Callable:
    def is_name_exist_inner(ctx: Context, _: Pipeline) -> bool:
        if ctx.validation:
            return False

        if NAME not in list(ctx.misc[SLOTS][FORM].keys()):
            return False

        names = ['Елена', 'Александр']
        if ctx.misc[SLOTS][FORM][NAME] in names:
            return True
        return False
    return is_name_exist_inner

