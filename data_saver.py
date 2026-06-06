import csv
from datetime import datetime


class DataSaver:
    @staticmethod
    def save_to_csv(fio, gender, age, answers, test_name, filename=None):
        if filename is None:
            filename = f"{test_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            headers = ["fio", "gender", "age", "test_date", "test_name"]
            if test_name == "FPI":
                headers += [f"q{i}" for i in range(1, 115)]
            elif test_name == "BussDurkee":
                headers += [f"q{i}" for i in range(1, 76)]
            else :
                headers += [f"q{i}" for i in range(1, 49)]
            writer.writerow(headers)
            row = [fio, gender, age, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), test_name] + answers
            writer.writerow(row)
        return filename