# Required libraries
import tkinter as tk
import customtkinter as ctk  # Enhanced themed widgets
import json  # For saving/loading task data
import os  # File handling
import threading  # For background tasks like timers
import time  # Time control
import datetime  # Date and time functions
import platform  # To check OS type
import winsound  # Windows sound support (alarm)

# Setup UI theme
ctk.set_appearance_mode("System")  # Match OS appearance
ctk.set_default_color_theme("blue")  # Default color theme

DATA_FILE = "tasks.json"  # File to store task data

# Play alarm sound depending on platform
def play_alarm_sound():
    if platform.system() == "Windows":
        winsound.Beep(1000, 500)
        winsound.Beep(1200, 500)
    else:
        print("Beep!")  # Fallback for non-Windows systems

# Popup window to add a task
class TaskPopup(ctk.CTkToplevel):
    def __init__(self, master, save_callback):
        super().__init__(master)
        self.title("Add Task")
        self.geometry("300x400")
        self.save_callback = save_callback  # Function to call when saving a task

        # Define task input variables
        self.task_var = tk.StringVar()
        self.desc_var = tk.StringVar()
        self.date_var = tk.StringVar()
        self.time_var = tk.StringVar()
        self.daily_var = tk.BooleanVar()

        # Create UI fields
        ctk.CTkLabel(self, text="Task Name *").pack(pady=5)
        ctk.CTkEntry(self, textvariable=self.task_var).pack(pady=5)

        ctk.CTkLabel(self, text="Description").pack(pady=5)
        ctk.CTkEntry(self, textvariable=self.desc_var).pack(pady=5)

        ctk.CTkLabel(self, text="Date (YYYY-MM-DD)").pack(pady=5)
        ctk.CTkEntry(self, textvariable=self.date_var).pack(pady=5)

        ctk.CTkLabel(self, text="Time (HH:MM)").pack(pady=5)
        ctk.CTkEntry(self, textvariable=self.time_var).pack(pady=5)

        ctk.CTkCheckBox(self, text="Daily Task", variable=self.daily_var).pack(pady=5)

        ctk.CTkButton(self, text="Save Task", command=self.save_and_close).pack(pady=20)

        # Keep popup on top
        self.lift()
        self.attributes("-topmost", 1)
        self.focus_force()

    # Save task and close popup
    def save_and_close(self):
        if not self.task_var.get().strip():
            return  # Don't save empty task names
        task = {
            "title": self.task_var.get(),
            "description": self.desc_var.get(),
            "date": self.date_var.get(),
            "time": self.time_var.get(),
            "daily": self.daily_var.get(),
            "completed": False
        }
        self.save_callback(task)
        self.destroy()

# Pomodoro Timer window (25-minute focus session)
class PomodoroTimer(ctk.CTkToplevel):
    def __init__(self):
        super().__init__()
        self.title("Pomodoro Timer")
        self.geometry("250x150")
        self.remaining = 25 * 60  # 25 minutes
        self.running = False

        # Display label and buttons
        self.label = ctk.CTkLabel(self, text="25:00", font=("Arial", 24))
        self.label.pack(pady=10)

        self.start_btn = ctk.CTkButton(self, text="Start", command=self.start)
        self.start_btn.pack(pady=2)

        self.stop_btn = ctk.CTkButton(self, text="Stop & Close", command=self.stop_and_close)
        self.stop_btn.pack(pady=2)

        self.lift()
        self.attributes("-topmost", 1)
        self.focus_force()

    def start(self):
        if not self.running:
            self.running = True
            threading.Thread(target=self.countdown, daemon=True).start()

    def countdown(self):
        while self.remaining > 0 and self.running:
            mins, secs = divmod(self.remaining, 60)
            self.label.configure(text=f"{mins:02}:{secs:02}")
            time.sleep(1)
            self.remaining -= 1
        if self.remaining == 0:
            play_alarm_sound()

    def stop_and_close(self):
        self.running = False
        self.destroy()

# Simple Stopwatch window
class Stopwatch(ctk.CTkToplevel):
    def __init__(self):
        super().__init__()
        self.title("Stopwatch")
        self.geometry("250x150")
        self.running = False
        self.elapsed = 0

        self.label = ctk.CTkLabel(self, text="00:00", font=("Arial", 24))
        self.label.pack(pady=10)

        self.start_btn = ctk.CTkButton(self, text="Start", command=self.start)
        self.start_btn.pack(pady=2)

        self.stop_btn = ctk.CTkButton(self, text="Stop & Close", command=self.stop_and_close)
        self.stop_btn.pack(pady=2)

        self.lift()
        self.attributes("-topmost", 1)
        self.focus_force()

    def start(self):
        if not self.running:
            self.running = True
            threading.Thread(target=self.update, daemon=True).start()

    def update(self):
        while self.running:
            self.elapsed += 1
            mins, secs = divmod(self.elapsed, 60)
            self.label.configure(text=f"{mins:02}:{secs:02}")
            time.sleep(1)

    def stop_and_close(self):
        self.running = False
        self.destroy()

