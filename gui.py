from optimiser.optimiser_core import ClosetOptimiser
from optimiser.visualiser import visualise_closet
import tkinter as tk

class ClosetOptimiserGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Closet Optimiser")

        # Helper functions
        def create_slider_with_input(parent, label, from_, to, increment, default):
            """Creates a slider with an entry box for manual input."""
            frame = tk.Frame(parent)
            frame.pack(pady=5, fill="x")

            tk.Label(frame, text=label).pack(side="left", padx=5)

            var = tk.DoubleVar(value=default)

            slider = tk.Scale(
                frame, from_=from_, to=to, resolution=increment,
                orient="horizontal", variable=var
            )
            slider.pack(side="left", expand=True, fill="x", padx=5)

            entry = tk.Entry(frame, textvariable=var, width=6)
            entry.pack(side="left", padx=5)

            # Update slider when entry is changed
            entry.bind("<FocusOut>", lambda e: update_slider(entry.get(), slider, var))
            entry.bind("<Return>", lambda e: update_slider(entry.get(), slider, var))

            # Update entry when slider is changed
            slider.config(command=lambda v: update_entry(v, var))

            return var

        def update_slider(value, slider, var):
            """Update slider position when entry value changes."""
            try:
                val = int(value)
                if slider.cget('from') <= val <= slider.cget('to'):
                    slider.set(val)
            except ValueError:
                pass

        def update_entry(value, entry_var):
            """Update entry value when slider changes."""
            entry_var.set(f"{int(value):d}")

        def toggle_advanced():
            """Toggle the visibility of the advanced section."""
            if advanced_frame.winfo_ismapped():
                advanced_frame.pack_forget()
                toggle_button.config(text="Show Advanced Settings")
            else:
                advanced_frame.pack(fill="x", pady=10)
                toggle_button.config(text="Hide Advanced Settings")

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

        # Space properties
        self.width = create_slider_with_input(root, "Width (mm)", 500, 5000, 10, 2540)
        self.height = create_slider_with_input(root, "Height (mm)", 788, 2176, 32, 2176)

        # Component preferences
        self.drawers = create_slider_with_input(root, "Drawers (%)", 0, 50, 1, 0)
        self.short_hanging = create_slider_with_input(root, "Short Hanging (%)", 0, 100, 1, 0)
        self.long_hanging = create_slider_with_input(root, "Long Hanging (%)", 0, 100, 1, 0)

        # Advanced settings dropdown
        toggle_button = tk.Button(root, text="Show Advanced Settings", command=toggle_advanced)
        toggle_button.pack(pady=10)


        advanced_frame = tk.LabelFrame(root, text="Advanced Settings")
        self.pop_size = create_slider_with_input(advanced_frame, "Algorithm Population Size", 100, 5000, 100, 500)
        self.num_gens = create_slider_with_input(advanced_frame, "Algorithm Generations", 100, 1000, 100, 100)

        # Optimise button
        tk.Button(root, text="Optimise Closet", command=self.run_optimisation).pack(pady=10)

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
        alg_pref = {
            "Population": self.pop_size.get(),
            "Generations": self.num_gens.get()
        }

        if preferences["shelves"] < 0:
            raise ValueError("Percentages must be less than or equal to 100")

        # Run optimisation
        optimiser = ClosetOptimiser(width, height, preferences, alg_pref)
        best_individual = optimiser.optimise()

        # Visualise results
        arrangement = optimiser.map_individual_to_arrangement(best_individual)
        visualise_closet(arrangement, width, height, optimiser.columns)