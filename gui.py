"""gui.py

Minimalne GUI (Tkinter) nad run_meta_analysis().

Wcześniej ten plik wywalał się natychmiast przy `python gui.py`, zanim
okno zdążyło się w ogóle pokazać - `from main import run_meta_analysis`
na starcie pociągało za sobą import analizator3_core w main.py, którego
w tym repo nie ma. Naprawione w main.py (patrz komentarz tam) - import
tego modułu jest teraz opcjonalny/leniwy, więc samo importowanie main
już nie crashuje, niezależnie od tego, czy analizator3_core istnieje.
"""
import tkinter as tk
from tkinter import ttk, messagebox

from main import run_meta_analysis


class MetaGui(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Analizator Gieldowy 3.0 + TIMDR META")
        self.geometry("600x400")

        self.run_button = ttk.Button(self, text="Uruchom analize META", command=self.run_analysis)
        self.run_button.pack(pady=20)

        self.output_box = tk.Text(self, height=15)
        self.output_box.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def run_analysis(self):
        try:
            result = run_meta_analysis()
            phases = result["phases"]

            self.output_box.delete("1.0", tk.END)
            self.output_box.insert(tk.END, "Ostatnie fazy meta-pola:\n\n")

            for i, phase in enumerate(phases[-50:]):
                self.output_box.insert(tk.END, f"{i}: {phase}\n")

            messagebox.showinfo("Gotowe", "Analiza META zakonczona.")
        except Exception as e:
            messagebox.showerror("Blad", str(e))


if __name__ == "__main__":
    app = MetaGui()
    app.mainloop()