# Alarm Clock popup
class AlarmClock(ctk.CTkToplevel):
    def __init__(self):
        super().__init__()
        self.title("Set Alarm")
        self.geometry("250x150")

        self.time_var = tk.StringVar()

        ctk.CTkLabel(self, text="Alarm Time (HH:MM)").pack(pady=5)
        ctk.CTkEntry(self, textvariable=self.time_var).pack(pady=5)

        ctk.CTkButton(self, text="Set Alarm", command=self.set_alarm).pack(pady=2)
        ctk.CTkButton(self, text="Close", command=self.destroy).pack(pady=2)

        self.lift()
        self.attributes("-topmost", 1)
        self.focus_force()

    def set_alarm(self):
        target_time = self.time_var.get().strip()
        if target_time:
            threading.Thread(target=self.wait_for_alarm, args=(target_time,), daemon=True).start()

    def wait_for_alarm(self, target):
        while True:
            now = datetime.datetime.now().strftime("%H:%M")
            if now == target:
                play_alarm_sound()
                break
            time.sleep(30)  # Check every 30 seconds

# Main Task Manager App
class TaskManagerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Task Manager")
        self.geometry("500x600")

        self.tasks = []  # List of tasks
        self.task_vars = []  # UI state for each checkbox

        self.load_tasks()
        self.build_ui()
        self.check_recurring()

    # Setup main UI
    def build_ui(self):
        ctk.CTkButton(self, text="Toggle Theme", command=self.toggle_theme).pack(pady=10)
        ctk.CTkButton(self, text="Add Task", command=self.open_task_popup).pack(pady=5)

        # Task completion progress bar
        self.progress = ctk.CTkProgressBar(self)
        self.progress.pack(pady=5, fill="x", padx=10)

        # Scrollable frame for task list
        self.task_frame = ctk.CTkScrollableFrame(self, height=350)
        self.task_frame.pack(fill="both", expand=True, pady=5, padx=10)

        # Time tools
        ctk.CTkButton(self, text="Pomodoro", command=self.open_pomodoro).pack(pady=2)
        ctk.CTkButton(self, text="Stopwatch", command=self.open_stopwatch).pack(pady=2)
        ctk.CTkButton(self, text="Alarm", command=self.open_alarm).pack(pady=2)

        self.render_tasks()

    # Toggle dark/light mode
    def toggle_theme(self):
        mode = ctk.get_appearance_mode()
        ctk.set_appearance_mode("Dark" if mode == "Light" else "Light")

    # Open various windows
    def open_task_popup(self):
        TaskPopup(self, self.save_task)

    def open_pomodoro(self):
        PomodoroTimer()

    def open_stopwatch(self):
        Stopwatch()

    def open_alarm(self):
        AlarmClock()

    # Save a new task
    def save_task(self, task):
        self.tasks.append(task)
        self.save_tasks()
        self.render_tasks()

    # Delete a task
    def delete_task(self, index):
        del self.tasks[index]
        self.save_tasks()
        self.render_tasks()

    # Draw task checkboxes
    def render_tasks(self):
        for widget in self.task_frame.winfo_children():
            widget.destroy()
        self.task_vars.clear()

        for i, task in enumerate(self.tasks):
            var = tk.BooleanVar(value=task["completed"])
            cb = ctk.CTkCheckBox(self.task_frame, text=task["title"], variable=var, command=self.update_progress)
            cb.grid(row=i, column=0, sticky="w", pady=2)
            ctk.CTkButton(self.task_frame, text="Delete", width=50, command=lambda i=i: self.delete_task(i)).grid(row=i, column=1, padx=5)
            self.task_vars.append(var)

        self.update_progress()

    # Update progress bar and save completed state
    def update_progress(self):
        total = len(self.task_vars)
        done = sum(var.get() for var in self.task_vars)
        self.progress.set(done / total if total > 0 else 0)
        for i, var in enumerate(self.task_vars):
            self.tasks[i]["completed"] = var.get()
        self.save_tasks()

    # Save tasks to JSON
    def save_tasks(self):
        with open(DATA_FILE, "w") as f:
            json.dump(self.tasks, f, indent=2)

    # Load tasks from file
    def load_tasks(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as f:
                self.tasks = json.load(f)

    # Check recurring tasks every minute
    def check_recurring(self):
        def monitor():
            while True:
                now = datetime.datetime.now().strftime("%H:%M")
                today = datetime.date.today().strftime("%Y-%m-%d")
                for task in self.tasks:
                    if task.get("time") == now:
                        if task.get("daily") or task.get("date") == today:
                            print(f"Reminder: {task['title']}")
                            play_alarm_sound()
                time.sleep(60)  # Check every 1 minute
        threading.Thread(target=monitor, daemon=True).start()

# Run the app
if __name__ == "__main__":
    app = TaskManagerApp()
    app.mainloop()
