import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
import re

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PIL import Image, ImageTk
from FPI import FPIQuizApp
from buss_durkee import BussDurkeeQuizApp
from EPQ_RS import EPQRSQuizApp
from base_window import FullscreenMixin


class MainMenu(FullscreenMixin):
    def __init__(self, root, saved_fio=None, saved_gender=None, saved_age=None):
        self.root = root
        self.root.title("Психологическая диагностика")
        self.root.geometry("800x750")
        self.root.configure(bg="#e8eef2")
        self.root.resizable(True, True)

        # Настройка полноэкранного режима
        self.setup_fullscreen(root, "1000x850")

        try:
            self.root.iconbitmap("icon.ico")
        except:
            pass

        # Данные респондента
        self.user_fio = saved_fio if saved_fio else ""
        self.user_gender = saved_gender if saved_gender else None
        self.user_age = saved_age if saved_age else None

        self.show_main_menu()

    def show_main_menu(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        scroll_container = tk.Frame(self.root, bg="#e8eef2")
        scroll_container.pack(fill=tk.BOTH, expand=True)

        # Canvas для прокрутки
        canvas = tk.Canvas(scroll_container, bg="#e8eef2", highlightthickness=0)
        scrollbar = tk.Scrollbar(scroll_container, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        main = tk.Frame(canvas, bg="#e8eef2")
        canvas.create_window((0, 0), window=main, anchor="nw", tags="content_frame")

        # Обновляем область прокрутки при изменении размера
        def configure_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        main.bind("<Configure>", configure_scroll_region)

        def on_canvas_configure(event):
            canvas.itemconfig("content_frame", width=event.width)

        canvas.bind("<Configure>", on_canvas_configure)

        def on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", on_mousewheel)

        def unbind_mousewheel(event):
            canvas.unbind_all("<MouseWheel>")

        self.root.bind("<Destroy>", unbind_mousewheel)

        # Верхняя панель с кнопкой полноэкранного режима
        top_frame = tk.Frame(main, bg="#e8eef2")
        top_frame.pack(fill=tk.X, pady=(0, 10))
        self.add_fullscreen_button_to_frame(top_frame, side=tk.RIGHT)

        logo_image = Image.open("icon2.png")
        logo_image = logo_image.resize((1000, 200), Image.Resampling.LANCZOS)
        logo_photo = ImageTk.PhotoImage(logo_image)

        # Label с картинкой
        logo_label = tk.Label(main, image=logo_photo, bg="#e8eef2")
        logo_label.image = logo_photo
        logo_label.pack(pady=(10, 5))

        # Карточка ввода данных респондента
        user_card = tk.Frame(main, bg="#ffffff", relief=tk.RAISED, bd=1)
        user_card.pack(fill=tk.X, pady=10, padx=20)

        tk.Label(user_card, text="Информация о респонденте", font=("Segoe UI", 12, "bold"),
                 fg="#2c3e50", bg="#ffffff").pack(pady=(10, 8))

        fio_frame = tk.Frame(user_card, bg="#ffffff")
        fio_frame.pack(fill=tk.X, padx=15, pady=5)
        tk.Label(fio_frame, text="ФИО:", font=("Segoe UI", 10), fg="#555", bg="#ffffff",
                 width=8, anchor="w").pack(side=tk.LEFT)
        self.fio_entry = tk.Entry(fio_frame, font=("Segoe UI", 10), relief=tk.SOLID, bd=1)
        self.fio_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))

        # Предзаполняем ФИО
        if self.user_fio:
            self.fio_entry.insert(0, self.user_fio)
            self.fio_entry.config(state='normal')

        # Пол - предзаполняем
        gender_frame = tk.Frame(user_card, bg="#ffffff")
        gender_frame.pack(fill=tk.X, padx=15, pady=5)
        tk.Label(gender_frame, text="Пол:", font=("Segoe UI", 10), fg="#555", bg="#ffffff",
                 width=8, anchor="w").pack(side=tk.LEFT)
        self.gender_male = tk.BooleanVar(value=False)
        self.gender_female = tk.BooleanVar(value=False)

        # Предзаполняем пол
        if self.user_gender == "Мужской":
            self.gender_male.set(True)
        elif self.user_gender == "Женский":
            self.gender_female.set(True)

        tk.Checkbutton(gender_frame, text="Мужской", variable=self.gender_male, font=("Segoe UI", 10),
                       bg="#ffffff", activebackground="#ffffff",
                       command=self._on_gender_change).pack(side=tk.LEFT, padx=(5, 10))
        tk.Checkbutton(gender_frame, text="Женский", variable=self.gender_female, font=("Segoe UI", 10),
                       bg="#ffffff", activebackground="#ffffff",
                       command=self._on_gender_change).pack(side=tk.LEFT)

        # Возраст - предзаполняем
        age_frame = tk.Frame(user_card, bg="#ffffff")
        age_frame.pack(fill=tk.X, padx=15, pady=5)
        tk.Label(age_frame, text="Возраст:", font=("Segoe UI", 10), fg="#555", bg="#ffffff",
                 width=8, anchor="w").pack(side=tk.LEFT)
        self.age_spin = tk.Spinbox(age_frame, from_=12, to=100, width=8, font=("Segoe UI", 10),
                                   relief=tk.SOLID, bd=1)
        self.age_spin.pack(side=tk.LEFT, padx=(5, 0))

        # Предзаполняем возраст
        if self.user_age:
            self.age_spin.delete(0, tk.END)
            self.age_spin.insert(0, str(self.user_age))

        # Карточка с выбором теста
        test_card = tk.Frame(main, bg="#ffffff", relief=tk.RAISED, bd=1)
        test_card.pack(fill=tk.X, pady=10, padx=20)

        tk.Label(test_card, text="Выбор методики", font=("Segoe UI", 12, "bold"),
                 fg="#2c3e50", bg="#ffffff").pack(pady=(10, 8))

        # Кнопка FPI
        btn_fpi = tk.Button(test_card, text="Фрайбургский личностный опросник (FPI-B)",
                            command=self.start_fpi_test,
                            bg="#3498db", fg="white", font=("Segoe UI", 12, "bold"),
                            padx=20, pady=12, relief=tk.FLAT, cursor="hand2")
        btn_fpi.pack(fill=tk.X, padx=15, pady=(5, 5))

        tk.Label(test_card, text="Оценка девиантности подростков",
                 font=("Segoe UI", 11), fg="#7f8c8d", bg="#ffffff").pack(pady=(0, 5))

        tk.Frame(test_card, height=1, bg="#d5dbdb").pack(fill=tk.X, padx=15, pady=5)

        # Кнопка Басса-Дарки
        btn_bd = tk.Button(test_card, text="Опросник Басса-Дарки (Buss-Durkee)",
                           command=self.start_buss_durkee_test,
                           bg="#9b59b6", fg="white", font=("Segoe UI", 12, "bold"),
                           padx=20, pady=12, relief=tk.FLAT, cursor="hand2")
        btn_bd.pack(fill=tk.X, padx=15, pady=(5, 5))

        tk.Label(test_card, text="Диагностика агрессивности и враждебности",
                 font=("Segoe UI", 11), fg="#7f8c8d", bg="#ffffff").pack(pady=(0, 5))

        tk.Frame(test_card, height=1, bg="#d5dbdb").pack(fill=tk.X, padx=15, pady=5)

        # Кнопка EPQ-RS (Айзенк)
        btn_epq = tk.Button(test_card, text="Личностный опросник Айзенка (EPQ-RS)",
                            command=self.start_epq_rs_test,
                            bg="#27ae60", fg="white", font=("Segoe UI", 12, "bold"),
                            padx=20, pady=12, relief=tk.FLAT, cursor="hand2")
        btn_epq.pack(fill=tk.X, padx=15, pady=(5, 5))

        tk.Label(test_card, text="Исследование темперамента и личности",
                 font=("Segoe UI", 11), fg="#7f8c8d", bg="#ffffff").pack(pady=(0, 10))

        # Информация
        info_card = tk.Frame(main, bg="#ffffff", relief=tk.RAISED, bd=1)
        info_card.pack(fill=tk.X, pady=10, padx=10)
        tk.Label(info_card, text="Информация", font=("Segoe UI", 12, "bold"),
                 fg="#2c3e50", bg="#ffffff").pack(pady=(10, 5))
        tk.Label(info_card,
                 text="Выберите методику тестирования для начала диагностики.\n"
                      "FPI-B - 114 вопросов, время 10-15 минут.\n"
                      "Басса-Дарки - 75 вопросов, время 5-7 минут.\n"
                      "EPQ-RS (Айзенк) - 48 вопросов, время 8-10 минут.",
                 font=("Segoe UI", 11), fg="#555", bg="#ffffff", justify=tk.CENTER, anchor="center").pack(
            fill=tk.X, padx=15, pady=(0, 10))

    def _on_gender_change(self):
        if self.gender_male.get() and self.gender_female.get():
            self.gender_female.set(False)

    def get_gender(self):
        if self.gender_male.get():
            return "Мужской"
        if self.gender_female.get():
            return "Женский"
        return None

    def validate_user_data(self):
        self.user_fio = self.fio_entry.get().strip()
        self.user_gender = self.get_gender()
        age_str = self.age_spin.get().strip()

        # Проверка ФИО
        if not self.user_fio:
            messagebox.showwarning("Внимание", "Пожалуйста, введите ФИО")
            return False

        # Проверка, что ФИО содержит только буквы, пробелы, дефисы
        fio_pattern = r'^[a-zA-Zа-яА-ЯёЁ\s\-]+$'
        if not re.match(fio_pattern, self.user_fio):
            messagebox.showwarning("Внимание",
                                   "ФИО должно содержать только буквы, пробелы, дефисы.\n"
                                   "Пример: Иванов Иван Иванович")
            return False

        # Проверка длины ФИО
        if len(self.user_fio) < 5:
            messagebox.showwarning("Внимание", "ФИО должно содержать минимум 5 символов")
            return False

        if len(self.user_fio) > 100:
            messagebox.showwarning("Внимание", "ФИО не должно превышать 100 символов")
            return False

        if self.user_fio.isspace():
            messagebox.showwarning("Внимание", "ФИО не может состоять только из пробелов")
            return False

        words = self.user_fio.split()
        if len(words) < 2:
            messagebox.showwarning("Внимание", "Пожалуйста, введите полные ФИО (минимум фамилию и имя)")
            return False

        if not self.user_gender:
            messagebox.showwarning("Внимание", "Пожалуйста, укажите пол")
            return False

        if not age_str or not age_str.isdigit() or int(age_str) < 12 or int(age_str) > 100:
            messagebox.showwarning("Внимание", "Пожалуйста, укажите корректный возраст (12-100 лет)")
            return False

        self.user_age = int(age_str)
        return True

    def start_fpi_test(self):
        if not self.validate_user_data():
            return

        for widget in self.root.winfo_children():
            widget.destroy()

        self.fpi_app = FPIQuizApp(self.root, self.user_fio, self.user_gender, self.user_age)

    def start_buss_durkee_test(self):
        if not self.validate_user_data():
            return

        for widget in self.root.winfo_children():
            widget.destroy()

        self.bd_app = BussDurkeeQuizApp(self.root, self.user_fio, self.user_gender, self.user_age)

    def start_epq_rs_test(self):
        if not self.validate_user_data():
            return

        for widget in self.root.winfo_children():
            widget.destroy()

        self.epq_app = EPQRSQuizApp(self.root, self.user_fio, self.user_gender, self.user_age)

    def return_to_main_menu(root_to_destroy):
        if messagebox.askyesno("Подтверждение", "Вы точно хотите вернуться в главное меню?"):
            root_to_destroy.destroy()
            new_root = tk.Tk()
            app = MainMenu(new_root)
            new_root.mainloop()


def main():
    root = tk.Tk()
    app = MainMenu(root)
    root.mainloop()


if __name__ == "__main__":
    main()