from pymystem3 import Mystem


class NameExtractor:
    def __init__(self):
        self.m = Mystem()

    def predict_names(self, text):
        if text is None:
            return None, None, None
        analyze = self.m.analyze(text)
        first_name = None
        second_name = None
        middle_name = None

        for word in analyze:
            try:
                try:
                    analysis = word['analysis'][0]
                except KeyError:
                    continue
            except IndexError:
                continue

            if 'имя' in analysis['gr']:
                first_name = word['text'].lower()
            elif 'фам' in analysis['gr']:
                second_name = word['text'].lower()
            elif 'отч' in analysis['gr']:
                middle_name = word['text'].lower()

        return second_name, first_name, middle_name


name_extractor = NameExtractor()
