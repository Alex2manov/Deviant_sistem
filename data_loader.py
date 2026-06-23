import csv
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime


class DataLoader:

    @staticmethod
    def load_csv(filepath):
        with open(filepath, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        if not rows:
            raise ValueError("Файл пуст")

        return rows[0]  # возвращаем первую запись

    @staticmethod
    def extract_respondent_data(data):
        return {
            'fio': data.get("fio", ""),
            'gender': data.get("gender", ""),
            'age': int(data.get("age", 0)) if data.get("age", "").isdigit() else 0,
            'test_name': data.get("test_name", ""),
            'test_date': data.get("test_date", "")
        }

    @staticmethod
    def extract_answers(data, test_name):
        answers = []

        if test_name == "FPI":
            max_q = 114
        elif test_name == "BussDurkee":
            max_q = 75
        else:  # EPQ_RS
            max_q = 48

        for i in range(1, max_q + 1):
            key = f"q{i}"
            value = data.get(key, "0")
            try:
                answers.append(int(float(value)))
            except:
                answers.append(0)

        return answers

    @staticmethod
    def select_file(parent, title="Выберите CSV-файл"):
        from tkinter import filedialog
        return filedialog.askopenfilename(
            title=title,
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )

    @staticmethod
    def process_fpi_file(app, filepath):
        data = DataLoader.load_csv(filepath)
        respondent = DataLoader.extract_respondent_data(data)
        answers = DataLoader.extract_answers(data, "FPI")

        # Устанавливаем данные в приложение
        app.user_fio = respondent['fio']
        app.user_gender = respondent['gender']
        app.user_age = respondent['age']
        app.answers = answers

        # Очищаем предыдущие ответы и загружаем новые
        app.fpi_test = __import__('FPI').FPITest()
        for ans in answers:
            app.fpi_test.add_response(ans)

        scores = app.fpi_test.calculate_scores()
        app.calculate_from_scores(scores, respondent['fio'], respondent['gender'], respondent['age'])

        return respondent

    @staticmethod
    def process_buss_durkee_file(app, filepath):
        data = DataLoader.load_csv(filepath)
        respondent = DataLoader.extract_respondent_data(data)
        answers = DataLoader.extract_answers(data, "BussDurkee")

        app.user_fio = respondent['fio']
        app.user_gender = respondent['gender']
        app.user_age = respondent['age']
        app.answers = answers

        # Очищаем предыдущие ответы и загружаем новые
        app.test = __import__('buss_durkee').BussDurkeeTest()
        for ans in answers:
            app.test.add_response(ans)

        scores = app.test.calculate_scores()
        app.calculate_from_scores(scores, respondent['fio'], respondent['gender'], respondent['age'])

        return respondent

    @staticmethod
    def process_epq_file(app, filepath):
        from EPQ_RS import EPQRSTest, EPQRSDashboard

        data = DataLoader.load_csv(filepath)
        respondent = DataLoader.extract_respondent_data(data)
        answers = DataLoader.extract_answers(data, "EPQ_RS")

        # Устанавливаем данные в приложение
        app.user_fio = respondent['fio']
        app.user_gender = respondent['gender']
        app.user_age = respondent['age']
        app.answers = answers

        # Очищаем предыдущие ответы и загружаем новые
        app.test = EPQRSTest()
        for ans in answers:
            app.test.add_response(ans)

        scores = app.test.calculate_scores()

        epq_scores = {
            "Экстраверсия": scores['extraversion'],
            "Нейротизм": scores['neuroticism'],
            "Психотизм": scores['psychoticism'],
            "Искренность": scores['lie_norm']
        }

        # Вызываем твой метод — в нём уже есть отладка!
        app.calculate_from_scores(epq_scores, respondent['fio'], respondent['gender'], respondent['age'])


        return respondent
