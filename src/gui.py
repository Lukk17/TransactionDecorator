import os
import subprocess
import sys
import tkinter as tk
from tkinter import messagebox
from process_transactions import process_transactions

first_row_entry = None
last_row_entry = None


def open_directory(relative_path):
    # Get the absolute path to the directory where the script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Navigate up one directory from the script's location
    parent_dir = os.path.dirname(script_dir)
    # Construct the absolute path to the desired directory
    directory_path = os.path.normpath(os.path.join(parent_dir, relative_path))

    # Attempt to open the directory using the default file explorer
    if sys.platform == "win32":
        os.startfile(directory_path)
    elif sys.platform == "darwin":  # macOS
        subprocess.Popen(["open", directory_path])
    else:  # Linux and other Unix-like OS
        subprocess.Popen(["xdg-open", directory_path])


def run_processing():
    try:
        first_row = max(int(first_row_entry.get()), 2)
        last_row = int(last_row_entry.get()) if last_row_entry.get() else None
        process_transactions(first_row, last_row)
        messagebox.showinfo("Success", "Processing completed successfully.")
    except ValueError as v:  # If the value entered is not a valid integer
        messagebox.showerror("Error", "Problem with value reading: " + str(v))
    except Exception as e:
        messagebox.showerror("Error", str(e))


def setup_gui():
    root = tk.Tk()
    root.title("CSV Processing")

    global first_row_entry, last_row_entry
    tk.Label(root, text="First Row:").pack()
    first_row_entry = tk.Entry(root)
    first_row_entry.pack()
    first_row_entry.insert(0, "2")  # Default value

    tk.Label(root, text="Last Row (optional):").pack()
    last_row_entry = tk.Entry(root)
    last_row_entry.pack()

    tk.Button(root, text="Run Processing", command=run_processing).pack()
    tk.Button(root, text="Open Dictionary Directory", command=lambda: open_directory('./dictionary')).pack()
    tk.Button(root, text="Open Backup Directory", command=lambda: open_directory('./backup')).pack()
    tk.Button(root, text="Open CSV Directory", command=lambda: open_directory('./csv')).pack()

    root.mainloop()


if __name__ == "__main__":
    setup_gui()
