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
            # Identify columns with drawers
            drawer_columns = [i for i, height in enumerate(drawer_heights) if height > 0]
            
            # ideal centred position of drawers
            ideal_positions = []
            num_drawer_columns = len(drawer_columns)
            if num_drawer_columns > 0:
                mid = self.columns // 2
                if num_drawer_columns % 2 == 0:
                    ideal_positions = list(range(mid - num_drawer_columns // 2, mid + num_drawer_columns // 2))
                else:
                    ideal_positions = list(range(mid - num_drawer_columns // 2, mid + num_drawer_columns // 2 + 1))
            
            # Penalise any deviation from ideal positions
            penalty += sum(
                10 * abs(pos - ideal_positions[i])
                for i, pos in enumerate(sorted(drawer_columns))
                if i < len(ideal_positions)
            )               
            return penalty
        
        penalty = 0
        
        penalty += drawer_equal_height(individual)
        penalty += drawer_centre(individual)
        
        return penalty
    
    """auxiliary functions"""
    
    def non_zero_elements_equal(self, lst: list[int]) -> bool:
        """Checks if non-zero elements in list are equal"""
        non_zero_elements = [x for x in lst if x != 0]
        return len(set(non_zero_elements)) <= 1 
    
if __name__ == "__main__":
    pass