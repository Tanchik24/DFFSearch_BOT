import re
from bot.api.prompts import FALLBACK_PROMPT, TELL_ABOUT_BOT, QUESTION_CODE_PROMPT
from dff.script import Context

prompts_dict = {
    'fallback_node': FALLBACK_PROMPT,
    'tell_about_bot_node': TELL_ABOUT_BOT,
    'mentor_query': QUESTION_CODE_PROMPT
}


def extract_parameters(template) -> set:
    pattern = re.compile(r'{(\w+)}')
    return set(match.group(1) for match in pattern.finditer(template))


def sort_key(item):
    parts = item.split('_')
    return int(parts[1])


def make_prompt(node: str, ctx: Context) -> str:
    if node in ['tell_about_bot_node', 'mentor_query_node']:
        prompt = prompts_dict[node]
        return prompt.format(utterance_1=ctx.last_request.text)

    parameters = extract_parameters(prompts_dict[node])
    last_three_user_messages, last_two_bot_messages = extract_messages(ctx)
    prompt = prompts_dict[node]
    kwargs = {}
    for param in parameters:
        param_type, param_index = param.split('_')
        index = int(param_index) - 1
        try:
            if param_type == 'utterance':
                kwargs[param] = last_three_user_messages[index].text
            elif param_type == 'response':
                kwargs[param] = last_two_bot_messages[index].text
        except IndexError:
            prompt = prompt.replace(f"""Ответ бота: '{{{param}}}'""", '')
            prompt = prompt.replace(f"""Сообщение пользователя: '{{{param}}}'""", '')

    return prompt.format(**kwargs)


def extract_messages(ctx):
    user_messages = list(ctx.requests.values())

    bot_messages = list(ctx.responses.values())

    last_three_user_messages = user_messages[-3:]

    last_two_bot_messages = bot_messages[-2:]

    return last_three_user_messages, last_two_bot_messages
