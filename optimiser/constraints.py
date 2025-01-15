class ClosetConstraints:
    """All constraint funcs start with con_"""
    def __init__(self, config: dict) -> None:
        self.width = config["width"]
        self.height = config["height"]
        self.preferences = config["preferences"]
        self.columns = config["columns"]
        self.components = config["components"]
        self.min_heights = config["min_heights"]

    """Basic space constraints"""
    
    def con_comp_percent_diff(self, individual: list[int]) -> int:
        """Penalise discrepancy in component percentage"""
        penalty = 0
        # Find total height (mm) in closet taken up by each component (across all 4 columns)
        component_allocation: dict[str: int] = {
            component: sum(individual[i :: len(self.components)])
            for i, component in enumerate(self.components)
        }
        
        for component, target_percentage in self.preferences.items():
            # if component == "shelves": 
            #     pass # skip penalty for shelves as it adapts to reminaing space
            # else:
            allocated_percentage: int = (component_allocation[component] / (self.columns * self.height)) * 100
            penalty += abs(allocated_percentage - target_percentage)  # Penalise deviation
        
        return penalty
    
    def con_exceed_total_space(self, individual: list[int]) -> int:
        """Ensure space does not exceed constraints and Penalise under utilisation of space"""
        penalty = 0
        total_space_used: int = sum(individual)
        unused_space: int = (self.height * self.columns) - total_space_used
        if unused_space < 0:
            penalty += 100  # Heavy penalty for exceeding total space
        elif unused_space > 0:
            penalty += unused_space
        return penalty
    
    def con_exceed_col_height(self, individual: list[int]) -> int:
        """Ensure space does not exceed constraints for each column"""
        penalty = 0
        num_components: int = len(self.preferences.keys())
        for col in range(self.columns):
            column_height: int = sum(individual[(col * num_components):((col + 1) * num_components)])
            if column_height > self.height:
                penalty += 100 + (column_height - self.height)  # Penalise exceeding column space heavily
        return penalty
    
    def con_exceed_min_comp_height(self, individual: list[int]) -> int:
        """Penalise any violation of minimum height constraint"""
        penalty = 0
        for col in range(self.columns):
            for comp_index, component in enumerate(self.components):
                height: int = individual[col * len(self.components) + comp_index]
                min_height: int = self.min_heights[component]
                if height == 0:
                    pass
                elif height % min_height != 0:
                    penalty += 100
        return penalty
    
    """Component Constraints"""
    
    """Drawer constraints"""
    def con_drawers(self, individual: list[int]) -> int:        
        """General function for all drawer constraints"""
        if "drawers" not in self.components: # check that drawers exist
            return 0
        
        def drawer_equal_height(individual: list[int]) -> int:
            """Ensure drawers are equal height"""
            penalty = 0
            drawer_heights = [d for d in individual[self.components.index("drawers")::len(self.components)] if d > 0]
            if len(drawer_heights) > 1:
                avg_height = sum(drawer_heights) / len(drawer_heights)
                penalty = sum(abs(height - avg_height) for height in drawer_heights) / 10
            return penalty
        
        def drawer_centre(individual: list[int]) -> int:
            """Encourage drawers to be centred"""
            penalty = 0
            drawer_heights = [d for d in individual[self.components.index("drawers")::len(self.components)]]
            
            # Find minimum required columns based off percentage
            min_required_columns = ((self.columns * self.preferences["drawers"] * 2) + 99) // 100 # Ceiling division
            
            # ensure min required columns allow for symmetric columns
            mid = self.columns // 2
            if self.columns % 2 != min_required_columns % 2:
                min_required_columns + 1
            if self.columns % 2 == 0:
                ideal_positions = list(range((mid - 1) - ((min_required_columns - 1) // 2), (mid + (min_required_columns - 1) // 2) + 1))
            else:
                ideal_positions = list(range(mid - (min_required_columns // 2), mid + (min_required_columns // 2) + 1))
            
            # Identify columns with drawers
            drawer_columns = [i for i, height in enumerate(drawer_heights) if height > 0]
            
            # Penalise for deviation from ideal positions
            for actual_pos, ideal_pos in zip(drawer_columns, ideal_positions):
                penalty += abs(actual_pos - ideal_pos) * 10  # Penalise misalignment
            
            # Penalise extra drawer columns beyond the ideal count
            if len(drawer_columns) > len(ideal_positions):
                extra_drawer_columns = drawer_columns[len(ideal_positions):]
                penalty += len(extra_drawer_columns) * 50  # Heavy penalty for additional columns
            
            return penalty
        
        def drawer_full_utilisation(individual: list[int]) -> int:
            """Ensure drawers fully utilise allocated space."""
            penalty = 0
            drawer_heights = [individual[i::len(self.components)][self.components.index("drawers")] for i in range(self.columns)]
            max_drawer_height_per_column = ((self.height // 2) // self.min_heights["drawers"] + 1) * self.min_heights["drawers"]

            # Penalise exceeding drawer space in each drawer column
            for height in drawer_heights:
                if height > max_drawer_height_per_column:
                    unused_space = height - max_drawer_height_per_column
                    penalty += unused_space * 5  # Adjust weight as needed

            return penalty

        
        # Main drawer script
        penalty = 0
        
        penalty += drawer_equal_height(individual)
        penalty += drawer_centre(individual)
        penalty += drawer_full_utilisation(individual)
        
        return penalty
    
    """auxiliary functions"""
    
    def non_zero_elements_equal(self, lst: list[int]) -> bool:
        """Checks if non-zero elements in list are equal"""
        non_zero_elements = [x for x in lst if x != 0]
        return len(set(non_zero_elements)) <= 1 
    
if __name__ == "__main__":
    pass