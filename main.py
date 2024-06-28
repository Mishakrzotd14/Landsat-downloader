import customtkinter as ctk

from gui.gui import MainGUI


def set_window_dimensions(window, width_percentage, height_percentage):
    """
    Set the dimensions and position of the window based on the screen size.

    Parameters:
    - window: The Tkinter window to be configured.
    - width_percentage: The width of the window as a percentage of the screen width.
    - height_percentage: The height of the window as a percentage of the screen height.
    """
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    width = int((screen_width * width_percentage) / 100)
    height = int((screen_height * height_percentage) / 100)

    x = (screen_width - width) // 2
    y = (screen_height - height) // 2

    window.geometry(f"{width}x{height}+{x}+{y}")


if __name__ == "__main__":
    ctk.set_appearance_mode("dark")  # Modes: "System" (standard), "Dark", "Light"
    ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

    root = ctk.CTk()
    set_window_dimensions(root, width_percentage=40, height_percentage=80)
    root.title("Модуль загрузки снимков Landsat")
    app = MainGUI(root)
    root.mainloop()
