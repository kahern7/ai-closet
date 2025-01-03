from deap import base, creator, tools, algorithms
import matplotlib.pyplot as plt
import random


class ClosetOptimiser:
    def __init__(self, width, height, preferences):
        self.width = width
        self.height = height
        self.preferences = preferences
        self.columns = 4
        self.components = ["shelves", "drawers", "short_hanging", "long_hanging"]
        self.toolbox = self.setup_toolbox()
    
    def setup_toolbox(self):
        # Define the DEAP toolbox here
        creator.create("FitnessMax", base.Fitness, weights=(1.0,))
        creator.create("Individual", list, fitness=creator.FitnessMax)

        toolbox = base.Toolbox()
        toolbox.register("attr_height", random.randint, 10, self.height)
        toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_height, self.columns * len(self.components))
        toolbox.register("population", tools.initRepeat, list, toolbox.individual)
        toolbox.register("evaluate", self.evaluate)
        toolbox.register("mate", tools.cxTwoPoint)
        toolbox.register("mutate", tools.mutUniformInt, low=10, up=self.height, indpb=0.1)
        toolbox.register("select", tools.selTournament, tournsize=3)
        return toolbox

    def evaluate(self, individual):
        # calculate fitness
        total_space_used = sum(individual)
        component_allocation = {
            "drawers": sum(individual[:self.columns]),
            "shelves": sum(individual[self.columns:2*self.columns]),
            "short_hanging": sum(individual[2*self.columns:3*self.columns]),
            "long_hanging": sum(individual[3*self.columns:])
        }

        # Calculate fitness based on adherence to user preferences
        fitness = 0
        for component, target_percentage in self.preferences.items():
            allocated_percentage = (component_allocation[component] / (self.columns * self.height)) * 100
            fitness -= abs(allocated_percentage - target_percentage)  # Penalise deviation

        # Ensure space does not exceed constraints
        if total_space_used > self.height * self.columns:
            fitness -= 100  # Heavy penalty for exceeding space

        # Ensure space does not exceed constraints for each column
        for col in range(self.columns):
            column_height = sum(individual[col::self.columns])
            if column_height > self.height:
                fitness -= 100  # Penalise exceeding column space heavily

        return fitness,

    def optimise(self, population_size=50, generations=100, cxpb=0.5, mutpb=0.2):
        population = self.toolbox.population(n=population_size)
        
        # Statistics for tracking performance
        stats = tools.Statistics(lambda ind: ind.fitness.values[0])
        stats.register("max", max)
        stats.register("avg", lambda fits: sum(fits) / len(fits))
        
        logbook = tools.Logbook()  # Logbook to store the evolution history
        logbook.header = ["gen", "max", "avg"]  # Columns for tracking

        # Evolutionary algorithm with tracking
        for gen in range(generations):
            offspring = algorithms.varAnd(population, self.toolbox, cxpb, mutpb)
            fits = self.toolbox.map(self.toolbox.evaluate, offspring)
            for ind, fit in zip(offspring, fits):
                ind.fitness.values = fit
            population[:] = self.toolbox.select(offspring, k=len(population))
            
            # Record stats for the current generation
            record = stats.compile(population)
            logbook.record(gen=gen, **record)
        
        # Get the best solution
        best_individual = tools.selBest(population, k=1)[0]
        self.plot_progress(logbook)  # Plot progress after the evolution
        return best_individual
    
    def plot_progress(self, logbook):
        generations = logbook.select("gen")
        max_fitness = logbook.select("max")
        avg_fitness = logbook.select("avg")

        plt.figure(1, figsize=(10, 6))
        plt.clf()
        plt.plot(generations, max_fitness, label="Max Fitness", color="blue")
        plt.plot(generations, avg_fitness, label="Average Fitness", color="green")
        plt.title("Algorithm Progress")
        plt.xlabel("Generations")
        plt.ylabel("Fitness")
        plt.legend(loc="best")
        plt.grid(True)

    def map_individual_to_arrangement(self, individual):
        """Convert the individual into a dictionary mapping columns to components and their heights."""
        arrangement = {}
        num_components = len(self.components)

        if len(individual) != self.columns * num_components:
            raise ValueError(
                f"Mismatch between individual length ({len(individual)}) and expected size ({self.columns * num_components})."
            )

        for col in range(self.columns):
            for comp_index, component in enumerate(self.components):
                # Safely calculate the index
                index = col * num_components + comp_index
                if index < len(individual):
                    height = individual[index]
                    arrangement[(col, component)] = height

        return arrangement

# Example usage
if __name__ == "__main__":
    # Closet parameters
    WIDTH = 100  # inches
    HEIGHT = 96  # inches
    COLUMNS = 4
    COMPONENTS = ["drawers", "shelves", "hanging"]

    # User preferences (% allocation)
    preferences = {"drawers": 35, "shelves": 15, "hanging": 50}

    optimizer = ClosetOptimiser(WIDTH, HEIGHT, COLUMNS, COMPONENTS, preferences)
    best_individual = optimizer.optimise()
    arrangement = optimizer.map_individual_to_arrangement(best_individual)
    # optimizer.visualise_closet(arrangement)
    plt.show()