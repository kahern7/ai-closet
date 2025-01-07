import tkinter as tk

class ClosetOptimiserGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Closet Optimiser")

        # Paned window layout
        self.paned_window = tk.PanedWindow(root, orient="horizontal")
        self.paned_window.pack(fill="both", expand=True)

        # Left panel (Options Menu)
        self.options_frame = tk.Frame(self.paned_window, bg="lightgrey")
        self.paned_window.add(self.options_frame)

        # Right panel (Figures)
        self.figures_frame = tk.Frame(self.paned_window, bg="white")
        self.paned_window.add(self.figures_frame)

        # Add a test label to ensure visibility
        tk.Label(self.options_frame, text="Options Panel").pack()
        tk.Label(self.figures_frame, text="Figures Panel").pack()

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
            else:
                advanced_frame.pack(fill="x", pady=10)
                toggle_button.config(text="Hide Advanced Settings")

        # Space properties
        self.width = create_slider_with_input(self.options_frame, "Width (mm)", 500, 5000, 10, 2540)
        self.height = create_slider_with_input(self.options_frame, "Height (mm)", 788, 2176, 32, 2176)

        # Component preferences
        self.drawers = create_slider_with_input(self.options_frame, "Drawers (%)", 0, 50, 1, 0)
        self.short_hanging = create_slider_with_input(self.options_frame, "Short Hanging (%)", 0, 100, 1, 0)
        self.long_hanging = create_slider_with_input(self.options_frame, "Long Hanging (%)", 0, 100, 1, 0)

        # Advanced settings dropdown
        toggle_button = tk.Button(self.options_frame, text="Show Advanced Settings", command=toggle_advanced)
        toggle_button.pack(pady=10)

        advanced_frame = tk.LabelFrame(self.options_frame, text="Advanced Settings")
        self.pop_size = create_slider_with_input(advanced_frame, "Algorithm Population Size", 100, 5000, 100, 500)
        self.num_gens = create_slider_with_input(advanced_frame, "Algorithm Generations", 100, 1000, 100, 100)


if __name__ == "__main__":
    root = tk.Tk()
    app = ClosetOptimiserGUI(root)
    root.mainloop()