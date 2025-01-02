from gui import ClosetOptimiserGUI
import tkinter as tk

if __name__ == "__main__":
    root = tk.Tk()
    app = ClosetOptimiserGUI(root)
    root.mainloop()

    # percentages = {
    #     "drawers": 30,
    #     "hanging": 50,
    #     "shelves": 20
    # }

    # # set max size for each component (inches)
    # max_size = {
    #     "drawers": 10,
    #     "hanging": 20,
    #     "shelves": 5
    # }

    # designer = ClosetDesigner()
    # arrangement = designer.design_closet(percentages)
    # designer.visualise_closet(arrangement)