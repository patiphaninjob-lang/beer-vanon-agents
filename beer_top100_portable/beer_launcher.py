import tkinter as tk
from tkinter import messagebox, ttk
import subprocess
import threading
import os
import sys

class BeerLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("Beer Vanon Agent Launcher")
        self.root.geometry("400x300")
        self.root.configure(bg="#0e1117")

        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TButton", foreground="#ffffff", background="#1e2329", font=("Arial", 10, "bold"))
        style.map("TButton", background=[('active', '#f0b90b')])

        label = tk.Label(root, text="🍺 Beer Vanon Agents", font=("Arial", 16, "bold"), fg="#f0b90b", bg="#0e1117")
        label.pack(pady=20)

        self.btn_us = ttk.Button(root, text="Run US Top 100 (Homework)", command=lambda: self.run_agent("us_agent/beer_top100_agent.py"))
        self.btn_us.pack(pady=10, fill=tk.X, padx=50)

        self.btn_th = ttk.Button(root, text="Run Thai Top 100 (การบ้านไทย)", command=lambda: self.run_agent("thai_agent/thai_top100_agent.py"))
        self.btn_th.pack(pady=10, fill=tk.X, padx=50)

        self.btn_coach = ttk.Button(root, text="Open AI Coach (Streamlit)", command=self.run_coach)
        self.btn_coach.pack(pady=10, fill=tk.X, padx=50)

        self.status = tk.Label(root, text="Ready", fg="#8a8f98", bg="#0e1117", font=("Arial", 9))
        self.status.pack(side=tk.BOTTOM, pady=10)

    def run_agent(self, script):
        if not os.path.exists(script):
            messagebox.showerror("Error", f"Script {script} not found!")
            return
        
        self.status.config(text=f"Running {script}...", fg="#f0b90b")
        threading.Thread(target=self._execute, args=(script,), daemon=True).start()

    def _execute(self, script):
        try:
            # Run in a new terminal window
            subprocess.Popen(f'start cmd /k python {script}', shell=True)
            self.root.after(0, lambda: self.status.config(text="Agent started in new window", fg="#00d395"))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))

    def run_coach(self):
        try:
            subprocess.Popen('start launch_coach.bat', shell=True)
            self.status.config(text="Coach launching...", fg="#00d395")
        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = BeerLauncher(root)
    root.mainloop()
