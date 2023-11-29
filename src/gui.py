import os
import subprocess
import sys
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from process_transactions import process_transactions

first_row_entry = None
last_row_entry = None

dark_bg = '#1e1e1e'  # very dark background color
light_text = '#ffffff'  # white text color
accent_color = '#d77337'  # orange accent color
entry_bg = '#2e2e2e'  # slightly lighter background for entries
button_active_bg = '#333333'  # button color when active/hover


# Define the styles for the widgets
def set_style():
    style = ttk.Style()
    style.theme_use('clam')

    style.configure('TButton', background=dark_bg, foreground=light_text, borderwidth=0, font=('Arial', 10))
    style.configure('TLabel', background=dark_bg, foreground=light_text, font=('Arial', 10))
    style.configure('TEntry', foreground=light_text, fieldbackground=entry_bg, borderwidth=0, font=('Arial', 10))
    style.map('TButton', background=[('active', button_active_bg)], foreground=[('active', light_text)])

    # Remove highlight thickness from entries
    style.configure('TEntry', highlightthickness=0)


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
    global first_row_entry, last_row_entry

    root = tk.Tk()
    root.title("CSV Processing")
    set_style()  # Apply the custom style

    # Set the main window background color
    root.configure(bg=dark_bg)

    # Create and pack widgets
    tk.Label(root, text="First Row:").pack(pady=(10, 0), padx=10)
    first_row_entry = ttk.Entry(root)
    first_row_entry.pack(pady=(0, 10), padx=10, fill='x')
    first_row_entry.insert(0, "2")  # Default value

    tk.Label(root, text="Last Row (optional):").pack(pady=(10, 0), padx=10)
    last_row_entry = ttk.Entry(root)
    last_row_entry.pack(pady=(0, 10), padx=10, fill='x')

    process_button = ttk.Button(root, text="Run Processing", command=run_processing)
    process_button.pack(pady=(0, 10), padx=10, fill='x')

    ttk.Button(root, text="Open Dictionary Directory", command=lambda: open_directory('./dictionary')).pack(pady=(0, 10), padx=10, fill='x')
    ttk.Button(root, text="Open Backup Directory", command=lambda: open_directory('./backup')).pack(pady=(0, 10), padx=10, fill='x')
    ttk.Button(root, text="Open CSV Directory", command=lambda: open_directory('./csv')).pack(pady=(0, 10), padx=10, fill='x')

    root.mainloop()


if __name__ == "__main__":
    setup_gui()
