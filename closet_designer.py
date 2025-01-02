import matplotlib.pyplot as plt
import numpy as np

class ClosetDesigner:
    def __init__(self, width=100, height=96, columns=4):
        self.width = width
        self.height = height
        self.columns = columns
        self.column_width = width / columns
        self.grid = np.zeros((columns, int(height)))  # initialise an empty grid
        self.comp_size = {k: v for k, v in max_size.items()} # set size of each component

    def validate_percentages(self, percentages):
        if sum(percentages.values()) != 100:
            raise ValueError("Percentages must sum to 100.")
    
    def allocate_space(self, percentages):
        self.validate_percentages(percentages)
        allocations = {}
        total_height = self.height
        total_columns = self.columns

        for component, percentage in percentages.items():
            # int((percentage / 100) * total_height)
            allocations[component] = int((percentage / 100) * total_height * total_columns) # gives maxmimum height allowed for each component across all columns

        return allocations
    
    def allocate_comps(self, allocations, arrangement, comp_filter=None, col_range=None):
        # initialise variables
        if col_range is None:
            col_range = range(self.columns)
        if comp_filter is None:
            comp_filter = self.comp_finish
        comp_size = self.comp_size

        # allocate components to remaining space
        comp_dict = {k: v for k, v in allocations.items() if k in comp_filter} # create dict with required components
        for component, comp_height in comp_dict.items():
            self.comp_finish.remove(component) # set current component as finished
            for col in col_range:
                if comp_height - comp_size[component] > 0 and self.col_height[col] - comp_size[component] > 0: # check for component finished
                    allocation = comp_size[component] * (min(comp_height, self.col_height[col]) // comp_size[component])
                    arrangement[(col, component)] = allocation
                    comp_height -= allocation
                    self.col_height[col] -= allocation
        
        return arrangement

    def arrange_components(self, allocations):
        arrangement = {}
        middle_columns = ([0,1] if self.columns == 2 else [i for i in range(1, self.columns - 1)] or [0])  # find middle columns, if no middle then default to column 0 or 0,1 for 1 and 2 columns respectively
        self.col_height = {col: self.height for col in range(self.columns)}
        self.comp_finish = [k for k in allocations.keys()]
        
        # Allocate drawers to middle columns
        arrangement = self.allocate_comps(allocations, arrangement, "drawers", middle_columns)
        
        # Allocate other components to remaining space
        arrangement = self.allocate_comps(allocations, arrangement)
        
        return arrangement

    def design_closet(self, percentages):
        allocations = self.allocate_space(percentages)
        arrangement = self.arrange_components(allocations)
        return arrangement

    def visualise_closet(self, arrangement):
        fig, ax = plt.subplots(figsize=(10, 8))
        colors = {"drawers": "orange", "hanging": "blue", "shelves": "green"}
        col_width = self.column_width
        column_positions = [((col + 0.5) * col_width - self.width / 2) for col in range(self.columns)]

        for col_index, x_position in enumerate(column_positions):
            y_start = 0
            for (column, component), height in arrangement.items():
                if column == col_index:
                    ax.bar(
                        x_position,
                        height,
                        width=col_width, # * 0.8,  # Slightly narrow bars for better spacing
                        bottom=y_start,
                        color=colors.get(component, "grey"),
                        edgecolor="black",
                        label=component if y_start == 0 else ""
                    )
                    ax.text(
                        x_position,
                        y_start + height / 2,
                        f"{component}\n{height} in",
                        ha="center",
                        va="center",
                        color="white",
                        fontsize=10
                    )
                    y_start += height

        ax.set_xlim(-self.width / 2, self.width / 2)
        ax.set_ylim(0, self.height)
        ax.set_title("Closet Space Arrangement")
        ax.set_xlabel("Width (inches, centred)")
        ax.set_ylabel("Height (inches)")
        # ax.legend(loc="upper right")
        plt.grid(visible=False)
        plt.show()

# Example Usage
if __name__ == "__main__":
    percentages = {
        "drawers": 30,
        "hanging": 50,
        "shelves": 20
    }

    # set max size for each component (inches)
    max_size = {
        "drawers": 10,
        "hanging": 20,
        "shelves": 5
    }

    designer = ClosetDesigner()
    arrangement = designer.design_closet(percentages)
    designer.visualise_closet(arrangement)
