import matplotlib.pyplot as plt
import numpy as np

class ClosetDesigner:
    def __init__(self, width=100, height=96, columns=4):
        self.width = width
        self.height = height
        self.columns = columns
        self.column_width = width / columns
        self.grid = np.zeros((columns, int(height)))  # Initialise an empty grid

    def validate_percentages(self, percentages):
        if sum(percentages.values()) != 100:
            raise ValueError("Percentages must sum to 100.")
    
    def allocate_space(self, percentages):
        self.validate_percentages(percentages)
        allocations = {}
        total_height = self.height

        for component, percentage in percentages.items():
            allocations[component] = int((percentage / 100) * total_height)
        
        return allocations

    def arrange_components(self, allocations):
        arrangement = {}
        middle_columns = [1, 2]  # Middle columns in a 4-column layout
        
        # Allocate drawers to middle columns
        drawer_height = allocations.get("drawers", 0)
        if drawer_height > 0:
            for col in middle_columns:
                allocation = min(drawer_height, self.height)
                arrangement[(col, "drawers")] = allocation
                drawer_height -= allocation
        
        # Allocate other components to remaining space
        other_components = {k: v for k, v in allocations.items() if k != "drawers"}
        for component, height in other_components.items():
            for col in range(self.columns):
                if height > 0:
                    allocation = min(height, self.height)
                    arrangement[(col, component)] = allocation
                    height -= allocation
        
        return arrangement

    def design_closet(self, percentages):
        allocations = self.allocate_space(percentages)
        arrangement = self.arrange_components(allocations)
        return arrangement

    def visualise_closet(self, arrangement):
        fig, ax = plt.subplots(figsize=(8, 8))
        colors = {"drawers": "orange", "hanging": "blue", "shelves": "green"}
        col_width = self.column_width

        for col in range(self.columns):
            y_start = 0
            for (column, component), height in arrangement.items():
                if column == col:
                    ax.bar(
                        col * col_width,
                        height,
                        width=col_width,
                        bottom=y_start,
                        color=colors.get(component, "grey"),
                        edgecolor="black",
                        label=component if y_start == 0 else ""
                    )
                    ax.text(
                        col * col_width + col_width / 2,
                        y_start + height / 2,
                        f"{component}\n{height} in",
                        ha="center",
                        va="center",
                        color="white",
                        fontsize=10
                    )
                    y_start += height

        ax.set_xlim(0, self.width)
        ax.set_ylim(0, self.height)
        ax.set_title("Closet Space Arrangement")
        ax.set_xlabel("Width (inches)")
        ax.set_ylabel("Height (inches)")
        ax.legend(loc="upper right")
        plt.grid(visible=True, linestyle="--", linewidth=0.5)
        plt.show()

# Example Usage
if __name__ == "__main__":
    percentages = {
        "drawers": 50,
        "hanging": 30,
        "shelves": 20
    }

    designer = ClosetDesigner()
    arrangement = designer.design_closet(percentages)
    designer.visualise_closet(arrangement)