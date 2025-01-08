class ClosetConstraints:
    """All constraint funcs start with con_"""
    def __init__(self, config: dict) -> None:
        self.width = config["width"]
        self.height = config["height"]
        self.preferences = config["preferences"]
        self.columns = config["columns"]
        self.components = config["components"]
        self.min_heights = config["min_heights"]

    def con_comp_percent_diff(self, individual: list[int]) -> int:
        """Penalise discrepancy in component percentage"""
        penalty = 0
        # Find total height (mm) in closet taken up by each component (across all 4 columns)
        component_allocation: dict[str: int] = {
            component: sum(individual[self.columns * i : self.columns * (i + 1)])
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
        else:
            penalty += unused_space / 50
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
    
if __name__ == "__main__":
    pass