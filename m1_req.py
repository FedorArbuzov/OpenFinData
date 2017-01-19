import re
import constants
import data
from data import NEURO_KEY_WORDS as WORDS
# from db_creation import Parameter, Tag
import datetime
import random as rng


class DataParser:
    def __init__(self, using_db=False):
        self.using_db = using_db

    def _collect_all_key_words(self):
        all_words = []

        if not self.using_db:
            all_words = list(WORDS['extra']) + list(data.SUBJECT.keys()) + \
                        list(data.TYPES.keys()) + list(data.NALOG_NENALOG.keys()) + \
                        list(data.SPHERES.keys()) + list(data.PLACES.keys())
            all_words = list(filter(lambda x: x != 'null', all_words))
        # else:
        #     for tv in Parameter.select(Parameter.tagValue):
        #         all_words.append(tv.tagValue)
        #
        #     for t in Tag.select(Tag.tag):
        #         all_words.append(t.tag)
        #
        #     all_words = list(filter(lambda x: x != 'null' and x is not None, all_words))

        return all_words

    @staticmethod
    def _represents_int(s):
        try:
            int(s)
            return True
        except ValueError:
            return False

    @staticmethod
    def _simple_split(s):
        s = s.lower()
        s = re.sub(r'[^\w\s]', '', s)
        return s.split()

    @staticmethod
    def hello_back(s):
        for _ in DataParser._simple_split(s):
            if _ in constants.HELLO:
                return constants.HELLO_ANSWER[rng.randint(0, len(constants.HELLO_ANSWER) - 1)]
            elif _ in constants.HOW_ARE_YOU:
                return constants.HOW_ARE_YOU_ANSWER[rng.randint(0, len(constants.HOW_ARE_YOU_ANSWER) - 1)]

    # Adaptive allowable mistake for distance between user word and key word
    @staticmethod
    def _allowable_error(word):
        allowable_inaccuracy = {
            1: 0, 2: 0, 3: 1, 4: 2,
            5: 2, 6: 3, 7: 3, 8: 3,
            9: 4, 10: 5, 11: 5, 12: 5,
            13: 5, 14: 5, 15: 6, 16: 6,
            17: 6, 18: 6, 19: 6, 20: 6
        }

        length = len(word)
        if length > 20:
            return 6

        return allowable_inaccuracy[length]

    # the Levenstein distance algorithm
    @staticmethod
    def distance(a: object, b: object) -> object:
        """Calculates the Levenshtein distance between a and b."""
        n, m = len(a), len(b)
        if n > m:
            # Make sure n <= m, to use O(min(n,m)) space
            a, b = b, a
            n, m = m, n

        current_row = range(n + 1)  # Keep current and previous row, not entire matrix
        for i in range(1, m + 1):
            previous_row, current_row = current_row, [i] + [0] * n
            for j in range(1, n + 1):
                add, delete, change = previous_row[j] + 1, current_row[j - 1] + 1, previous_row[j - 1]
                if a[j - 1] != b[i - 1]:
                    change += 1
                current_row[j] = min(add, delete, change)

        return current_row[n]

    # return index of possible key word
    def _find_similar_word(self, str_user):
        all_words = self._collect_all_key_words()
        minimum_value = len(all_words)
        index_of_the_most_likely_variant = 0
        i = 0

        for _ in all_words:
            distance_between_input_and_table_data = DataParser.distance(str_user, all_words[i])
            if (distance_between_input_and_table_data < minimum_value and
                        distance_between_input_and_table_data <= DataParser._allowable_error(str_user)):
                minimum_value = distance_between_input_and_table_data
                index_of_the_most_likely_variant = i
            i += 1

        return all_words[index_of_the_most_likely_variant]

    # parse the string into affordable form for Module 2
    def main_func(self, s):
        s = re.sub(r'[^\w\s]', '', s)
        words = s.split()

        list_of_int = []

        for i in range(len(words)):
            if DataParser._represents_int(words[i]):
                list_of_int.append(words[i])

        words = list(filter(lambda x: x not in constants.USELESS_PILE_OF_CRAP, words))

        for s in list_of_int:
            if s in words:
                words.remove(s)

        user_req = Result()

        now_date = datetime.date.today()

        if not self.using_db:
            territories = list(filter(lambda x: x != 'null', data.PLACES.keys()))
            spheres = list(filter(lambda x: x != 'null', data.SPHERES.keys()))
            subjects = data.SUBJECT.keys()
            types = list(filter(lambda x: x != 'null', data.TYPES.keys()))
            sectors = data.NALOG_NENALOG.keys()
        # else:
        #     territories = []
        #     for t in Parameter.select(Parameter.tagValue).where(Parameter.type == 1):
        #         territories.append(t.tagValue)
        #
        #     spheres = []
        #     for s in Parameter.select(Parameter.tagValue).where(Parameter.type == 3):
        #         spheres.append(s.tagValue)
        #     spheres = list(filter(lambda x: x != 'null', spheres))
        #
        #     subjects = []
        #     for t in Tag.select(Tag.tag):
        #         subjects.append(t.tag)
        #
        #     types = []
        #     for p in Parameter.select(Parameter.tagValue) \
        #             .where((Parameter.type == 4) | (Parameter.type == 5) | (Parameter.type == 6)):
        #         types.append(p.tagValue)
        #
        #     sectors = []
        #     for s in Parameter.select(Parameter.tagValue).where(Parameter.type == 7):
        #         sectors.append(s.tagValue)

        for i in range(len(words)):
            result = self._find_similar_word(words[i])

            if result == 'прошлый':
                user_req.year = now_date.year - 1
                continue

            if result in subjects:
                # if result == 'профицит' or result == 'дефицит':
                #     user_req.subject = 'профицит/дефицит'
                # else:
                user_req.subject = result
                continue

            if result in types:
                user_req.planned_or_actual = result
                continue

            if result in sectors:
                user_req.sector = result
                continue

            if result in territories:
                user_req.place = result
                continue

            if result in spheres:
                user_req.sector = result
                continue

        if user_req.sector == "":
            user_req.sector = "null"
        if user_req.planned_or_actual == "":
            user_req.planned_or_actual = "null"
        if user_req.place == "":
            user_req.place = "null"

        if user_req.year == 0 or user_req.year == now_date.year:
            if len(list_of_int) != 0:
                user_req.year = int(list_of_int[0])
            else:
                user_req.year = "null"

        user_r = [user_req.subject, user_req.place.lower(), user_req.year, user_req.sector, user_req.planned_or_actual]
        return user_r


class Result:
    subject = ""
    place = ""
    year = 0
    sector = ""
    planned_or_actual = ""
