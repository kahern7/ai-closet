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
                arrangement[(col, "drawers")] = min(drawer_height, self.height)
                drawer_height -= self.height
        
        # Allocate other components to remaining space
        other_components = {k: v for k, v in allocations.items() if k != "drawers"}
        for component, height in other_components.items():
            for col in range(self.columns):
                if col not in middle_columns or height <= 0:
                    arrangement[(col, component)] = min(height, self.height)
                    height -= self.height
        
        return arrangement

    def design_closet(self, percentages):
        allocations = self.allocate_space(percentages)
        arrangement = self.arrange_components(allocations)
        return arrangement

# Example Usage
if __name__ == "__main__":
    percentages = {
        "drawers": 50,
        "hanging": 30,
        "shelves": 20
    }

    designer = ClosetDesigner()
    arrangement = designer.design_closet(percentages)

    # Print the arrangement
    for location, size in arrangement.items():
        print(f"Column {location[0]}, Component: {location[1]}, Height Allocated: {size} inches")
