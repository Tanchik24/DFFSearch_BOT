from NLU.NameExtractor import name_extractor
import pymorphy2


def get_name(message: str) -> str:
    full_name = name_extractor.predict_names(message)
    morph = pymorphy2.MorphAnalyzer()
    name = None

    for elem in full_name:
        if elem:
            if name is None:
                name = ''
            name += elem + ' '

    if name is not None:
        name = name.strip()
        name = morph.parse(name)[0]
        name = name.normal_form
        name = name.capitalize()
    return name

