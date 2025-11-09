# consent_keylogger_demo_with_csv.py
# Educational / consent-based key-event logger (only logs while the app window is focused)
# Writes CSV rows (timestamp, key). Creates ~/Documents/keylogs by default.
# Use only for authorized/demo/learning purposes.

import tkinter as tk
from tkinter import filedialog, messagebox
import datetime
import os
import csv

DEFAULT_LOG_DIR = os.path.join(os.path.expanduser("~"), "Documents", "keylogs")

class ConsentKeyLoggerApp:
    def __init__(self, root):
        self.root = root
        root.title("Consent-based Key Logger (Demo)")
        root.geometry("760x480")
        root.resizable(False, False)

        self.logging = False
        self.log_file_path = None

        # Ensure default folder exists
        try:
            os.makedirs(DEFAULT_LOG_DIR, exist_ok=True)
        except Exception as e:
            # If creating default folder fails, continue but inform user when trying to save
            print("Could not create default log dir:", e)

        # Top control frame
        top_frame = tk.Frame(root, pady=8)
        top_frame.pack(fill="x", padx=8)

        self.start_btn = tk.Button(top_frame, text="Start Logging", width=14, command=self.start_logging)
        self.start_btn.pack(side="left", padx=6)

        self.stop_btn = tk.Button(top_frame, text="Stop Logging", width=14, command=self.stop_logging, state="disabled")
        self.stop_btn.pack(side="left", padx=6)

        choose_btn = tk.Button(top_frame, text="Choose Log File", width=14, command=self.choose_file)
        choose_btn.pack(side="left", padx=6)

        save_btn = tk.Button(top_frame, text="Save Preview to File", width=16, command=self.save_preview_to_file)
        save_btn.pack(side="left", padx=6)

        clear_btn = tk.Button(top_frame, text="Clear Preview", width=12, command=self.clear_preview)
        clear_btn.pack(side="left", padx=6)

        info_label = tk.Label(top_frame, text="(Logs only while this window is focused. Get consent before using.)")
        info_label.pack(side="left", padx=12)

        # Preview text area
        self.preview = tk.Text(root, height=22, wrap="word")
        self.preview.pack(fill="both", expand=True, padx=10, pady=(0,10))
        self.preview.insert("1.0", "Preview of keystrokes will appear here. Click Start Logging to capture keys while this window is focused.\n")
        self.preview.configure(state="disabled")

        # Bind key events to root (fires only when window has focus)
        root.bind("<Key>", self.on_key)

        # Confirm on close if logging active
        root.protocol("WM_DELETE_WINDOW", self.on_close)

    def choose_file(self):
        path = filedialog.asksaveasfilename(
            initialdir=DEFAULT_LOG_DIR,
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("Text files", "*.txt"), ("All files", "*.*")],
            title="Choose log file (consented)"
        )
        if path:
            # Ensure parent folder exists
            parent = os.path.dirname(path)
            try:
                os.makedirs(parent, exist_ok=True)
            except Exception as e:
                messagebox.showerror("Folder error", f"Could not create or access folder:\n{parent}\n\n{e}")
                return

            # If file doesn't exist, create and write header
            try:
                new_file = not os.path.exists(path)
                with open(path, "a", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    if new_file:
                        writer.writerow(["timestamp", "key"])
                self.log_file_path = path
                messagebox.showinfo("Log file set", f"Log file set to:\n{self.log_file_path}")
            except PermissionError:
                messagebox.showerror("Permission denied", f"Cannot write to the selected file:\n{path}")
            except Exception as e:
                messagebox.showerror("File error", f"Could not create or open the file:\n{e}")

    def _create_default_log(self):
        """Create a default timestamped CSV in DEFAULT_LOG_DIR and return its path, or None on failure."""
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"typing_log_{ts}.csv"
        path = os.path.join(DEFAULT_LOG_DIR, filename)
        try:
            os.makedirs(DEFAULT_LOG_DIR, exist_ok=True)
            with open(path, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["timestamp", "key"])
            return path
        except PermissionError:
            messagebox.showerror("Permission denied",
                                 f"Cannot create default log file in:\n{DEFAULT_LOG_DIR}\n\nChoose a different location.")
            return None
        except Exception as e:
            messagebox.showerror("File error", f"Could not create default log file:\n{e}")
            return None

    def start_logging(self):
        # If user hasn't chosen a file, create a default one automatically
        if not self.log_file_path:
            if messagebox.askyesno("Log file", "No log file chosen. Create a default log file in Documents/keylogs?"):
                default_path = self._create_default_log()
                if default_path:
                    self.log_file_path = default_path
                else:
                    # user declined or error occurred; let them choose
                    if not messagebox.askyesno("Choose file", "Do you want to choose a file now?"):
                        return
                    self.choose_file()
                    if not self.log_file_path:
                        return

        if not self.log_file_path:
            messagebox.showwarning("No file", "Logging requires a writable log file. Choose a file first.")
            return

        # final permission test: try opening for append before enabling logging
        try:
            with open(self.log_file_path, "a", newline="", encoding="utf-8") as f:
                pass
        except PermissionError:
            messagebox.showerror("Permission denied", f"Cannot write to:\n{self.log_file_path}\nChoose another file.")
            self.log_file_path = None
            return
        except Exception as e:
            messagebox.showerror("File error", f"Cannot write to the log file:\n{e}")
            self.log_file_path = None
            return

        self.logging = True
        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self.append_preview(f"\n--- Logging started at {self._now_str()} ---\n")

    def stop_logging(self):
        if self.logging:
            self.logging = False
            self.start_btn.configure(state="normal")
            self.stop_btn.configure(state="disabled")
            self.append_preview(f"--- Logging stopped at {self._now_str()} ---\n\n")

    def on_key(self, event):
        """Called when a key is pressed AND the app window has focus."""
        key_repr = self._key_representation(event)
        timestamp = self._now_str()
        line = f"{timestamp}\t{key_repr}\n"

        # Always show keys in preview (for transparency)
        self.append_preview(line)

        # If logging enabled and file chosen, append to CSV file
        if self.logging and self.log_file_path:
            try:
                with open(self.log_file_path, "a", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow([timestamp, key_repr])
            except PermissionError:
                messagebox.showerror("File write error", f"Permission denied writing to:\n{self.log_file_path}")
                self.stop_logging()
            except Exception as e:
                messagebox.showerror("File write error", f"Could not write to file:\n{e}")
                self.stop_logging()

    def save_preview_to_file(self):
        """Append the current preview buffer into the chosen CSV file as a block (timestamped)."""
        if not self.log_file_path:
            # Offer to create default
            if messagebox.askyesno("No file", "No log file chosen. Create default file in Documents/keylogs?"):
                default_path = self._create_default_log()
                if default_path:
                    self.log_file_path = default_path
                else:
                    self.choose_file()
                    if not self.log_file_path:
                        return
            else:
                self.choose_file()
                if not self.log_file_path:
                    return

        text = self.get_preview_text()
        # Split preview lines and try to append as CSV rows
        try:
            lines = [ln for ln in text.splitlines() if ln.strip()]
            with open(self.log_file_path, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["--- Manual save at", self._now_str()])
                for ln in lines:
                    writer.writerow([self._now_str(), ln])
            messagebox.showinfo("Saved", f"Preview appended to {self.log_file_path}")
        except PermissionError:
            messagebox.showerror("Save error", f"Permission denied writing to:\n{self.log_file_path}")
        except Exception as e:
            messagebox.showerror("Save error", f"Could not save preview:\n{e}")

    def clear_preview(self):
        self.preview.configure(state="normal")
        self.preview.delete("1.0", "end")
        self.preview.insert("1.0", "Preview cleared. Click Start Logging to capture keys while this window is focused.\n")
        self.preview.configure(state="disabled")

    def append_preview(self, text):
        self.preview.configure(state="normal")
        self.preview.insert("end", text)
        self.preview.see("end")
        self.preview.configure(state="disabled")

    def get_preview_text(self):
        self.preview.configure(state="normal")
        text = self.preview.get("1.0", "end").rstrip()
        self.preview.configure(state="disabled")
        return text

    def on_close(self):
        if self.logging:
            if not messagebox.askyesno("Logging active", "Logging is still active. Stop logging and exit?"):
                return
            self.stop_logging()
        self.root.destroy()

    @staticmethod
    def _now_str():
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def _key_representation(event):
        """
        Return readable representation for the key event.
        event.char -> printable characters, event.keysym -> key name
        """
        if event.char and event.char.isprintable():
            ch = event.char
            if ch == "\r" or ch == "\n":
                ch = "\\n"
            elif ch == "\t":
                ch = "\\t"
            return f"CHAR('{ch}') keysym={event.keysym}"
        else:
            return f"KEY({event.keysym})"

if __name__ == "__main__":
    root = tk.Tk()
    app = ConsentKeyLoggerApp(root)
    root.mainloop()
