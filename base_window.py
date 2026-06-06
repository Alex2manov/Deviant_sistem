import tkinter as tk


class FullscreenMixin:

    # Классовая переменная
    _global_fullscreen = False
    _global_geometry = "1300x750"

    def setup_fullscreen(self, window, default_geometry="750x700"):
        self._fullscreen_window = window
        self._is_fullscreen = FullscreenMixin._global_fullscreen
        self._prev_geometry = default_geometry

        if self._is_fullscreen:
            window.attributes("-fullscreen", True)
        else:
            window.geometry(default_geometry)

        # Горячие клавиши
        self._fullscreen_window.bind("<F11>", lambda e: self.toggle_fullscreen())
        self._fullscreen_window.bind("<Escape>", lambda e: self.exit_fullscreen())

    def toggle_fullscreen(self):
        self._is_fullscreen = not self._is_fullscreen
        FullscreenMixin._global_fullscreen = self._is_fullscreen
        self._fullscreen_window.attributes("-fullscreen", self._is_fullscreen)

        if not self._is_fullscreen:
            self._fullscreen_window.geometry(self._prev_geometry)
            FullscreenMixin._global_geometry = self._prev_geometry

        if hasattr(self, 'fullscreen_btn') and self.fullscreen_btn:
            if self._is_fullscreen:
                self.fullscreen_btn.config(text="⬛ Выйти из полноэкранного режима", bg="#c0392b")
            else:
                self.fullscreen_btn.config(text="🖥️ Полноэкранный режим", bg="#34495e")

    def exit_fullscreen(self):
        if self._is_fullscreen:
            self._is_fullscreen = False
            FullscreenMixin._global_fullscreen = False
            self._fullscreen_window.attributes("-fullscreen", False)
            self._fullscreen_window.geometry(self._prev_geometry)
            if hasattr(self, 'fullscreen_btn') and self.fullscreen_btn:
                self.fullscreen_btn.config(text="🖥️ Полноэкранный режим", bg="#34495e")

    def create_fullscreen_button(self, parent, bg_color="#34495e"):
        self.fullscreen_btn = tk.Button(parent, text="🖥️ Полноэкранный режим",
                                        command=self.toggle_fullscreen,
                                        bg=bg_color, fg="white",
                                        font=("Segoe UI", 9), padx=10, pady=3,
                                        relief=tk.FLAT, cursor="hand2")
        return self.fullscreen_btn

    def add_fullscreen_button_to_frame(self, frame, side=tk.RIGHT, bg_color="#34495e"):
        btn = self.create_fullscreen_button(frame, bg_color)
        btn.pack(side=side, padx=5)
        return btn