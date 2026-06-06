import numpy as np
import matplotlib.pyplot as plt

def linzmf(x, a, b):
    """Z-образная убывающая функция"""
    return np.where(x <= a, 1, np.where(x >= b, 0, (b - x) / (b - a)))

def trap_mf(x, a, b, c, d):
    """Трапециевидная функция"""
    return np.where(x <= a, 0,
           np.where(x < b, (x - a) / (b - a),
           np.where(x <= c, 1,
           np.where(x < d, (d - x) / (d - c), 0))))

def trimf(x, a, b, c):
    """Треугольная функция"""
    return np.where(x <= a, 0,
           np.where(x <= b, (x - a) / (b - a),
           np.where(x < c, (c - x) / (c - b), 0)))

def linsmf(x, a, b):
    """S-образная возрастающая функция"""
    return np.where(x <= a, 0, np.where(x >= b, 1, (x - a) / (b - a)))

# Диапазон значений
x = np.linspace(0, 100, 1000)

# Функции принадлежности для hostility
low = linzmf(x, 9, 19)
middle = trap_mf(x, 9, 19, 31, 41)
elevated = trap_mf(x, 31, 41, 54, 64)
high = trimf(x, 54, 64, 74)
very_high = linsmf(x, 64, 74)

# Создание графика
plt.figure(figsize=(14, 6))

# Цвета для каждого терма
colors = ['#2ecc71', '#f39c12', '#f39c12', '#e67e22', '#e74c3c']
labels = ['low', 'middle', 'elevated', 'high', 'very high']
functions = [low, middle, elevated, high, very_high]

for func, label, color in zip(functions, labels, colors):
    plt.plot(x, func, linewidth=3, color=color)  # linewidth=3 вместо 2

# Отметим границы на графике
bounds = [9, 19, 31, 41, 54, 64, 74]
for bound in bounds:
    plt.axvline(x=bound, color='gray', linestyle='--', alpha=0.4, linewidth=1)

# Добавим подписи термов прямо на графике (текст больше)
plt.text(5, 1.05, 'low', ha='center', fontsize=13, color='#2ecc71', fontweight='bold')
plt.text(25, 1.05, 'middle', ha='center', fontsize=13, color='#f39c12', fontweight='bold')
plt.text(48, 1.05, 'elevated', ha='center', fontsize=13, color='#f39c12', fontweight='bold')
plt.text(60, 1.05, 'high', ha='center', fontsize=13, color='#e67e22', fontweight='bold')
plt.text(82, 1.05, 'very high', ha='center', fontsize=13, color='#e74c3c', fontweight='bold')

plt.xlim(0, 100)
plt.ylim(-0.05, 1.1)
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()