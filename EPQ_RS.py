import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from data_saver import DataSaver
from base_window import FullscreenMixin


class EPQRSFuzzySystem:

    def __init__(self):
        self.setup_system()

    def trap_mf(self, x, a, b, c, d):
        if x <= a:
            return 0
        elif a < x < b:
            return (x - a) / (b - a)
        elif b <= x <= c:
            return 1
        elif c < x < d:
            return (d - x) / (d - c)
        else:
            return 0

    def linsmf(self, x, a, b):
        if x <= a:
            return 0
        elif x >= b:
            return 1
        else:
            return (x - a) / (b - a)

    def linzmf(self, x, a, b):
        if x <= a:
            return 1
        elif x >= b:
            return 0
        else:
            return (b - x) / (b - a)

    def fuzzify(self, value, mfs):
        return {name: mf(value) for name, mf in mfs.items()}

    def get_membership_with_not(self, inputs_fuzzy, input_name, term_idx):
        if term_idx == 0:
            return 1.0
        elif term_idx > 0:
            term_names = list(inputs_fuzzy[input_name].keys())
            if term_idx - 1 < len(term_names):
                term = term_names[term_idx - 1]
                return inputs_fuzzy[input_name][term]
            return 0.0
        else:
            term_names = list(inputs_fuzzy[input_name].keys())
            abs_idx = abs(term_idx)
            if abs_idx - 1 < len(term_names):
                term = term_names[abs_idx - 1]
                return 1.0 - inputs_fuzzy[input_name][term]
            return 1.0

    def evaluate_rules(self, inputs_fuzzy, rules, output_range, output_mfs):
        output_values = []
        for x in output_range:
            rule_activations = []
            for rule in rules:
                input_indices = rule[:-1]
                output_idx = rule[-1]
                activation = 1.0
                for i, idx in enumerate(input_indices):
                    if i >= len(list(inputs_fuzzy.keys())):
                        continue
                    if idx == 0:
                        continue
                    input_name = list(inputs_fuzzy.keys())[i]
                    membership = self.get_membership_with_not(inputs_fuzzy, input_name, idx)
                    activation = min(activation, membership)
                if output_idx > 0 and output_idx - 1 < len(output_mfs):
                    out_term_name = list(output_mfs.keys())[output_idx - 1]
                    out_membership = output_mfs[out_term_name](x)
                    rule_activation = min(activation, out_membership)
                    rule_activations.append(rule_activation)
            if rule_activations:
                output_values.append(max(rule_activations))
            else:
                output_values.append(0)
        numerator = sum(x * y for x, y in zip(output_range, output_values))
        denominator = sum(output_values)
        return numerator / denominator if denominator != 0 else 0

    def setup_system(self):
        # ШКАЛА ЭКСТРАВЕРСИЯ-ИНТРОВЕРСИЯ
        self.e_inputs = {
            'extraversion': {'range': [0, 100], 'mfs': {}}
        }
        self.e_inputs['extraversion']['mfs']['strong_introvert'] = lambda x: self.linzmf(x, 16.6, 25)
        self.e_inputs['extraversion']['mfs']['introvert'] = lambda x: self.trap_mf(x, 16.6, 25, 33.3, 41.7)
        self.e_inputs['extraversion']['mfs']['ambivert'] = lambda x: self.trap_mf(x, 33.3, 41.7, 66.7, 75)
        self.e_inputs['extraversion']['mfs']['extravert'] = lambda x: self.trap_mf(x,66.7,75, 83.3, 91.7)
        self.e_inputs['extraversion']['mfs']['strong_extravert'] = lambda x: self.linsmf(x, 83.3, 100)

        # ШКАЛА НЕЙРОТИЗМ
        self.n_inputs = {
            'neuroticism': {'range': [0, 100], 'mfs': {}}
        }
        self.n_inputs['neuroticism']['mfs']['low'] = lambda x: self.linzmf(x, 50, 58.3)
        self.n_inputs['neuroticism']['mfs']['average'] = lambda x: self.trap_mf(x, 29.2, 50, 54.2, 62.5)
        self.n_inputs['neuroticism']['mfs']['high'] = lambda x: self.trap_mf(x, 54.2, 58.3, 75, 79.2)
        self.n_inputs['neuroticism']['mfs']['very_high'] = lambda x: self.linsmf(x, 75, 79.2)

        # ШКАЛА ПСИХОТИЗМ
        self.p_inputs = {
            'psychoticism': {'range': [0, 100], 'mfs': {}}
        }
        self.p_inputs['psychoticism']['mfs']['low'] = lambda x: self.linzmf(x, 8.3, 16.7)
        self.p_inputs['psychoticism']['mfs']['average'] = lambda x: self.trap_mf(x, 8.3, 16.7, 58.3, 66.7)
        self.p_inputs['psychoticism']['mfs']['high'] = lambda x: self.linsmf(x, 58.3, 66.7)

        # ШКАЛА ИСКРЕННОСТЬ
        self.l_inputs = {
            'lie': {'range': [0, 100], 'mfs': {}}
        }
        self.l_inputs['lie']['mfs']['low'] = lambda x: self.linzmf(x, 8.3, 16.7)
        self.l_inputs['lie']['mfs']['average'] = lambda x: self.trap_mf(x, 8.3, 16.7, 50, 58.3)
        self.l_inputs['lie']['mfs']['high'] = lambda x: self.linsmf(x, 50, 58.3)
        # ВЫХОДНАЯ ПЕРЕМЕННАЯ
        self.output_range = np.arange(0, 101, 1)
        self.output_mfs = {}
        self.output_mfs['low'] = lambda x: self.linzmf(x, 16.6, 25)
        self.output_mfs['middle'] = lambda x: self.trap_mf(x, 16.6, 25, 33.3, 41.7)
        self.output_mfs['elevated'] = lambda x: self.trap_mf(x, 33.3, 41.7, 58.3, 66.7)
        self.output_mfs['high'] = lambda x: self.trap_mf(x, 58.3, 66.7, 75, 83.3)
        self.output_mfs['very_high'] = lambda x: self.linsmf(x, 83.3, 100)

        #ПРАВИЛА
        self.rules = [
            # P=1 (НИЗКИЙ ПСИХОТИЗМ)
            (1, 1, 1, 1, 1), (1, 2, 1, 1, 1), (1, 3, 1, 1, 1), (1, 4, 1, 1, 1),
            (2, 1, 1, 1, 1), (2, 2, 1, 1, 1), (2, 3, 1, 1, 1), (2, 4, 1, 1, 1),
            (3, 1, 1, 1, 1), (3, 2, 1, 1, 1), (3, 3, 1, 1, 1), (3, 4, 1, 1, 1),
            (4, 1, 1, 1, 1), (4, 2, 1, 1, 1), (4, 3, 1, 1, 1), (4, 4, 1, 1, 2),
            (5, 1, 1, 1, 1), (5, 2, 1, 1, 1), (5, 3, 1, 1, 2), (5, 4, 1, 1, 2),
            (1, 1, 1, 2, 1), (1, 2, 1, 2, 1), (1, 3, 1, 2, 1), (1, 4, 1, 2, 1),
            (2, 1, 1, 2, 1), (2, 2, 1, 2, 1), (2, 3, 1, 2, 1), (2, 4, 1, 2, 2),
            (3, 1, 1, 2, 1), (3, 2, 1, 2, 1), (3, 3, 1, 2, 2), (3, 4, 1, 2, 2),
            (4, 1, 1, 2, 1), (4, 2, 1, 2, 2), (4, 3, 1, 2, 2), (4, 4, 1, 2, 2),
            (5, 1, 1, 2, 1), (5, 2, 1, 2, 2), (5, 3, 1, 2, 2), (5, 4, 1, 2, 3),
            (1, 1, 1, 3, 1), (1, 2, 1, 3, 1), (1, 3, 1, 3, 1), (1, 4, 1, 3, 2),
            (2, 1, 1, 3, 1), (2, 2, 1, 3, 1), (2, 3, 1, 3, 2), (2, 4, 1, 3, 2),
            (3, 1, 1, 3, 1), (3, 2, 1, 3, 2), (3, 3, 1, 3, 2), (3, 4, 1, 3, 2),
            (4, 1, 1, 3, 2), (4, 2, 1, 3, 2), (4, 3, 1, 3, 3), (4, 4, 1, 3, 3),
            (5, 1, 1, 3, 2), (5, 2, 1, 3, 2), (5, 3, 1, 3, 3), (5, 4, 1, 3, 3),
            # P=2 (СРЕДНИЙ ПСИХОТИЗМ)
            (1, 1, 2, 1, 2), (1, 2, 2, 1, 2), (1, 3, 2, 1, 2), (1, 4, 2, 1, 2),
            (2, 1, 2, 1, 2), (2, 2, 2, 1, 2), (2, 3, 2, 1, 2), (2, 4, 2, 1, 3),
            (3, 1, 2, 1, 2), (3, 2, 2, 1, 2), (3, 3, 2, 1, 3), (3, 4, 2, 1, 3),
            (4, 1, 2, 1, 2), (4, 2, 2, 1, 3), (4, 3, 2, 1, 3), (4, 4, 2, 1, 3),
            (5, 1, 2, 1, 2), (5, 2, 2, 1, 3), (5, 3, 2, 1, 3), (5, 4, 2, 1, 4),
            (1, 1, 2, 2, 2), (1, 2, 2, 2, 2), (1, 3, 2, 2, 2), (1, 4, 2, 2, 3),
            (2, 1, 2, 2, 2), (2, 2, 2, 2, 2), (2, 3, 2, 2, 3), (2, 4, 2, 2, 3),
            (3, 1, 2, 2, 2), (3, 2, 2, 2, 3), (3, 3, 2, 2, 3), (3, 4, 2, 2, 3),
            (4, 1, 2, 2, 3), (4, 2, 2, 2, 3), (4, 3, 2, 2, 4), (4, 4, 2, 2, 4),
            (5, 1, 2, 2, 3), (5, 2, 2, 2, 3), (5, 3, 2, 2, 4), (5, 4, 2, 2, 4),
            (1, 1, 2, 3, 2), (1, 2, 2, 3, 2), (1, 3, 2, 3, 3), (1, 4, 2, 3, 3),
            (2, 1, 2, 3, 2), (2, 2, 2, 3, 3), (2, 3, 2, 3, 3), (2, 4, 2, 3, 3),
            (3, 1, 2, 3, 3), (3, 2, 2, 3, 3), (3, 3, 2, 3, 4), (3, 4, 2, 3, 4),
            (4, 1, 2, 3, 3), (4, 2, 2, 3, 4), (4, 3, 2, 3, 4), (4, 4, 2, 3, 4),
            (5, 1, 2, 3, 3), (5, 2, 2, 3, 4), (5, 3, 2, 3, 4), (5, 4, 2, 3, 4),
            # P=3 (ВЫСОКИЙ ПСИХОТИЗМ)
            (1, 1, 3, 1, 3), (1, 2, 3, 1, 3), (1, 3, 3, 1, 3), (1, 4, 3, 1, 4),
            (2, 1, 3, 1, 3), (2, 2, 3, 1, 3), (2, 3, 3, 1, 4), (2, 4, 3, 1, 4),
            (3, 1, 3, 1, 3), (3, 2, 3, 1, 4), (3, 3, 3, 1, 4), (3, 4, 3, 1, 4),
            (4, 1, 3, 1, 4), (4, 2, 3, 1, 4), (4, 3, 3, 1, 5), (4, 4, 3, 1, 5),
            (5, 1, 3, 1, 4), (5, 2, 3, 1, 4), (5, 3, 3, 1, 5), (5, 4, 3, 1, 5),
            (1, 1, 3, 2, 3), (1, 2, 3, 2, 3), (1, 3, 3, 2, 4), (1, 4, 3, 2, 4),
            (2, 1, 3, 2, 3), (2, 2, 3, 2, 4), (2, 3, 3, 2, 4), (2, 4, 3, 2, 4),
            (3, 1, 3, 2, 4), (3, 2, 3, 2, 4), (3, 3, 3, 2, 5), (3, 4, 3, 2, 5),
            (4, 1, 3, 2, 4), (4, 2, 3, 2, 5), (4, 3, 3, 2, 5), (4, 4, 3, 2, 5),
            (5, 1, 3, 2, 5), (5, 2, 3, 2, 5), (5, 3, 3, 2, 5), (5, 4, 3, 2, 5),
            (1, 1, 3, 3, 4), (1, 2, 3, 3, 4), (1, 3, 3, 3, 4), (1, 4, 3, 3, 5),
            (2, 1, 3, 3, 4), (2, 2, 3, 3, 4), (2, 3, 3, 3, 5), (2, 4, 3, 3, 5),
            (3, 1, 3, 3, 4), (3, 2, 3, 3, 5), (3, 3, 3, 3, 5), (3, 4, 3, 3, 5),
            (4, 1, 3, 3, 5), (4, 2, 3, 3, 5), (4, 3, 3, 3, 5), (4, 4, 3, 3, 5),
            (5, 1, 3, 3, 5), (5, 2, 3, 3, 5), (5, 3, 3, 3, 5), (5, 4, 3, 3, 5)
        ]

    def calculate_deviance(self, extraversion, neuroticism, psychoticism, lie):
        inputs_fuzzy = {
            'extraversion': self.fuzzify(extraversion, self.e_inputs['extraversion']['mfs']),
            'neuroticism': self.fuzzify(neuroticism, self.n_inputs['neuroticism']['mfs']),
            'psychoticism': self.fuzzify(psychoticism, self.p_inputs['psychoticism']['mfs']),
            'lie': self.fuzzify(lie, self.l_inputs['lie']['mfs'])
        }
        return self.evaluate_rules(inputs_fuzzy, self.rules, self.output_range, self.output_mfs)




