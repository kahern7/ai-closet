from gui import ClosetOptimiserGUI
# from tests.test_gui import ClosetOptimiserGUI
import customtkinter as ctk

if __name__ == "__main__":
    root = ctk.CTk()
    app = ClosetOptimiserGUI(root)
    root.mainloop()