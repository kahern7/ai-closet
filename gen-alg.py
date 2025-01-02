from deap import base, creator, tools, algorithms
import matplotlib.pyplot as plt
import random


class ClosetOptimizer:
    def __init__(self, width, height, columns, components, preferences):
        self.width = width
        self.height = height
        self.columns = columns
        self.column_width = width / columns
        self.components = components
        self.preferences = preferences

        # Create Fitness and Individual classes
        creator.create("FitnessMax", base.Fitness, weights=(1.0,))
        creator.create("Individual", list, fitness=creator.FitnessMax)

        # Define the toolbox
        self.toolbox = base.Toolbox()
        self.toolbox.register("attr_height", random.randint, 10, height)
        self.toolbox.register("individual", tools.initRepeat, creator.Individual, 
                               self.toolbox.attr_height, columns * len(components))
        self.toolbox.register("population", tools.initRepeat, list, self.toolbox.individual)
        self.toolbox.register("evaluate", self.evaluate)
        self.toolbox.register("mate", tools.cxTwoPoint)
        self.toolbox.register("mutate", tools.mutUniformInt, low=10, up=height, indpb=0.1)
        self.toolbox.register("select", tools.selTournament, tournsize=3)

    def evaluate(self, individual):
        total_space_used = sum(individual)
        component_allocation = {
            "drawers": sum(individual[0:self.columns]),
            "shelves": sum(individual[self.columns:2*self.columns]),
            "hanging": sum(individual[2*self.columns:])
        }

        # Calculate fitness based on adherence to user preferences
        fitness = 0
        for component, target_percentage in self.preferences.items():
            allocated_percentage = (component_allocation[component] / (self.columns * self.height)) * 100
            fitness -= abs(allocated_percentage - target_percentage)  # Penalise deviation

        # Ensure space does not exceed constraints
        if total_space_used > self.height * self.columns:
            fitness -= 100  # Heavy penalty for exceeding space

        return fitness,

    def optimise(self, population_size=50, generations=100, cxpb=0.5, mutpb=0.2):
        population = self.toolbox.population(n=population_size)
        algorithms.eaSimple(population, self.toolbox, cxpb, mutpb, generations, verbose=True)
        best_individual = tools.selBest(population, k=1)[0]
        return best_individual

    def map_individual_to_arrangement(self, individual):
        arrangement = {}
        num_components = len(self.components)
        for col in range(self.columns):
            for comp_index, component in enumerate(self.components):
                height = individual[col * num_components + comp_index]
                arrangement[(col, component)] = height
        return arrangement

    def visualise_closet(self, arrangement):
        fig, ax = plt.subplots(figsize=(10, 8))
        colors = {"drawers": "orange", "hanging": "blue", "shelves": "green"}
        column_positions = [((col + 0.5) * self.column_width - self.width / 2) for col in range(self.columns)]

        for col_index, x_position in enumerate(column_positions):
            y_start = 0
            for (column, component), height in arrangement.items():
                if column == col_index:
                    ax.bar(
                        x_position,
                        height,
                        width=self.column_width, # * 0.8,
                        bottom=y_start,
                        color=colors.get(component, "grey"),
                        edgecolor="black"
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
        plt.grid(visible=False)
        plt.show()


# Example usage
if __name__ == "__main__":
    # Closet parameters
    WIDTH = 100  # inches
    HEIGHT = 96  # inches
    COLUMNS = 4
    COMPONENTS = ["drawers", "shelves", "hanging"]

    # User preferences (% allocation)
    preferences = {"drawers": 50, "shelves": 30, "hanging": 20}

    optimizer = ClosetOptimizer(WIDTH, HEIGHT, COLUMNS, COMPONENTS, preferences)
    best_individual = optimizer.optimise()
    arrangement = optimizer.map_individual_to_arrangement(best_individual)
    optimizer.visualise_closet(arrangement)
