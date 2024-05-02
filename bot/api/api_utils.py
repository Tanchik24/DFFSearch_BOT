import re
from bot.api.prompts.fallback import FALLBACK_PROMPT
from dff.script import Context

prompts_dict = {
    'fallback_node': FALLBACK_PROMPT
}


def extract_parameters(template) -> set:
    pattern = re.compile(r'{(\w+)}')
    return set(match.group(1) for match in pattern.finditer(template))


def make_prompt(node: str, ctx: Context) -> str:
    parameters = extract_parameters(prompts_dict[node])
    kwargs = {}
    for param in parameters:
        param_type, param_index = param.split('_')
        index = (-1) * int(param_index)
        if param_type == 'utterance':
            kwargs[param] = ctx.requests[list(ctx.requests.keys())[index]]
        elif param_type == 'response':
            kwargs[param] = ctx.responses[list(ctx.requests.keys())[index]]
    return prompts_dict[node].format(**kwargs)