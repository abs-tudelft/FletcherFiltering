from tests.data_generation.BaseGenerator import BaseGenerator
import lipsum
from fletcherfiltering import settings
import math

class SentenceGenerator(BaseGenerator):

    def generate(self, maxlength: int = settings.VAR_LENGTH) -> str:
        sentence = lipsum.generate_sentences(1)
        if len(sentence) > maxlength:
            indexes = [pos for pos, char in enumerate(sentence) if char == ' ' and pos < maxlength]
            if len(indexes) == 0:
                sentence = sentence[:maxlength]
            else:
                sentence = sentence[:indexes[-1]]
        return sentence
