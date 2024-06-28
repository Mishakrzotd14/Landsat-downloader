import os
import time
import tkinter as tk

import customtkinter as ctk
from CTkTable import *


class ConsoleRedirect:
    """Redirect console output to a tkinter text box."""

    def __init__(self):
        """Initialize ConsoleRedirect."""
        self.textBox = None

    def RedirectTextBox(self, textBox):
        """Redirect console output to the specified text box."""
        self.textBox = textBox

    def write(self, string):
        """Write the given string to the text box."""
        if self.textBox:
            self.textBox.insert(tk.END, string)
            self.textBox.update_idletasks()  # force an update of the text widget
            self.textBox.after(50)


def file_size_downloaded(filepath):
    """Get the size of the downloaded file."""
    size = 0
    try:
        size = os.path.getsize(filepath)

    except FileNotFoundError:
        pass
    return size


class DownloadProgressBar:
    """Class for displaying a download progress bar."""

    def __init__(self, parent_frame, filepath, final_size, update_interval=1):
        self.parent_frame = parent_frame
        self.filepath = filepath
        self.final_size = final_size
        self.update_interval = update_interval
        self.progressbar_download = ctk.CTkProgressBar(
            self.parent_frame,
            orientation="horizontal",
            width=400,
            height=20,
            fg_color="#3C3C3C",
            progress_color="#329acd",
            mode="determinate",
        )
        self.progressbar_download.set(0)
        self.progressbar_download.grid(row=0, column=0, padx=5, pady=2)

        self.progress_text = tk.StringVar()
        progress_label_widget = ctk.CTkLabel(self.parent_frame, textvariable=self.progress_text, font=("Helvetica", 14))
        progress_label_widget.grid(row=0, column=1, padx=5, pady=2)

        self.size_text = tk.StringVar()
        size_label = ctk.CTkLabel(self.parent_frame, textvariable=self.size_text, font=("Helvetica", 14))
        size_label.grid(row=0, column=2, padx=5, pady=2)

        self.speed_text = tk.StringVar()
        speed_label = ctk.CTkLabel(self.parent_frame, textvariable=self.speed_text, font=("Helvetica", 14))
        speed_label.grid(row=0, column=3, padx=5, pady=2)

        self.start_time = time.time()
        self.update_progress()

    def update_progress(self):
        """Update the download progress."""
        downloaded_size = file_size_downloaded(self.filepath)
        if downloaded_size == self.final_size:
            self.progress_text.set("Загрузка завершена")
            self.speed_text.set("")
            self.progressbar_download.set(1)
            return

        progress_percent = int((downloaded_size / self.final_size) * 100)
        self.progressbar_download.set(progress_percent / 100)
        self.progress_text.set("{}%".format(progress_percent))
        self.size_text.set("{}MB".format(round((self.final_size / 1024 / 1024))))
        time_elapsed = time.time() - self.start_time
        download_speed = downloaded_size / time_elapsed
        self.speed_text.set("{:.2f} MB/s".format(download_speed / 1024 / 1024))

        self.parent_frame.after(self.update_interval * 100, self.update_progress)


class DownloadBarFrame(ctk.CTkFrame):
    """Class for a frame containing the download bar."""

    def __init__(self, master):
        super().__init__(master)
        self.download_barr_frame = ctk.CTkFrame(master=master)
        self.download_barr_frame.pack(pady=5, padx=10)


class InformationTable(CTkTable):
    """Class for displaying an information table."""

    def __init__(self, master, data):
        super().__init__(master, values=data, corner_radius=0, hover_color="#329acd")
        self.pack(expand=True, fill="both", padx=20, pady=20)
