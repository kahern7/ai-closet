from optimiser.optimiser_core import ClosetOptimiser
from optimiser.visualiser import visualise_closet
import tkinter as tk
from tkinter import ttk
from tkinter import PhotoImage
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.pyplot as plt

class ClosetOptimiserGUI:
    def __init__(self, root):
        """Initalise tkinter GUI """
        self.root = root
        self.root.title("ClosetCAD AI Testbench")

        # set custom icon
        self.root.iconbitmap("images/favicon.ico")
        icon = PhotoImage(file="images/logo_256x256.png")
        self.root.iconphoto(True, icon)

        # Initial and minimum window sizing
        self.root.geometry("1200x600")
        self.root.minsize(600, 400)

        # Paned window layout
        self.paned_window = tk.PanedWindow(root, orient="horizontal", sashrelief="raised")
        self.paned_window.pack(fill="both", expand=True)

        # Left panel (Options Menu)
        self.options_frame = tk.Frame(self.paned_window, bg='lightgrey')
        self.options_frame.pack_propagate(False)  # Prevent resizing based on content
        self.paned_window.add(self.options_frame, minsize=350)

        # Right panel (Figures)
        self.figures_frame = tk.Frame(self.paned_window, bg="white")
        self.options_frame.pack_propagate(True)
        self.paned_window.add(self.figures_frame, stretch="always")

        tk.Label(self.options_frame, text="Options Panel").pack()
        tk.Label(self.figures_frame, text="Figures Panel").pack()

        # Add UI elements to the options frame
        self.add_options_ui()

    def add_options_ui(self):
        """Create the UI components for user inputs."""
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
                # self.root.geometry("1200x600")  # Restore default window size
            else:
                advanced_frame.pack(fill="x", pady=10)
                toggle_button.config(text="Hide Advanced Settings")
                # self.root.geometry("1200x600")  # Expand window to fit advanced settings

        # Space properties
        self.width = create_slider_with_input(self.options_frame, "Width (mm)", 500, 5000, 10, 2540)
        self.height = create_slider_with_input(self.options_frame, "Height (mm)", 788, 2176, 32, 2176)

        # Component preferences
        self.drawers = create_slider_with_input(self.options_frame, "Drawers (%)", 0, 50, 1, 0)
        self.short_hanging = create_slider_with_input(self.options_frame, "Short Hanging (%)", 0, 100, 1, 0)
        self.long_hanging = create_slider_with_input(self.options_frame, "Long Hanging (%)", 0, 100, 1, 0)

        # Advanced settings button
        toggle_button = tk.Button(self.options_frame, text="Show Advanced Settings", command=toggle_advanced)
        toggle_button.pack(pady=10)

        # Advanced settings menu and sliders
        advanced_frame = tk.LabelFrame(self.options_frame, text="Advanced Settings")
        self.pop_size = create_slider_with_input(advanced_frame, "Algorithm Population Size", 100, 5000, 100, 500)
        self.num_gens = create_slider_with_input(advanced_frame, "Algorithm Generations", 100, 1000, 100, 100)

        # Optimise button
        tk.Button(self.options_frame, text="Optimise Closet", command=self.run_optimisation).pack(pady=10)

    def run_optimisation(self):
        """Run the optimisation and update the figures."""
        # Collect user inputs
        width = self.width.get()
        height = self.height.get()
        preferences = {
            "shelves": int(100 - self.drawers.get() - self.short_hanging.get() - self.long_hanging.get()),
            "drawers": int(self.drawers.get()),
            "short_hanging": int(self.short_hanging.get()),
            "long_hanging": int(self.long_hanging.get()),
        }
        alg_pref = {
            "Population": int(self.pop_size.get()),
            "Generations": int(self.num_gens.get())
        }

        # Ensure user inputs are within required percentage range
        if preferences["shelves"] < 0:
            raise ValueError("Percentages must be less than or equal to 100")

        # Run optimisation
        optimiser = ClosetOptimiser(int(width), int(height), preferences, alg_pref)
        best_individual, progress_fig = optimiser.optimise()

        # Prepare output for visualisation
        arrangement = optimiser.map_individual_to_arrangement(best_individual)
        closet_fig = visualise_closet(arrangement, width, height, optimiser.columns)

        self.update_figure([closet_fig, progress_fig], ["Closet Visualisation", "Optimisation Progress"])

    def update_figure(self, figures, titles):
        """Display the figures in tabs within the right panel."""
        for widget in self.figures_frame.winfo_children():
            widget.destroy()

        tab_control = ttk.Notebook(self.figures_frame)
        tab_control.pack(fill="both", expand=True)

        for fig, title in zip(figures, titles):
            frame = ttk.Frame(tab_control)
            tab_control.add(frame, text=title)
            canvas = FigureCanvasTkAgg(fig, master=frame)
            canvas.draw()

            # create an pack NavigationToolbar2Tk
            toolbar = NavigationToolbar2Tk(canvas, frame)
            toolbar.update()
            toolbar.pack()
            
            # Pack tge canvas for the plot
            canvas.get_tk_widget().pack(fill="both", expand=True)

"""Example Usage"""
if __name__ == "__main__":
    root = tk.Tk()
    app = ClosetOptimiserGUI(root)
    root.mainloop()