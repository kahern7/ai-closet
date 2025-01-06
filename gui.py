from optimiser.optimiser_core import ClosetOptimiser
from optimiser.visualiser import visualise_closet
import tkinter as tk

class ClosetOptimiserGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Closet Optimiser")

        # Space properties
        tk.Label(root, text="Width (mm)").pack()
        self.width = tk.Scale(root, from_=500, to=5000, orient="horizontal")
        self.width.set(2540)
        self.width.pack()

        tk.Label(root, text="Height (mm)").pack()
        self.height = tk.Scale(root, from_=788, to=2176, bigincrement=32, orient="horizontal") # max height changed to 2176 to allow for 100% space filling
        self.height.set(2176)
        self.height.pack()

        # Component preferences
        # tk.Label(root, text="Shelves").pack()
        # self.shelves = tk.Scale(root, from_=63, to=63, orient="horizontal")
        # self.shelves.pack()

        tk.Label(root, text="Drawers").pack()
        self.drawers = tk.Scale(root, from_=0, to=50, orient="horizontal")
        self.drawers.pack()

        tk.Label(root, text="Short Hanging").pack()
        self.short_hanging = tk.Scale(root, from_=0, to=100, orient="horizontal")
        self.short_hanging.pack()

        tk.Label(root, text="Long Hanging").pack()
        self.long_hanging = tk.Scale(root, from_=0, to=100, orient="horizontal")
        self.long_hanging.pack()

        # Optimise button
        tk.Button(root, text="Optimise Closet", command=self.run_optimisation).pack()

    def run_optimisation(self):
        # Collect user inputs
        width = self.width.get()
        height = self.height.get()
        preferences = {
            "shelves": 100 - self.drawers.get() - self.short_hanging.get() - self.long_hanging.get(), # self.shelves.get(),
            "drawers": self.drawers.get(),
            "short_hanging": self.short_hanging.get(),
            "long_hanging": self.long_hanging.get(),
        }

        if preferences["shelves"] < 0:
            raise ValueError("Percentages must be less than or equal to 100")

        # Run optimisation
        optimiser = ClosetOptimiser(width, height, preferences)
        best_individual = optimiser.optimise()

        # Visualise results
        arrangement = optimiser.map_individual_to_arrangement(best_individual)
        visualise_closet(arrangement, width, height, optimiser.columns)