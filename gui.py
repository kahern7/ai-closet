from optimiser.optimiser_core import ClosetOptimiser
from optimiser.visualiser import visualise_closet
import tkinter as tk

class ClosetOptimiserGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Closet Optimiser")

        # Space properties
        tk.Label(root, text="Width").pack()
        self.width = tk.Scale(root, from_=50, to=200, orient="horizontal")
        self.width.pack()

        tk.Label(root, text="Height").pack()
        self.height = tk.Scale(root, from_=50, to=200, orient="horizontal")
        self.height.pack()

        # Component preferences
        tk.Label(root, text="Shelves").pack()
        self.shelves = tk.Scale(root, from_=0, to=100, orient="horizontal")
        self.shelves.pack()

        tk.Label(root, text="Drawers").pack()
        self.drawers = tk.Scale(root, from_=0, to=100, orient="horizontal")
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
            "shelves": self.shelves.get(),
            "drawers": self.drawers.get(),
            "short_hanging": self.short_hanging.get(),
            "long_hanging": self.long_hanging.get(),
        }

        # Run optimisation
        optimiser = ClosetOptimiser(width, height, preferences)
        best_arrangement = optimiser.optimise()

        # Visualise results
        visualise_closet(best_arrangement, width, height, optimiser.columns)