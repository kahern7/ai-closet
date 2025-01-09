import customtkinter as ctk
from optimiser.optimiser_core import ClosetOptimiser
from optimiser.visualiser import visualise_closet
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

class ClosetOptimiserGUI:
    def __init__(self, root: ctk.CTk) -> None:
        """Initialise customtkinter GUI."""
        self.root: ctk.CTk = root
        self.root.title("ClosetCAD AI Testbench")
        ctk.set_appearance_mode("light")  # 'light' or 'dark' mode
        ctk.set_default_color_theme("blue")  # Default theme

        # Set custom icon
        self.root.iconbitmap("images/favicon.ico")

        # Initial and minimum window sizing
        self.root.geometry("1200x600")
        self.root.minsize(400, 350)

        # Paned window layout
        self.paned_window: ctk.CTkFrame = ctk.CTkFrame(root)
        self.paned_window.pack(fill="both", expand=True)

        # Left panel (Options Menu)
        self.options_frame: ctk.CTkFrame = ctk.CTkFrame(self.paned_window)
        self.options_frame.pack_propagate(True)  # Prevent resizing based on content
        self.options_frame.pack(side="left", fill="y", padx=10, pady=10)

        # Right panel (Figures)
        self.figures_frame: ctk.CTkFrame = ctk.CTkFrame(self.paned_window)
        self.figures_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(self.options_frame, text="Options Panel", font=("Arial", 16)).pack(pady=5)
        ctk.CTkLabel(self.figures_frame, text="Figures Panel", font=("Arial", 16)).pack(pady=5)

        # Add UI elements to the options frame
        self.add_options_ui()

    def add_options_ui(self) -> None:
        """Create the UI components for user inputs."""
        def create_slider_with_input(parent: ctk.CTkFrame, label: str, from_: int, to: int, increment: int, default: int) -> ctk.IntVar:
            """Creates a slider with an entry box for manual input."""
            frame: ctk.CTkFrame = ctk.CTkFrame(parent)
            frame.pack(pady=5, fill="x")

            ctk.CTkLabel(frame, text=label).pack(side="left", padx=5)
            var: ctk.IntVar = ctk.IntVar(value=default)
            slider: ctk.CTkSlider = ctk.CTkSlider(
                frame, from_=from_, to=to, number_of_steps=int((to - from_) / increment), variable=var
            )
            slider.pack(side="left", expand=True, fill="x", padx=5)

            entry: ctk.CTkEntry = ctk.CTkEntry(frame, textvariable=var, width=50)
            entry.pack(side="left", padx=5)

            return var

        # Space properties
        self.width: ctk.IntVar = create_slider_with_input(self.options_frame, "Width (mm)", 500, 5000, 10, 2540)
        self.height: ctk.IntVar = create_slider_with_input(self.options_frame, "Height (mm)", 800, 2176, 32, 2176)

        # Component preferences
        self.drawers: ctk.IntVar = create_slider_with_input(self.options_frame, "Drawers (%)", 0, 50, 1, 0)
        self.short_hanging: ctk.IntVar = create_slider_with_input(self.options_frame, "Short Hanging (%)", 0, 100, 1, 0)
        self.long_hanging: ctk.IntVar = create_slider_with_input(self.options_frame, "Long Hanging (%)", 0, 100, 1, 0)

        # Advanced settings button
        toggle_button: ctk.CTkButton = ctk.CTkButton(self.options_frame, text="Show Advanced Settings", command=self.toggle_advanced)
        toggle_button.pack(pady=10)

        # Advanced settings menu and sliders
        self.advanced_frame: ctk.CTkFrame = ctk.CTkFrame(self.options_frame)
        self.pop_size: ctk.IntVar = create_slider_with_input(self.advanced_frame, "Algorithm Population Size", 100, 5000, 100, 500)
        self.num_gens: ctk.IntVar = create_slider_with_input(self.advanced_frame, "Algorithm Generations", 25, 500, 25, 50)

        # Optimise button
        ctk.CTkButton(self.options_frame, text="Optimise Closet", command=self.run_optimisation).pack(pady=10)

    def toggle_advanced(self):
        """Toggle the visibility of the advanced section."""
        if self.advanced_frame.winfo_ismapped():
            self.advanced_frame.pack_forget()
        else:
            self.advanced_frame.pack(fill="x", pady=10)

    def run_optimisation(self):
        """Run the optimisation and update the figures."""
        # Collect user inputs
        width: int = self.width.get()
        height: int = self.height.get()
        preferences: dict[str, int] = { # shelves must be last
            "drawers": int(self.drawers.get()),
            "short_hanging": int(self.short_hanging.get()),
            "long_hanging": int(self.long_hanging.get()),
            "shelves": int(100 - self.drawers.get() - self.short_hanging.get() - self.long_hanging.get()),
        }
        alg_pref: dict[str, int] = {
            "Population": int(self.pop_size.get()),
            "Generations": int(self.num_gens.get())
        }

        # Ensure user inputs are within required percentage range
        if preferences["shelves"] < 0:
            raise ValueError("Percentages must be less than or equal to 100")

        # Run optimisation
        optimiser: ClosetOptimiser = ClosetOptimiser(width, height, preferences, alg_pref)
        best_individual, progress_fig = optimiser.optimise()

        # Prepare output for visualisation
        arrangement: dict = optimiser.map_individual_to_arrangement(best_individual)
        closet_fig = visualise_closet(arrangement, width, height, optimiser.columns)

        self.update_figure([closet_fig, progress_fig], ["Closet Visualisation", "Optimisation Progress"])

    def update_figure(self, figures, titles):
        """Display the figures in tabs within the right panel."""
        # Clear existing content
        for widget in self.figures_frame.winfo_children():
            widget.destroy()

        # Create the tab control
        tab_control: ctk.CTkTabview = ctk.CTkTabview(self.figures_frame)
        tab_control.pack(fill="both", expand=True)

        for fig, title in zip(figures, titles):
            # Add a new tab with the title
            tab_control.add(title)
            frame: ctk.CTkFrame = tab_control.tab(title)

            # Embed the matplotlib figure
            canvas: FigureCanvasTkAgg = FigureCanvasTkAgg(fig, master=frame)
            canvas.draw()

            # Add NavigationToolbar2Tk
            toolbar: NavigationToolbar2Tk = NavigationToolbar2Tk(canvas, frame)
            toolbar.update()
            toolbar.pack()

            # Pack the canvas
            canvas.get_tk_widget().pack(fill="both", expand=True)

# Example usage
if __name__ == "__main__":
    app = ctk.CTk()
    gui = ClosetOptimiserGUI(app)
    app.mainloop()
