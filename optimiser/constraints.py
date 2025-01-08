from optimiser_core import ClosetOptimiser as co

class ClosetConstraints:
    def __init__(self) -> None:
        pass

    def comp_percent_diff(self, individual: list[int], fitness: int) -> int:
        """Penalise discrepancy in component percentage"""
        # Find total height (mm) in closet taken up by each component (across all 4 columns)
        component_allocation: dict[str: int] = {
            component: sum(individual[co.columns * i : co.columns * (i + 1)])
            for i, component in enumerate(co.components)
        }
        for component, target_percentage in co.preferences.items():
            weight:int = 1
            if component == "shelves" and target_percentage == 0: # penalise model if it is filling drawers in over other components
                weight = 5
            allocated_percentage: int = (component_allocation[component] / (co.columns * co.height)) * 100
            fitness -= weight * abs(allocated_percentage - target_percentage)  # Penalise deviation
        return fitness
    
    def exceed_total_space(self, individual: list[int], fitness: int) -> int:
        """Ensure space does not exceed constraints and Penalise under utilisation of space"""
        total_space_used: int = sum(individual)
        unused_space: int = (co.height * co.columns) - total_space_used
        if unused_space < 0:
            fitness -= 100  # Heavy penalty for exceeding space
        else:
            fitness -= unused_space / 50
        return fitness
    
    def exceed_min_comp_height(self, individual: list[int], fitness: int) -> int:
        """Penalise any violation of minimum height constraint"""
        for col in range(co.columns):
            for comp_index, component in enumerate(co.components):
                height: int = individual[col * len(co.components) + comp_index]
                min_height: int = co.min_heights[component]
                if height == 0:
                    pass
                if height % min_height != 0:
                    fitness -= 100
        return fitness