class EPQRSTest:

    def __init__(self):
        self.questions = [
            "1. Часто ли у вас бывают спады и подъемы настроения?",
            "2. Обращаете ли вы внимание на мнения других людей?",
            "3. Вы разговорчивый человек?",
            "4. Если вы обещаете что-нибудь сделать, всегда ли сдерживаете свои обещания невзирая на то, что это может быть для вас неудобно?",
            "5. Часто ли вы чувствуете себя несчастным человеком без достаточных на это причин?",
            "6. Вас беспокоило бы то, что вы залезли в долги?",
            "7. Считаете ли себя человеком живым и веселым?",
            "8. Случалось ли вам жадничать, стремясь получить больше, чем вам полагалось?",
            "9. Раздражительны ли вы?",
            "10. Стали бы вы принимать средства, которые могут привести вас в необычное или опасное состояние (алкоголь, наркотики)?",
            "11. Вам нравится знакомиться с новыми людьми?",
            "12. Вы когда-нибудь обвиняли кого-нибудь в том, в чем на самом деле были виноваты вы сами?",
            "13. Легко ли вас обидеть?",
            "14. Вы скорее предпочтете сделать всё по-своему, чем следовать правилам?",
            "15. Способны ли вы дать волю своим чувствам и вовсю повеселиться в компании?",
            "16. Считаете ли вы все свои привычки хорошими?",
            "17. Часто ли вам что-нибудь так надоедает, что вы чувствуете себя «сытым по горло»?",
            "18. Для вас много значат хорошие манеры и чистоплотность?",
            "19. При знакомстве вы обычно первым проявляете инициативу?",
            "20. Вам случалось брать вещи, принадлежащие другому лицу, будь это даже такая мелочь, как булавка или пуговица?",
            "21. Можете ли вы назвать себя нервным человеком?",
            "22. Считаете ли вы, что брак старомоден, и его следует отменить?",
            "23. Легко ли вам внести оживление в довольно скучную компанию?",
            "24. Вам случалось сломать или потерять чужую вещь?",
            "25. Вы беспокойный человек?",
            "26. Вам нравится сотрудничать с другими людьми?",
            "27. Остаетесь ли вы на вечеринках и в компании «в тени»?",
            "28. Вы переживаете, если узнаете, что допустили ошибки в своей работе?",
            "29. Вы когда-нибудь говорили что-то плохое или неприятное о другом человеке?",
            "30. Считаете ли вы себя человеком возбудимым и чувствительным?",
            "31. Считаете ли вы, что люди затрачивают слишком много времени, чтобы обеспечить свое будущее, откладывая сбережения и страхуя себя и свою жизнь?",
            "32. Любите ли вы бывать среди людей?",
            "33. Вы дерзили когда-нибудь своим родителям в детстве?",
            "34. Долго ли вы переживаете после случившегося конфуза?",
            "35. Вы стараетесь не грубить людям?",
            "36. Любите ли вы оживление и суету вокруг вас?",
            "37. Вы когда-нибудь жульничали в игре?",
            "38. Подводят ли вас нервы?",
            "39. Хотели бы вы, чтобы люди боялись вас?",
            "40. Вы когда-нибудь воспользовались оплошностью другого человека в своих целях?",
            "41. Вы больше молчите, находясь в обществе других людей?",
            "42. Вы часто испытываете чувство одиночества?",
            "43. Лучше ли следовать установленным в обществе правилам, чем делать всё по-своему?",
            "44. Считают ли вас другие люди очень оживленным?",
            "45. Всегда ли вы сами поступаете так, как советуете поступать другим?",
            "46. Часто ли вас беспокоит чувство вины?",
            "47. Откладываете ли вы иногда на завтра то, что должны сделать сегодня?",
            "48. Могли бы вы устроить вечеринку?"
        ]

        self.scale_keys = {
            "extraversion": {"direct": [3, 7, 11, 15, 19, 23, 32, 36, 41, 44, 48], "reverse": [27]},
            "neuroticism": {"direct": [1, 5, 9, 13, 17, 21, 25, 30, 34, 38, 42, 46], "reverse": []},
            "psychoticism": {"direct": [10, 14, 22, 31, 39], "reverse": [2, 6, 18, 26, 28, 35, 43]},
            "lie": {"reverse": [4, 16, 45], "direct": [8, 12, 20, 24, 29, 33, 37, 40, 47]}
        }

        self.responses = []

    def add_response(self, response):
        self.responses.append(response)

    def calculate_scores(self):
        e_score = 0
        for q_num in self.scale_keys["extraversion"]["direct"]:
            if q_num - 1 < len(self.responses) and self.responses[q_num - 1] == 1:
                e_score += 1
        for q_num in self.scale_keys["extraversion"]["reverse"]:
            if q_num - 1 < len(self.responses) and self.responses[q_num - 1] == 0:
                e_score += 1

        n_score = 0
        for q_num in self.scale_keys["neuroticism"]["direct"]:
            if q_num - 1 < len(self.responses) and self.responses[q_num - 1] == 1:
                n_score += 1

        p_score = 0
        for q_num in self.scale_keys["psychoticism"]["direct"]:
            if q_num - 1 < len(self.responses) and self.responses[q_num - 1] == 1:
                p_score += 1
        for q_num in self.scale_keys["psychoticism"]["reverse"]:
            if q_num - 1 < len(self.responses) and self.responses[q_num - 1] == 0:
                p_score += 1

        l_score = 0
        for q_num in self.scale_keys["lie"]["direct"]:
            if q_num - 1 < len(self.responses) and self.responses[q_num - 1] == 1:
                l_score += 1
        for q_num in self.scale_keys["lie"]["reverse"]:
            if q_num - 1 < len(self.responses) and self.responses[q_num - 1] == 0:
                l_score += 1

        is_valid = l_score >= 2

        return {
            'extraversion_raw': e_score,
            'neuroticism_raw': n_score,
            'psychoticism_raw': p_score,
            'lie_raw': l_score,
            'is_valid': is_valid,
            'extraversion': (e_score / 12) * 100,
            'neuroticism': (n_score / 12) * 100,
            'psychoticism': (p_score / 12) * 100,
            'lie_norm': (l_score / 12) * 100
        }

    def get_extraversion_type(self, score):
        if score <= 2:
            return "Сильный интроверт"
        elif score <= 4:
            return "Интроверт"
        elif score <= 8:
            return "Амбиверт"
        elif score <= 9:
            return "Экстраверт"
        else:
            return "Сильный экстраверт"

    def get_neuroticism_type(self, score):
        if score <= 3:
            return "Низкий уровень нейротизма"
        elif score <= 7:
            return "Средний уровень нейротизма"
        elif score <= 10:
            return "Высокий уровень нейротизма"
        else:
            return "Очень высокий уровень нейротизма"

    def get_psychoticism_type(self, score):
        if score <= 3:
            return "Низкий уровень психотизма"
        elif score <= 8:
            return "Средний уровень психотизма"
        else:
            return "Высокий уровень психотизма"

    def get_lie_type(self, score):
        if score <= 1:
            return "Низкая искренность (результат недостоверен)"
        elif score <= 6:
            return "Средняя искренность"
        else:
            return "Высокая искренность (результат достоверен)"

    def get_temperament_type(self, extraversion_raw, neuroticism_raw):
        if extraversion_raw <= 4:
            extraversion_type = "introvert"
        elif extraversion_raw >= 9:
            extraversion_type = "extravert"
        else:
            extraversion_type = "ambivert"

        if neuroticism_raw <= 3:
            neuroticism_type = "stable"
        elif neuroticism_raw >= 8:
            neuroticism_type = "unstable"
        else:
            neuroticism_type = "balanced"

        if extraversion_type == "introvert" and neuroticism_type == "stable":
            return {
                'name': "Флегматик",
                'color': "#3498db",
                'description': "Спокойный, уравновешенный, надежный человек. Выдержанный и терпеливый, редко выходит из себя. Предпочитает стабильность и предсказуемость, обладает высокой работоспособностью."
            }
        elif extraversion_type == "introvert" and neuroticism_type == "unstable":
            return {
                'name': "Меланхолик",
                'color': "#9b59b6",
                'description': "Чувствительный, ранимый, тревожный человек. Склонен к глубоким переживаниям, даже по незначительным поводам. Быстро утомляется, нуждается в поддержке и одобрении."
            }
        elif extraversion_type == "extravert" and neuroticism_type == "stable":
            return {
                'name': "Сангвиник",
                'color': "#2ecc71",
                'description': "Жизнерадостный, активный, общительный человек. Легко адаптируется к новым условиям, быстро переключается между задачами. Оптимистичен, эмоционален, но неглубок в переживаниях."
            }
        elif extraversion_type == "extravert" and neuroticism_type == "unstable":
            return {
                'name': "Холерик",
                'color': "#e74c3c",
                'description': "Энергичный, страстный, вспыльчивый человек. Быстро возбуждается, эмоционален, склонен к резким сменам настроения. Лидер по натуре, но может быть агрессивным и нетерпеливым."
            }
        else:
            return {
                'name': "Смешанный тип",
                'color': "#f39c12",
                'description': "Вы сочетаете черты разных темпераментов. В зависимости от ситуации можете проявлять как экстравертные, так и интровертные черты. Ваше эмоциональное состояние также вариативно."
            }

    def get_temperament_chart(self, extraversion_raw, neuroticism_raw):
        x = (extraversion_raw - 6) / 6
        y = (neuroticism_raw - 6) / 6
        return x, y

    def get_scale_description(self, scale_name, value, raw_score=None):
        if scale_name == "extraversion":
            if raw_score is not None:
                if raw_score <= 2:
                    return "Сильный интроверт. Вы спокойны, застенчивы, склонны к самоанализу. Сдержаны и отдалены от всех, кроме близких друзей. Планируете и обдумываете свои действия заранее, не доверяете внезапным побуждениям, серьезно относитесь к принятию решений, любите во всем порядок. Контролируете свои чувства, вас нелегко вывести из себя."
                elif raw_score <= 4:
                    return "Интроверт. Вы склонны к самоанализу, сдержаны в общении. Предпочитаете небольшие компании близких друзей. Планируете свои действия, серьезно относитесь к решениям. Цените порядок и стабильность."
                elif raw_score <= 8:
                    return "Амбиверт. Вы сочетаете черты интроверта и экстраверта. В зависимости от ситуации можете быть как душой компании, так и предпочитать уединение. Гибко адаптируетесь к обстоятельствам."
                elif raw_score <= 10:
                    return "Экстраверт. Вы общительны, имеете широкий круг знакомств. Действуете под влиянием момента, импульсивны, оптимистичны, веселы. Предпочитаете движение и действие, склонны к рискованным поступкам."
                else:
                    return "Сильный экстраверт. Вы очень общительны, имеете широкий круг знакомств, нуждаетесь в постоянных контактах. Импульсивны, беззаботны, оптимистичны. Предпочитаете движение и действие, склонны к агрессивности и рискованным поступкам. На вас не всегда можно положиться."
        elif scale_name == "neuroticism":
            if raw_score is not None:
                if raw_score <= 3:
                    return "Низкий уровень нейротизма (эмоциональная стабильность). Вы эмоционально устойчивы, сохраняете организованное поведение в стрессовых ситуациях. Характеризуетесь зрелостью, отличной адаптацией, отсутствием большой напряженности и беспокойства. Склонны к лидерству, общительности."
                elif raw_score <= 7:
                    return "Средний уровень нейротизма. Вы достаточно эмоционально устойчивы, хорошо справляетесь со стрессом. Иногда испытываете тревогу, но она не мешает нормальной жизни."
                elif raw_score <= 9:
                    return "Высокий уровень нейротизма. Вы склонны к тревожности, эмоциональной неустойчивости. У вас может быть неустойчивость в стрессовых ситуациях, изменчивость интересов, неуверенность в себе. Вы чувствительны и впечатлительны."
                else:
                    return "Очень высокий уровень нейротизма (эмоциональная нестабильность). Вы чрезвычайно нервны, неустойчивы, плохо адаптируетесь. Склонны к быстрой смене настроений, чувству вины и беспокойства, депрессивным реакциям, рассеянности внимания."
        elif scale_name == "psychoticism":
            if raw_score is not None:
                if raw_score <= 3:
                    return "Низкий уровень психотизма. Вы склонны к сотрудничеству, хорошо ладите с людьми, уважаете социальные нормы и правила. Эмпатичны и заботливы."
                elif raw_score <= 8:
                    return "Средний уровень психотизма. Вы достаточно социально адаптированы, умеете сочувствовать другим. В целом следуете общепринятым нормам поведения, но иногда можете проявлять отстраненность."
                else:
                    return "Высокий уровень психотизма. Вы склонны к асоциальному поведению, вычурности, неадекватности эмоциональных реакций. Вам свойственны высокая конфликтность, неконтактность, эгоцентричность, эгоистичность, равнодушие."
        else:
            if raw_score is not None:
                if raw_score <= 1:
                    return "Низкая искренность. Результаты теста могут быть недостоверны. Возможно, вы отвечали неискренне или стремились произвести благоприятное впечатление. Попробуйте пройти тест еще раз, отвечая более откровенно."
                elif raw_score <= 6:
                    return "Средняя искренность. Результаты теста можно считать достаточно достоверными, но некоторая социальная желательность могла повлиять на ответы."
                else:
                    return "Высокая искренность. Результаты теста достоверны. Вы отвечали честно и открыто."
        return "Описание отсутствует"


