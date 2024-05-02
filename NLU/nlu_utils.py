from NLU.NameExtractor import name_extractor


def get_name(message: str) -> str:
    full_name = name_extractor.predict_names(message)
    name = None

    for elem in full_name:
        if elem:
            if name is None:
                name = ''
            name += elem + ' '

    if name is not None:
        name = name.strip()
    return name
