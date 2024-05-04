import pytest
from dff.utils.testing.common import check_happy_path
from dff.messengers.telegram import TelegramMessage
from dff.script import RESPONSE, Message

from bot.dialog_graph.script import script
from main import pipeline


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "happy_path",
    [
        (
            (TelegramMessage(text="/start"), script["general_flow"]["say_hi_node"][RESPONSE]),
            (TelegramMessage(text="Татьяна"), script["general_flow"]["ntmu_node"][RESPONSE]),
        )
    ],
)
async def test_happy_path(happy_path):
    check_happy_path(pipeline=pipeline, happy_path=happy_path)