class EPQRSResultsTable(FullscreenMixin):
    def __init__(self, parent, scores, raw_scores, lie_score, lie_norm, is_valid, fio=None, age=None, gender=None):
        self.parent = parent
        self.scores = scores
        self.raw_scores = raw_scores
        self.lie_score = lie_score
        self.lie_norm = lie_norm
        self.is_valid = is_valid
        self.fio = fio
        self.age = age
        self.gender = gender
        self.window = None
        self.test = EPQRSTest()

    def get_level(self, value, scale_name=None):
        if scale_name == "lie":
            if value <= 8.33:
                return "Низкая"
            elif value <= 50:
                return "Средняя"
            else:
                return "Высокая"
        elif scale_name == "extraversion":
            if value <= 33.3:
                return "Очень низкий"
            elif value <= 41.5:
                return "Низкий"
            elif value <= 66.7:
                return "Средний"
            elif value <= 75:
                return "Высокий"
            else:
                return "Очень высокий"
        elif scale_name == "neuroticism":
            if value < 50:
                return "Низкий"
            elif value <= 70:
                return "Средний"
            elif value <= 75:
                return "Высокий"
            else:
                return "Очень высокий"
        elif scale_name == "psychoticism":
            if value <= 25:
                return "Низкий"
            elif value <= 60:
                return "Средний"
            else:
                return "Высокий"
        else:
            if value <= 25:
                return "Низкий"
            elif value <= 50:
                return "Средний"
            elif value <= 75:
                return "Повышенный"
            else:
                return "Высокий"

    def get_color(self, value, scale_name=None):
        if scale_name == "lie":
            if value <= 8.33:
                return "#e74c3c"
            elif value <= 50:
                return "#f39c12"
            else:
                return "#2ecc71"
        elif scale_name == "psychoticism":
            if value <= 20:
                return "#2ecc71"
            elif value <= 42:
                return "#f39c12"
            else:
                return "#e74c3c"
        elif scale_name == "extraversion":
            if value <= 33.3:
                return "#2ecc71"
            elif value <= 41.7:
                return "#58d68d"
            elif value <= 66.7:
                return "#f39c12"
            elif value <= 75:
                return "#e67e22"
            else:
                return "#e74c3c"
        else:
            if value <= 25:
                return "#2ecc71"
            elif value <= 50:
                return "#58d68d"
            elif value <= 75:
                return "#f39c12"
            else:
                return "#e74c3c"

    def show(self):
        self.window = tk.Toplevel(self.parent)
        self.window.title("Результаты EPQ-RS - Подробная таблица")
        self.window.geometry("1400x900")
        self.window.configure(bg="#f0f4f8")

        self.setup_fullscreen(self.window, "1400x900")

        try:
            self.window.iconbitmap("icon.ico")
        except:
            pass

        main_frame = tk.Frame(self.window, bg="#f0f4f8")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        top_frame = tk.Frame(main_frame, bg="#f0f4f8")
        top_frame.pack(fill=tk.X, pady=(0, 15))

        self.add_fullscreen_button_to_frame(top_frame, side=tk.RIGHT, bg_color="#2c3e50")

        title_frame = tk.Frame(top_frame, bg="#f0f4f8")
        title_frame.pack(fill=tk.X, side=tk.LEFT, expand=True)
        tk.Label(title_frame, text="Результаты теста EPQ-RS (Айзенк)", font=("Segoe UI", 18, "bold"), fg="#2c3e50",
                 bg="#f0f4f8").pack()
        if self.fio:
            tk.Label(title_frame, text=f"ФИО: {self.fio}", font=("Segoe UI", 11), fg="#7f8c8d", bg="#f0f4f8").pack()
        info = f"{self.gender or ''} {self.age or ''} лет".strip()
        if info:
            tk.Label(title_frame, text=info, font=("Segoe UI", 11), fg="#7f8c8d", bg="#f0f4f8").pack()

        # Круг Айзенка
        eisenck_frame = tk.Frame(main_frame, bg="#ffffff", relief=tk.RAISED, bd=1)
        eisenck_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Label(eisenck_frame, text="Круг Айзенка (тип темперамента)", font=("Segoe UI", 11, "bold"),
                 fg="#2c3e50", bg="#ffffff").pack(pady=(8, 3))

        fig = Figure(figsize=(3, 3), dpi=100, facecolor="#ffffff")
        ax = fig.add_subplot(111)

        ax.axhline(y=0, color='black', linewidth=1)
        ax.axvline(x=0, color='black', linewidth=1)

        circle = plt.Circle((0, 0), 1, fill=False, color='#3498db', linewidth=1.5, linestyle='--')
        ax.add_patch(circle)

        ax.text(1.0, 0, 'Экстраверсия', ha='center', va='center', fontsize=8, color='#2ecc71')
        ax.text(-1.0, 0, 'Интроверсия', ha='center', va='center', fontsize=8, color='#3498db')
        ax.text(0, 1.0, 'Нейротизм', ha='center', va='center', fontsize=8, color='#e74c3c')
        ax.text(0, -1.0, 'Стабильность', ha='center', va='center', fontsize=8, color='#2ecc71')

        ax.text(0.65, 0.65, 'Холерик', ha='center', va='center', fontsize=8, fontweight='bold', color='#e74c3c')
        ax.text(-0.65, 0.65, 'Меланхолик', ha='center', va='center', fontsize=8, fontweight='bold', color='#9b59b6')
        ax.text(0.65, -0.65, 'Сангвиник', ha='center', va='center', fontsize=8, fontweight='bold', color='#2ecc71')
        ax.text(-0.65, -0.65, 'Флегматик', ha='center', va='center', fontsize=8, fontweight='bold', color='#3498db')

        x, y = self.test.get_temperament_chart(
            self.raw_scores['extraversion_raw'],
            self.raw_scores['neuroticism_raw']
        )

        ax.plot(x, y, 'ro', markersize=8, markerfacecolor='red', markeredgecolor='darkred')

        ax.set_xlim(-1.2, 1.2)
        ax.set_ylim(-1.2, 1.2)
        ax.set_aspect('equal')
        ax.axis('off')

        canvas = FigureCanvasTkAgg(fig, master=eisenck_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(pady=5)

        # Таблица
        table_frame = tk.Frame(main_frame, bg="#f0f4f8")
        table_frame.pack(fill=tk.BOTH, expand=True)

        # Заголовки таблицы
        headers = ["№", "Шкала", "Сырой балл", "Макс.", "Норм. балл", "Уровень", "Описание"]
        for col, header in enumerate(headers):
            tk.Label(table_frame, text=header, font=("Segoe UI", 11, "bold"),
                     bg="#27ae60", fg="white", padx=10, pady=8, relief=tk.FLAT).grid(
                row=0, column=col, sticky="nsew")

        max_scores = {
            "extraversion": 12,
            "neuroticism": 12,
            "psychoticism": 12,
            "lie": 12
        }

        scale_names_ru = {
            "extraversion": "Экстраверсия-Интроверсия",
            "neuroticism": "Нейротизм",
            "psychoticism": "Психотизм",
            "lie": "Контрольная шкала (искренность)"
        }

        raw_values = {
            "extraversion": self.raw_scores['extraversion_raw'],
            "neuroticism": self.raw_scores['neuroticism_raw'],
            "psychoticism": self.raw_scores['psychoticism_raw'],
            "lie": self.lie_score
        }

        norm_values = {
            "extraversion": self.scores['extraversion'],
            "neuroticism": self.scores['neuroticism'],
            "psychoticism": self.scores['psychoticism'],
            "lie": self.lie_norm
        }

        for i, (scale, score) in enumerate(norm_values.items(), 1):
            raw = raw_values.get(scale, 0)
            level = self.get_level(score, scale)
            color = self.get_color(score, scale)
            description = self.test.get_scale_description(scale, score, raw)
            bg_color = "#ffffff" if i % 2 == 0 else "#f8f9fa"
            scale_ru = scale_names_ru.get(scale, scale)

            tk.Label(table_frame, text=str(i), font=("Segoe UI", 10), bg=bg_color, padx=10, pady=8,
                     relief=tk.FLAT).grid(row=i, column=0, sticky="nsew")
            tk.Label(table_frame, text=scale_ru, font=("Segoe UI", 10), bg=bg_color, padx=10, pady=8, anchor="w",
                     relief=tk.FLAT).grid(row=i, column=1, sticky="nsew")
            tk.Label(table_frame, text=str(raw), font=("Segoe UI", 10), bg=bg_color, padx=10, pady=8,
                     relief=tk.FLAT).grid(row=i, column=2, sticky="nsew")
            tk.Label(table_frame, text=str(max_scores.get(scale, 0)), font=("Segoe UI", 10), bg=bg_color, padx=10,
                     pady=8, relief=tk.FLAT).grid(row=i, column=3, sticky="nsew")
            tk.Label(table_frame, text=f"{score:.1f}", font=("Segoe UI", 10, "bold"), fg=color, bg=bg_color, padx=10,
                     pady=8, relief=tk.FLAT).grid(row=i, column=4, sticky="nsew")
            tk.Label(table_frame, text=level, font=("Segoe UI", 10), fg=color, bg=bg_color, padx=10, pady=8,
                     relief=tk.FLAT).grid(row=i, column=5, sticky="nsew")
            tk.Label(table_frame, text=description, font=("Segoe UI", 9), bg=bg_color, padx=10, pady=8, anchor="w",
                     wraplength=500, justify=tk.LEFT, relief=tk.FLAT).grid(row=i, column=6, sticky="nsew")

        # Настройка весов
        table_frame.columnconfigure(0, weight=0, minsize=40)
        table_frame.columnconfigure(1, weight=1, minsize=180)
        table_frame.columnconfigure(2, weight=0, minsize=80)
        table_frame.columnconfigure(3, weight=0, minsize=60)
        table_frame.columnconfigure(4, weight=0, minsize=80)
        table_frame.columnconfigure(5, weight=0, minsize=110)
        table_frame.columnconfigure(6, weight=3, minsize=400)

        if not self.is_valid:
            warning_frame = tk.Frame(main_frame, bg="#ffe6e6", relief=tk.RAISED, bd=1)
            warning_frame.pack(fill=tk.X, pady=10)
            tk.Label(warning_frame, text="ВНИМАНИЕ! Результат может быть недостоверен!",
                     font=("Segoe UI", 10, "bold"), fg="#e74c3c", bg="#ffe6e6").pack(pady=5)
            tk.Label(warning_frame,
                     text="Низкий балл по контрольной шкале (искренности) указывает на возможную неискренность ответов. "
                          "Попробуйте пройти тест еще раз, отвечая более откровенно.",
                     font=("Segoe UI", 9), fg="#555", bg="#ffe6e6").pack(pady=(0, 5))

        # Кнопка закрытия
        tk.Button(main_frame, text="Закрыть", command=self.window.destroy,
                  bg="#27ae60", fg="white", font=("Segoe UI", 11), padx=20, pady=5,
                  relief=tk.FLAT, cursor="hand2").pack(pady=15)
class EPQRSDashboard(FullscreenMixin):
    def __init__(self, parent, scores, raw_scores, deviance, lie_score, lie_norm, is_valid, answers=None, fio=None, age=None, gender=None):
        self.parent = parent
        self.scores = scores
        self.raw_scores = raw_scores
        self.deviance = deviance
        self.lie_score = lie_score
        self.lie_norm = lie_norm
        self.is_valid = is_valid
        self.answers = answers
        self.fio = fio
        self.age = age
        self.gender = gender
        self.test = EPQRSTest()
        self.fuzzy_system = EPQRSFuzzySystem()
        self.window = None

    def get_category(self, value):
        if value <= 35:
            return "Низкий уровень"
        elif value <= 50:
            return "Средний уровень"
        elif value <= 75:
            return "Повышенный уровень"
        else:
            return "Высокий уровень"

    def get_color(self, value):
        if value <= 35:
            return "#2ecc71"
        elif value <= 55:
            return "#58d68d"
        elif value <= 75:
            return "#f39c12"
        else:
            return "#e74c3c"

    def save_data(self, parent_window):
        filename = DataSaver.save_to_csv(self.fio, self.gender, self.age, self.answers, "EPQ_RS")
        if filename:
            messagebox.showinfo("Успех", f"Данные сохранены в файл:\n{filename}")
        else:
            messagebox.showerror("Ошибка", "Не удалось сохранить данные")

    def back_to_menu(self):
        if messagebox.askyesno("Подтверждение", "Вы точно хотите вернуться в главное меню?"):
            if self.window:
                self.window.destroy()

            for widget in self.parent.winfo_children():
                widget.destroy()

            from main import MainMenu
            MainMenu(self.parent, self.fio, self.gender, self.age)

    def show(self):
        self.window = tk.Toplevel(self.parent)
        self.window.title("Оценка по EPQ-RS")
        self.window.geometry("1300x750")
        self.window.configure(bg="#f0f4f8")

        self.setup_fullscreen(self.window, "1300x750")

        try:
            self.window.iconbitmap("icon.ico")
        except:
            pass

        main_frame = tk.Frame(self.window, bg="#f0f4f8")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        top_frame = tk.Frame(main_frame, bg="#f0f4f8")
        top_frame.pack(fill=tk.X, pady=(0, 15))

        self.add_fullscreen_button_to_frame(top_frame, side=tk.RIGHT, bg_color="#2c3e50")

        info_frame = tk.Frame(main_frame, bg="#ffffff", relief=tk.RAISED, bd=1)
        info_frame.pack(fill=tk.X, pady=(0, 15))
        tk.Label(info_frame, text="EPQ-RS - Личностный опросник Айзенка", font=("Segoe UI", 16, "bold"), fg="#2c3e50",
                 bg="#ffffff").pack(side=tk.LEFT, padx=15, pady=10)
        if self.fio:
            tk.Label(info_frame, text=f"{self.fio}", font=("Segoe UI", 11), fg="#7f8c8d", bg="#ffffff").pack(side=tk.RIGHT, padx=15)
        if self.age or self.gender:
            info = f"{self.gender or ''} {self.age or ''} лет".strip()
            if info:
                tk.Label(info_frame, text=info, font=("Segoe UI", 11), fg="#7f8c8d", bg="#ffffff").pack(side=tk.RIGHT, padx=5)

        temperament = self.test.get_temperament_type(
            self.raw_scores['extraversion_raw'],
            self.raw_scores['neuroticism_raw']
        )

        temp_frame = tk.Frame(info_frame, bg="#f0f8ff", relief=tk.RAISED, bd=1)
        temp_frame.pack(side=tk.RIGHT, padx=15, pady=5)
        tk.Label(temp_frame, text="Тип темперамента", font=("Segoe UI", 10, "bold"),
                 fg="#2c3e50", bg="#f0f8ff").pack(side=tk.LEFT, padx=10)
        tk.Label(temp_frame, text=temperament['name'], font=("Segoe UI", 12, "bold"),
                 fg=temperament['color'], bg="#f0f8ff").pack(side=tk.LEFT, padx=5)

        content_frame = tk.Frame(main_frame, bg="#f0f4f8")
        content_frame.pack(fill=tk.BOTH, expand=True)

        left_frame = tk.Frame(content_frame, bg="#ffffff", relief=tk.RAISED, bd=1)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        fig = Figure(figsize=(7, 5), dpi=100, facecolor="#ffffff")
        ax = fig.add_subplot(111, facecolor="#f8f9fa")
        categories = ['Экстраверсия', 'Нейротизм', 'Психотизм', 'Искренность', 'Итог']
        values = [self.scores['extraversion'], self.scores['neuroticism'],
                  self.scores['psychoticism'], self.lie_norm, self.deviance]
        colors = ['#3498db', '#2ecc71', '#e74c3c', '#9b59b6', '#f39c12']
        bars = ax.bar(categories, values, color=colors, alpha=0.8, edgecolor='white', linewidth=1)
        ax.axhline(y=75, color='#e74c3c', linestyle='--', linewidth=1.5, alpha=0.7, label='Критический (75)')
        ax.axhline(y=55, color='#f39c12', linestyle='--', linewidth=1.5, alpha=0.7, label='Высокий (55)')
        ax.axhline(y=35, color='#f1c40f', linestyle='--', linewidth=1.5, alpha=0.7, label='Средний (35)')
        ax.set_ylim(0, 100)
        ax.set_ylabel('Значение (0-100)', fontsize=11, color="#555")
        ax.set_title('Результаты теста EPQ-RS', fontsize=13, fontweight='bold', color="#2c3e50", pad=15)
        ax.legend(loc='upper right', frameon=True, facecolor='white', fontsize=9)
        ax.grid(True, alpha=0.2, axis='y')
        for bar, val in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 2, f'{val:.1f}',
                    ha='center', va='bottom', fontweight='bold', fontsize=10)
        canvas = FigureCanvasTkAgg(fig, master=left_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        right_frame = tk.Frame(content_frame, bg="#f0f4f8")
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))

        result_card = tk.Frame(right_frame, bg="#ffffff", relief=tk.RAISED, bd=1)
        result_card.pack(fill=tk.X, pady=(0, 10))
        tk.Label(result_card, text="Итоговая оценка", font=("Segoe UI", 12, "bold"), fg="#2c3e50", bg="#ffffff").pack(
            pady=(10, 5))
        category = self.get_category(self.deviance)
        color = self.get_color(self.deviance)
        tk.Label(result_card, text=f"{self.deviance:.1f}", font=("Segoe UI", 28, "bold"), fg=color,
                 bg="#ffffff").pack()
        tk.Label(result_card, text=category, font=("Segoe UI", 11), fg=color, bg="#ffffff").pack(pady=(0, 10))

        comp_card = tk.Frame(right_frame, bg="#ffffff", relief=tk.RAISED, bd=1)
        comp_card.pack(fill=tk.X, pady=(0, 10))
        tk.Label(comp_card, text="Компоненты", font=("Segoe UI", 12, "bold"), fg="#2c3e50", bg="#ffffff").pack(
            pady=(10, 5))
        components = [
            ("Экстраверсия", self.scores['extraversion'], "#3498db"),
            ("Нейротизм", self.scores['neuroticism'], "#2ecc71"),
            ("Психотизм", self.scores['psychoticism'], "#e74c3c")
        ]
        for label, val, clr in components:
            frame = tk.Frame(comp_card, bg="#ffffff")
            frame.pack(fill=tk.X, padx=15, pady=4)
            tk.Label(frame, text=f"{label}:", font=("Segoe UI", 10), fg="#555", bg="#ffffff").pack(side=tk.LEFT)
            tk.Label(frame, text=f"{val:.1f}", font=("Segoe UI", 11, "bold"), fg=clr, bg="#ffffff").pack(side=tk.RIGHT)



        btn_frame = tk.Frame(right_frame, bg="#f0f4f8")
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        tk.Button(btn_frame, text="Полная таблица",
                  command=lambda: EPQRSResultsTable(
                      self.window, self.scores, self.raw_scores, self.lie_score, self.lie_norm, self.is_valid,
                      self.fio, self.age, self.gender
                  ).show(),
                  bg="#27ae60", fg="white", font=("Segoe UI", 10), padx=15, pady=5, relief=tk.FLAT,
                  cursor="hand2").pack(side=tk.LEFT, padx=(0, 5))
        tk.Button(btn_frame, text="Сохранить ответы",
                  command=lambda: self.save_data(self.window),
                  bg="#2980b9", fg="white", font=("Segoe UI", 10), padx=15, pady=5, relief=tk.FLAT,
                  cursor="hand2").pack(side=tk.LEFT, padx=(0, 5))
        tk.Button(btn_frame, text="Главное меню",
                  command=self.back_to_menu,
                  bg="#e67e22", fg="white", font=("Segoe UI", 10), padx=15, pady=5, relief=tk.FLAT,
                  cursor="hand2").pack(side=tk.LEFT, padx=(0, 5))


