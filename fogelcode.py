import tkinter as tk
from tkinter import messagebox
import threading

def vogel_method(supply, demand, costs):
    m = len(supply)
    n = len(demand)
    allocation = [[0] * n for _ in range(m)]
    supply_left = supply[:]
    demand_left = demand[:]
    total_cost = 0

    while sum(supply_left) > 0 and sum(demand_left) > 0:
        penalties_row = []
        penalties_col = []

        for i in range(m):
            if supply_left[i] > 0:
                row_costs = [costs[i][j] for j in range(n) if demand_left[j] > 0]
                if len(row_costs) > 1:
                    penalties_row.append(sorted(row_costs)[1] - sorted(row_costs)[0])
                else:
                    penalties_row.append(sorted(row_costs)[0])
            else:
                penalties_row.append(-1)

        for j in range(n):
            if demand_left[j] > 0:
                col_costs = [costs[i][j] for i in range(m) if supply_left[i] > 0]
                if len(col_costs) > 1:
                    penalties_col.append(sorted(col_costs)[1] - sorted(col_costs)[0])
                else:
                    penalties_col.append(sorted(col_costs)[0])
            else:
                penalties_col.append(-1)

        max_row_penalty = max(penalties_row)
        max_col_penalty = max(penalties_col)

        if max_row_penalty >= max_col_penalty:
            row = penalties_row.index(max_row_penalty)
            col = min((j for j in range(n) if demand_left[j] > 0), key=lambda j: costs[row][j])
        else:
            col = penalties_col.index(max_col_penalty)
            row = min((i for i in range(m) if supply_left[i] > 0), key=lambda i: costs[i][col])

        qty = min(supply_left[row], demand_left[col])
        allocation[row][col] = qty
        supply_left[row] -= qty
        demand_left[col] -= qty
        total_cost += qty * costs[row][col]

    return allocation, total_cost


def calculate_plan_threaded():
    try:
        m = int(m_entry.get())
        n = int(n_entry.get())
        supply = [int(supply_entries[i].get()) for i in range(m)]
        demand = [int(demand_entries[i].get()) for i in range(n)]
        costs = [[int(cost_entries[i][j].get()) for j in range(n)] for i in range(m)]

        def worker():
            allocation, total_cost = vogel_method(supply, demand, costs)

            def update_ui():
                detailed_cost = []
                for i in range(m):
                    for j in range(n):
                        result_entries[i][j].config(state="normal")
                        result_entries[i][j].delete(0, tk.END)
                        result_entries[i][j].insert(0, allocation[i][j])
                        result_entries[i][j].config(state="readonly")
                        if allocation[i][j] > 0:
                            detailed_cost.append(f"{allocation[i][j]}*{costs[i][j]}")

                total_cost_label.config(
                text=f"Общая стоимость: {total_cost} ({' + '.join(detailed_cost)})"
                )

            root.after(0, update_ui)

        threading.Thread(target=worker).start()

    except ValueError:
        messagebox.showerror("Ошибка", "Пожалуйста, введите корректные числа.")

def generate_table():
    try:
        m = int(m_entry.get())
        n = int(n_entry.get())

        for widget in supply_frame.winfo_children():
            widget.destroy()
        for widget in demand_frame.winfo_children():
            widget.destroy()
        for widget in cost_frame.winfo_children():
            widget.destroy()
        for widget in result_frame.winfo_children():
            widget.destroy()

        global supply_entries
        supply_entries = []
        tk.Label(supply_frame, text="Запасы").grid(row=0, column=0)
        for i in range(m):
            entry = tk.Entry(supply_frame, width=5)
            entry.grid(row=i + 1, column=0)
            supply_entries.append(entry)

        global demand_entries
        demand_entries = []
        tk.Label(demand_frame, text="Потребности").grid(row=0, column=0)
        for j in range(n):
            entry = tk.Entry(demand_frame, width=5)
            entry.grid(row=0, column=j + 1)
            demand_entries.append(entry)

        global cost_entries
        cost_entries = []
        tk.Label(cost_frame, text="Стоимость перевозок").grid(row=0, column=0, columnspan=n)
        for i in range(m):
            row_entries = []
            for j in range(n):
                entry = tk.Entry(cost_frame, width=5)
                entry.grid(row=i + 1, column=j)
                row_entries.append(entry)
            cost_entries.append(row_entries)

        global result_entries
        result_entries = []
        tk.Label(result_frame, text="Распределение").grid(row=0, column=0, columnspan=n)
        for i in range(m):
            row_entries = []
            for j in range(n):
                entry = tk.Entry(result_frame, width=5, state="readonly")
                entry.grid(row=i + 1, column=j)
                row_entries.append(entry)
            result_entries.append(row_entries)

        calculate_button.pack(pady=10)
        total_cost_label.pack(pady=5)

    except ValueError:
        messagebox.showerror("Ошибка", "Пожалуйста, введите корректные размеры.")

root = tk.Tk()
root.title("Транспортная задача методом Фогеля")

try:
    root.iconbitmap("python.ico")
except tk.TclError:
    print("Иконка не найдена. Убедитесь, что файл python.ico находится в той же директории.")

size_frame = tk.Frame(root)
size_frame.pack(pady=10)
tk.Label(size_frame, text="Количество строк (m):").grid(row=0, column=0)
m_entry = tk.Entry(size_frame, width=5)
m_entry.grid(row=0, column=1)
tk.Label(size_frame, text="Количество столбцов (n):").grid(row=1, column=0)
n_entry = tk.Entry(size_frame, width=5)
n_entry.grid(row=1, column=1)

generate_button = tk.Button(root, text="Создать таблицу", command=generate_table)
generate_button.pack(pady=10)

supply_frame = tk.Frame(root)
supply_frame.pack(pady=10)

demand_frame = tk.Frame(root)
demand_frame.pack(pady=10)

cost_frame = tk.Frame(root)
cost_frame.pack(pady=10)

result_frame = tk.Frame(root)
result_frame.pack(pady=10)

calculate_button = tk.Button(root, text="Рассчитать", command=calculate_plan_threaded)
total_cost_label = tk.Label(root, text="Общая стоимость:")

root.mainloop()
