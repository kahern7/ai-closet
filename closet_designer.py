import matplotlib.pyplot as plt
import numpy as np

class ClosetDesigner:
    def __init__(self, width=100, height=96, columns=4):
        self.width = width
        self.height = height
        self.columns = columns
        self.column_width = width / columns
        self.grid = np.zeros((columns, int(height)))  # Initialise an empty grid
        self.comp_size = {k: v for k, v in max_size.items()}

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
    
    # def allocate_comps(self, allocations, arrangement, col_height, comp_filter=None, col_range=None):
    #     # initialise variables
    #     if col_range is None:
    #         col_range = range(self.columns)
    #     comp_size = self.comp_size

    #     # allocate components to remaining space
    #     comp_dict = {k: v for k, v in allocations.items() if k != comp_filter}
    #     for component, comp_height in comp_dict.items():
    #         for col in col_range:
    #             if comp_height - comp_size[component] > 0 and col_height[col] - comp_size[component] > 0:
    #                 allocation = comp_size[component] * (min(comp_height, col_height[col]) // comp_size[component])
    #                 arrangement[(col, component)] = allocation
    #                 comp_height -= allocation
    #                 col_height[col] -= allocation
        
    #     return arrangement

    def arrange_components(self, allocations):
        arrangement = {}
        middle_columns = [1, 2]  # Middle columns in a 4-column layout
        col_height = {col: self.height for col in range(self.columns)}
        comp_size = self.comp_size
        
        # Allocate drawers to middle columns
        drawer_height = allocations.get("drawers", 0)
        for col in middle_columns:
            # ensure drawer allocation and column allocation available
            if drawer_height - comp_size["drawers"] > 0 and col_height[col] - comp_size["drawers"] > 0:
                # allocation is max number of comps permissible in space
                allocation = comp_size["drawers"] * (min(drawer_height, col_height[col]) // comp_size["drawers"])
                arrangement[(col, "drawers")] = allocation
                drawer_height -= allocation
                col_height[col] -= allocation
        
        # Allocate other components to remaining space
        other_components = {k: v for k, v in allocations.items() if k != "drawers"}
        for component, comp_height in other_components.items():
            for col in range(self.columns):
                if comp_height - comp_size[component] > 0 and col_height[col] - comp_size[component] > 0:
                    allocation = comp_size[component] * (min(comp_height, col_height[col]) // comp_size[component])
                    arrangement[(col, component)] = allocation
                    comp_height -= allocation
                    col_height[col] -= allocation
        
        return arrangement

    def design_closet(self, percentages):
        allocations = self.allocate_space(percentages)
        arrangement = self.arrange_components(allocations)
        return arrangement

    def visualise_closet(self, arrangement):
        fig, ax = plt.subplots(figsize=(10, 8))
        colors = {"drawers": "orange", "hanging": "blue", "shelves": "green"}
        col_width = self.column_width
        if self.columns % 2 == 0:
            column_positions = [((col + 0.5) * col_width - self.width / 2) for col in range(self.columns)] # even number of columns requires middle columns to be offset from 0
        else:
            column_positions = [(col * col_width - self.width / 2) for col in range(self.columns)]

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
