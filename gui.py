# gui.py

import tkinter as tk
from tkinter import ttk, messagebox
from main import run_meta_analysis


class MetaGui(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Analizator Giełdowy 3.0 + TIMDR META")
        self.geometry("600x400")

        self.run_button = ttk.Button(self, text="Uruchom analizę META", command=self.run_analysis)
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

            messagebox.showinfo("Gotowe", "Analiza META zakończona.")
        except Exception as e:
            messagebox.showerror("Błąd", str(e))


if __name__ == "__main__":
    app = MetaGui()
    app.mainloop()