class EPQRSQuizApp(FullscreenMixin):
    def __init__(self, root, fio=None, gender=None, age=None):
        self.root = root
        self.root.title("EPQ-RS - Личностный опросник Айзенка")
        self.root.geometry("850x750")
        self.root.configure(bg="#e8eef2")
        self.root.resizable(True, True)

        self.setup_fullscreen(root, "850x750")

        try:
            self.root.iconbitmap("icon.ico")
        except:
            pass

        self.user_fio = fio if fio else ""
        self.user_gender = gender if gender else None
        self.user_age = age if age else None

        self.test = EPQRSTest()
        self.fuzzy_system = EPQRSFuzzySystem()

        self.current_question = 0
        self.answers = []

        self.setup_styles()
        self.show_welcome()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TProgressbar", background="#27ae60", troughcolor="#d5dbdb", thickness=10)

    def back_to_menu(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        from main import MainMenu
        MainMenu(self.root, self.user_fio, self.user_gender, self.user_age)

    def _debug_deviance_rules(self, extraversion, neuroticism, psychoticism, lie, deviance):
        e_fuzzy = self.fuzzy_system.fuzzify(extraversion, self.fuzzy_system.e_inputs['extraversion']['mfs'])
        n_fuzzy = self.fuzzy_system.fuzzify(neuroticism, self.fuzzy_system.n_inputs['neuroticism']['mfs'])
        p_fuzzy = self.fuzzy_system.fuzzify(psychoticism, self.fuzzy_system.p_inputs['psychoticism']['mfs'])
        l_fuzzy = self.fuzzy_system.fuzzify(lie, self.fuzzy_system.l_inputs['lie']['mfs'])

        # Термы для каждой шкалы
        e_terms = ['strong_introvert', 'introvert', 'ambivert', 'extravert', 'strong_extravert']
        n_terms = ['low', 'average', 'high', 'very_high']
        p_terms = ['low', 'average', 'high']
        l_terms = ['low', 'average', 'high']

        out_names = {1: 'low (очень низкий)', 2: 'middle (низкий)',
                     3: 'elevated (средний)', 4: 'high (высокий)', 5: 'very_high (критический)'}

        print("ОТЛАДКА ИТОГОВОЙ СИСТЕМЫ EPQ-RS")

        print("\n1. ФАЗЗИФИКАЦИЯ ВХОДНЫХ ЗНАЧЕНИЙ:")
        print(f"   Экстраверсия = {extraversion}")
        for i, t in enumerate(e_terms, 1):
            val = e_fuzzy.get(t, 0)
            if val > 0:
                print(f"      Экстраверсия: {t} (индекс {i}) = {val:.3f}")

        print(f"\n   Нейротизм = {neuroticism}")
        for i, t in enumerate(n_terms, 1):
            val = n_fuzzy.get(t, 0)
            if val > 0:
                print(f"      Нейротизм: {t} (индекс {i}) = {val:.3f}")

        print(f"\n   Психотизм = {psychoticism}")
        for i, t in enumerate(p_terms, 1):
            val = p_fuzzy.get(t, 0)
            if val > 0:
                print(f"      Психотизм: {t} (индекс {i}) = {val:.3f}")

        print(f"\n   Искренность = {lie}")
        for i, t in enumerate(l_terms, 1):
            val = l_fuzzy.get(t, 0)
            if val > 0:
                print(f"      Искренность: {t} (индекс {i}) = {val:.3f}")

        print("\n2. АКТИВИРОВАННЫЕ ПРАВИЛА:")

        active_rules = []
        for rule in self.fuzzy_system.rules:
            e_idx, n_idx, p_idx, l_idx, out = rule

            # Получаем степени принадлежности
            e_val = 1.0 if e_idx == 0 or e_idx < 0 else e_fuzzy.get(e_terms[e_idx - 1], 0) if 1 <= e_idx <= len(
                e_terms) else 0
            n_val = 1.0 if n_idx == 0 or n_idx < 0 else n_fuzzy.get(n_terms[n_idx - 1], 0) if 1 <= n_idx <= len(
                n_terms) else 0
            p_val = 1.0 if p_idx == 0 or p_idx < 0 else p_fuzzy.get(p_terms[p_idx - 1], 0) if 1 <= p_idx <= len(
                p_terms) else 0
            l_val = 1.0 if l_idx == 0 or l_idx < 0 else l_fuzzy.get(l_terms[l_idx - 1], 0) if 1 <= l_idx <= len(
                l_terms) else 0

            activation = min(e_val, n_val, p_val, l_val)
            if activation > 0.01:
                active_rules.append((rule, activation, out))

        active_rules.sort(key=lambda x: x[1], reverse=True)

        for rule, activation, out in active_rules[:30]:
            e_idx, n_idx, p_idx, l_idx, out = rule
            print(f"   Rule ({e_idx},{n_idx},{p_idx},{l_idx}) → out={out}, активация={activation:.3f}")

        print(f"\n   Всего активных правил: {len(active_rules)}")

        # Максимальная активация по выходным термам
        max_out = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for rule, activation, out in active_rules:
            max_out[out] = max(max_out[out], activation)

        print("\n3. МАКСИМАЛЬНАЯ АКТИВАЦИЯ ПО ВЫХОДНЫМ ТЕРМАМ:")
        for out, act in max_out.items():
            if act > 0:
                print(f"   {out_names.get(out)}: {act:.3f}")

        print(f"\n4. ИТОГОВЫЙ РЕЗУЛЬТАТ: {deviance:.2f}")

    def show_welcome(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        main = tk.Frame(self.root, bg="#e8eef2")
        main.pack(fill=tk.BOTH, expand=True, padx=25, pady=25)

        top_bar = tk.Frame(main, bg="#e8eef2", height=40)
        top_bar.pack(fill=tk.X, pady=(0, 5))
        top_bar.pack_propagate(False)

        back_btn = tk.Button(top_bar, text="↩",
                             command=self.back_to_menu,
                             bg="#e8eef2", fg="#2c3e50", font=("Segoe UI", 22, "bold"),
                             width=2, height=1, relief=tk.FLAT, cursor="hand2",
                             activebackground="#e8eef2", activeforeground="#e74c3c",
                             bd=0, highlightthickness=0)
        back_btn.pack(side=tk.LEFT, padx=(5, 0))

        def on_enter(event):
            back_btn.config(fg="#e74c3c", font=("Segoe UI", 22, "bold"))

        def on_leave(event):
            back_btn.config(fg="#2c3e50", font=("Segoe UI", 20, "bold"))

        back_btn.bind("<Enter>", on_enter)
        back_btn.bind("<Leave>", on_leave)

        self.add_fullscreen_button_to_frame(top_bar, side=tk.RIGHT, bg_color="#2c3e50")

        title_frame = tk.Frame(main, bg="#e8eef2")
        title_frame.pack(fill=tk.X, pady=(0, 20))

        tk.Label(title_frame, text="EPQ-RS", font=("Segoe UI", 22, "bold"), fg="#2c3e50", bg="#e8eef2").pack()
        tk.Label(title_frame, text="Личностный опросник Айзенка", font=("Segoe UI", 12), fg="#7f8c8d",
                 bg="#e8eef2").pack()

        info_card = tk.Frame(main, bg="#ffffff", relief=tk.RAISED, bd=1)
        info_card.pack(fill=tk.X, pady=10)

        tk.Label(info_card, text="Данные респондента", font=("Segoe UI", 12, "bold"), fg="#2c3e50", bg="#ffffff").pack(
            pady=(10, 5))
        tk.Label(info_card, text=f"ФИО: {self.user_fio}", font=("Segoe UI", 11), fg="#555", bg="#ffffff").pack(
            anchor="w", padx=25, pady=2)
        tk.Label(info_card, text=f"Пол: {self.user_gender}", font=("Segoe UI", 11), fg="#555", bg="#ffffff").pack(
            anchor="w", padx=25, pady=2)
        tk.Label(info_card, text=f"Возраст: {self.user_age} лет", font=("Segoe UI", 11), fg="#555", bg="#ffffff").pack(
            anchor="w", padx=25, pady=(0, 12))

        # Информация о тесте
        test_info = tk.Frame(main, bg="#ffffff", relief=tk.RAISED, bd=1)
        test_info.pack(fill=tk.X, pady=10)
        tk.Label(test_info, text="Информация", font=("Segoe UI", 12, "bold"), fg="#2c3e50", bg="#ffffff").pack(
            pady=(10, 5))

        tk.Label(test_info,
                 text=f"Вам будет предложено {len(self.test.questions)} утверждений. На каждое утверждение необходимо ответить \"Да\" или \"Нет\".\n\n"
                      f"Отвечайте искренне, не задумываясь подолгу. Ваши ответы помогут оценить\n"
                      f"различные аспекты личности по трем шкалам: Экстраверсия, Нейротизм и Психотизм.\n\n"
                      f"Тест занимает около 8-10 минут.",
                 font=("Segoe UI", 11), fg="#555", bg="#ffffff", justify=tk.CENTER).pack(
            fill=tk.X, padx=15, pady=(0, 12))

        # Кнопки
        btn_frame = tk.Frame(main, bg="#e8eef2")
        btn_frame.pack(fill=tk.X, pady=15)
        tk.Button(btn_frame, text="Начать тест", command=self.start_test,
                  bg="#27ae60", fg="white", font=("Segoe UI", 11, "bold"),
                  padx=30, pady=10, relief=tk.FLAT, cursor="hand2").pack()
        tk.Button(btn_frame, text="Ввести результаты вручную", command=self.manual_input, bg="#95a5a6", fg="white",
                  font=("Segoe UI", 10), padx=20, pady=5, relief=tk.FLAT, cursor="hand2").pack(pady=(8, 0))

    def start_test(self):
        if not self.user_fio:
            messagebox.showwarning("Внимание",
                                   "Данные респондента не найдены. Пожалуйста, вернитесь в главное меню и заполните информацию.")
            return

        if not self.user_gender:
            messagebox.showwarning("Внимание",
                                   "Данные респондента не найдены. Пожалуйста, вернитесь в главное меню и заполните информацию.")
            return

        if not self.user_age or self.user_age < 12 or self.user_age > 100:
            messagebox.showwarning("Внимание",
                                   "Данные респондента не найдены. Пожалуйста, вернитесь в главное меню и заполните информацию.")
            return

        self.current_question = 0
        self.answers = []
        self.show_question()

    def show_question(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        if self.current_question >= len(self.test.questions):
            self.finish_test()
            return

        main = tk.Frame(self.root, bg="#e8eef2")
        main.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        progress = (self.current_question / len(self.test.questions)) * 100
        tk.Label(main, text=f"Вопрос {self.current_question + 1} из {len(self.test.questions)}",
                 font=("Segoe UI", 16), fg="#7f8c8d", bg="#e8eef2").pack()
        pb = ttk.Progressbar(main, length=600, mode='determinate', value=progress)
        pb.pack(pady=(5, 20))

        card = tk.Frame(main, bg="#ffffff", relief=tk.RAISED, bd=1)
        card.pack(fill=tk.BOTH, expand=True)

        tk.Label(card, text=self.test.questions[self.current_question],
                 font=("Segoe UI", 16), wraplength=700, justify=tk.LEFT,
                 bg="#ffffff", fg="#2c3e50").pack(pady=40, padx=20)

        btn_frame = tk.Frame(card, bg="#ffffff")
        btn_frame.pack(pady=20)

        tk.Button(btn_frame, text="ДА", command=lambda: self.answer(1),
                  bg="#2ecc71", fg="white", font=("Segoe UI", 16, "bold"),
                  width=10, height=1, relief=tk.FLAT, cursor="hand2").pack(side=tk.LEFT, padx=20)

        tk.Button(btn_frame, text="НЕТ", command=lambda: self.answer(0),
                  bg="#e74c3c", fg="white", font=("Segoe UI", 16, "bold"),
                  width=10, height=1, relief=tk.FLAT, cursor="hand2").pack(side=tk.LEFT, padx=20)

        # Ссылка "Вопрос непонятен"
        self.desc_frame = tk.Frame(card, bg="#f8f9fa")
        help_link = tk.Label(card, text="Вопрос непонятен", font=("Segoe UI", 14, "underline"), fg="#3498db",
                             bg="#ffffff", cursor="hand2")
        help_link.pack(pady=(10, 5))
        help_link.bind("<Button-1>", lambda e: self.toggle_description())

        if self.current_question > 0:
            nav_frame = tk.Frame(main, bg="#e8eef2")
            nav_frame.pack(fill=tk.X, pady=15)
            tk.Button(nav_frame, text="← Назад", command=self.prev_question,
                      bg="#95a5a6", fg="white", font=("Segoe UI", 14),
                      padx=20, relief=tk.FLAT, cursor="hand2").pack(side=tk.LEFT)

    def toggle_description(self):
        if hasattr(self, 'desc_frame') and self.desc_frame.winfo_ismapped():
            self.desc_frame.pack_forget()
        else:
            for w in self.desc_frame.winfo_children():
                w.destroy()

            helps = {
                1: "Эмоциональные качели: настроение может меняться без видимой причины, то вверх, то вниз.",
                2: "Зависимость от чужого мнения: когда решение меняется из-за того, что кто-то его не одобрил.",
                3: "Разговорчивость в компании: обычно говорите много или предпочитаете отмалчиваться.",
                4: "Обязательность: выполнение обещаний даже тогда, когда это стало неудобно или невыгодно.",
                5: "Беспричинная грусть: чувство несчастья, когда в жизни всё нормально.",
                6: "Долговая тревога: беспокойство о деньгах, которые взяли взаймы, даже если знаете, что вернете.",
                7: "Жизнерадостность: ощущение себя веселым, энергичным человеком, который заряжает других.",
                8: "Жадность: желание получить больше, чем положено, даже если это нечестно по отношению к другим.",
                9: "Вспыльчивость: насколько легко вас вывести из себя, нужен серьезный повод или хватит мелочи.",
                10: "Склонность к риску: готовность пробовать наркотики или алкоголь ради необычных ощущений.",
                11: "Открытость новым знакомствам: комфорт при общении с незнакомыми людьми, желание знакомиться первым.",
                12: "Нечестность: обвинение другого в своей вине, чтобы избежать наказания.",
                13: "Обидчивость: насколько легко вас задеть словами, которые другим кажутся безобидными.",
                14: "Бунтарство: нарушение правил, которые кажутся глупыми или бессмысленными.",
                15: "Раскованность в компании: способность расслабиться, дурачиться, не думая о чужом мнении.",
                16: "Самооценка привычек: уверенность, что у вас нет вредных привычек или недостатков.",
                17: "Эмоциональное истощение: состояние, когда всё надоело и хочется послать всех куда подальше.",
                18: "Значение порядка: важность чистоты, опрятности, хороших манер, отношение к неаккуратным людям.",
                19: "Инициативность в знакомстве: готовность подойти первым, а не ждать, когда другие проявят интерес.",
                20: "Честность: способность взять чужую мелочь без спроса, если она очень нужна.",
                21: "Нервозность: постоянное ощущение напряжения, тревоги, когда другим не заметно.",
                22: "Отношение к браку: убеждение, что регистрация отношений устарела и не нужна.",
                23: "Умение развлекать других: способность оживить скучную компанию, придумать занятие или шутку.",
                24: "Невнимательность: потеря или поломка чужой вещи, отношение к компенсации ущерба.",
                25: "Беспокойство: постоянное внутреннее напряжение, невозможность сидеть спокойно.",
                26: "Командная работа: предпочтение делать всё самому, а не зависеть от других в общем деле.",
                27: "Заметность в компании: привычка оставаться в тени, не привлекать внимание, молчать.",
                28: "Переживание об ошибках: долгая тревога даже после того, как ошибка исправлена и никто не ругает.",
                29: "Сплетни: обсуждение других людей за глаза, даже если это несправедливо или неприятно.",
                30: "Чувствительность: реакция на события сильнее, чем у других, впечатлительность.",
                31: "Планирование будущего: мнение, что люди слишком много времени тратят на сбережения и страховки.",
                32: "Любовь к людям: тяга находиться среди людей, в толпе, в центре событий.",
                33: "Детское непослушание: грубость родителям в детстве, дерзость в ответ на замечания.",
                34: "Застревание в неловкости: долгие переживания после конфузной ситуации, прокручивание её в голове.",
                35: "Сдержанность: осознанное старание не грубить, даже когда хочется.",
                36: "Любовь к суете: комфорт в шумном, оживленном месте, потребность в движении вокруг.",
                37: "Нечестность в игре: жульничество, подглядывание, нарушение правил ради выигрыша.",
                38: "Эмоциональный контроль: частота ситуаций, когда нервы сдают и эмоции берут верх.",
                39: "Властолюбие: желание, чтобы люди боялись, уважали из страха, а не из-за личных качеств.",
                40: "Использование других: готовность воспользоваться чужой ошибкой или слабостью для своей выгоды.",
                41: "Молчаливость: привычка больше слушать, чем говорить, даже когда есть что сказать.",
                42: "Одиночество: ощущение, что вы одиноки, даже находясь среди людей.",
                43: "Конформизм: убеждение, что лучше следовать правилам, даже если они не нравятся.",
                44: "Восприятие другими: считают ли вас окружающие очень активным, оживленным человеком.",
                45: "Честность с собой: соответствие между вашими советами другим и вашим реальным поведением.",
                46: "Чувство вины: частота беспокойства о своих поступках, переживание «а правильно ли я сделал».",
                47: "Прокрастинация: привычка откладывать дела на потом, даже зная, что нужно сделать сегодня.",
                48: "Организаторские способности: уверенность, что вы можете организовать праздник для других людей."
            }

            q_num = self.current_question + 1
            text = helps.get(q_num,
                             "Постарайтесь ответить максимально честно, основываясь на вашем типичном поведении и чувствах в обычной жизни.")

            tk.Label(self.desc_frame, text="Пояснение:", font=("Segoe UI", 14, "bold"), bg="#f8f9fa", fg="#555").pack(
                anchor="w", padx=10, pady=(8, 2))
            tk.Label(self.desc_frame, text=text, font=("Segoe UI", 14), bg="#f8f9fa", fg="#666", wraplength=450,
                     justify=tk.LEFT).pack(padx=10, pady=(0, 8))
            self.desc_frame.pack(fill=tk.X, padx=20, pady=(0, 10))

    def answer(self, value):
        if self.current_question >= len(self.answers):
            self.answers.append(value)
        else:
            self.answers[self.current_question] = value

        if self.current_question < len(self.test.questions) - 1:
            self.current_question += 1
            self.show_question()
        else:
            self.finish_test()

    def prev_question(self):
        if self.current_question > 0:
            self.current_question -= 1
            self.show_question()

    def finish_test(self):
        for answer in self.answers:
            self.test.add_response(answer)

        scores = self.test.calculate_scores()
        deviance = self.fuzzy_system.calculate_deviance(
           scores['extraversion'],
            scores['neuroticism'],
            scores['psychoticism'],
            scores['lie_norm']
        )

        self._debug_deviance_rules(
            scores['extraversion'],
            scores['neuroticism'],
            scores['psychoticism'],
            scores['lie_norm'],
            deviance
        )

        dashboard = EPQRSDashboard(
            self.root,
            {
                'extraversion': scores['extraversion'],
                'neuroticism': scores['neuroticism'],
                'psychoticism': scores['psychoticism']
            },
            scores,
            deviance,
            scores['lie_raw'],
            scores['lie_norm'],
            scores['is_valid'],
            self.answers,
            self.user_fio,
            self.user_age,
            self.user_gender
        )
        dashboard.show()

    def manual_input(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Ручной ввод - EPQ-RS")
        dialog.geometry("500x450")
        dialog.configure(bg="#f0f4f8")
        dialog.transient(self.root)
        dialog.grab_set()
        try:
            dialog.iconbitmap("icon.ico")
        except:
            pass

        tk.Label(dialog, text="Введите баллы по шкалам (0-100)", font=("Segoe UI", 12, "bold"), fg="#2c3e50",
                 bg="#f0f4f8").pack(pady=10)

        canvas = tk.Canvas(dialog, bg="#f0f4f8", highlightthickness=0)
        scrollbar = ttk.Scrollbar(dialog, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg="#f0f4f8")
        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        entries = {}
        scales = ["Экстраверсия", "Нейротизм", "Психотизм", "Искренность"]

        for s in scales:
            frame = tk.Frame(scroll_frame, bg="#f0f4f8")
            frame.pack(fill=tk.X, padx=20, pady=3)
            tk.Label(frame, text=s, font=("Segoe UI", 10), width=25, anchor="w", bg="#f0f4f8").pack(side=tk.LEFT)
            var = tk.DoubleVar(value=50)
            entries[s] = var
            tk.Scale(frame, from_=0, to=100, orient="horizontal", variable=var, length=200, bg="#f0f4f8",
                     troughcolor="#d5dbdb").pack(side=tk.LEFT, padx=10)

        canvas.pack(side="left", fill="both", expand=True, padx=10)
        scrollbar.pack(side="right", fill="y")

        def calc():
            scores = {n: v.get() for n, v in entries.items()}
            dialog.destroy()
            self.calculate_from_scores(scores, self.user_fio, self.user_gender, self.user_age)

        tk.Button(dialog, text="Рассчитать", command=calc, bg="#27ae60", fg="white", font=("Segoe UI", 11), padx=20,
                  pady=5, relief=tk.FLAT).pack(pady=15)

    def calculate_from_scores(self, epq_scores, fio=None, gender=None, age=None):
        if fio:
            self.user_fio = fio
        if gender:
            self.user_gender = gender
        if age:
            self.user_age = age

        extraversion = epq_scores["Экстраверсия"]
        neuroticism = epq_scores["Нейротизм"]
        psychoticism = epq_scores["Психотизм"]
        lie = epq_scores["Искренность"]

        deviance = self.fuzzy_system.calculate_deviance(extraversion, neuroticism, psychoticism, lie)
        self._debug_deviance_rules(extraversion, neuroticism, psychoticism, lie, deviance)

        # Для совместимости с Dashboard создаём структуру scores
        scores = {
            'extraversion': extraversion,
            'neuroticism': neuroticism,
            'psychoticism': psychoticism,
            'lie_norm': lie
        }

        raw_scores = {
            'extraversion_raw': round(extraversion / 100 * 12),
            'neuroticism_raw': round(neuroticism / 100 * 12),
            'psychoticism_raw': round(psychoticism / 100 * 12),
            'lie_raw': round(lie / 100 * 12)
        }

        is_valid = raw_scores['lie_raw'] >= 2

        dashboard = EPQRSDashboard(
            self.root,
            scores,
            raw_scores,
            deviance,
            raw_scores['lie_raw'],
            lie,
            is_valid,
            self.answers,
            self.user_fio,
            self.user_age,
            self.user_gender
        )
        dashboard.show()


def main():
    root = tk.Tk()
    app = EPQRSQuizApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()