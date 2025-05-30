from deap import base, creator, tools, algorithms
import matplotlib.pyplot as plt
import random


class ClosetOptimiser:
    def __init__(self, width, height, preferences, alg_pref):
        self.width = width
        self.height = height
        self.preferences = {k: v for k, v in preferences.items() if v > 0}  # Filter out zero-preference components
        self.columns = 4
        self.components = list(self.preferences.keys())  # Use filtered components
        self.min_heights = {  # Minimum heights for components
            "shelves": 32,
            "drawers": (7*32), # 224 mm
            "short_hanging": (29*32), # 928 mm
            "long_hanging": (47*32) # 1504 mm
        }
        self.alg_pref = alg_pref
        self.toolbox = self.setup_toolbox()
    
    def setup_toolbox(self):
        """Define the DEAP toolbox"""
        # Avoid overwriting exisiting class
        try:
            del creator.Individual
            del creator.FitnessMax
        except Exception as e:
            pass

        creator.create("FitnessMax", base.Fitness, weights=(1.0,))
        creator.create("Individual", list, fitness=creator.FitnessMax)

        toolbox = base.Toolbox()

        def attr_height(component):
            min_height = self.min_heights[component]
            return random.randint(0, int(self.height // min_height)) * min_height

        toolbox.register(
            "individual",
            lambda: creator.Individual(
                [attr_height(component) for component in self.components for _ in range(self.columns)]
            )
        )

        toolbox.register("population", tools.initRepeat, list, toolbox.individual)
        toolbox.register("evaluate", self.evaluate)
        toolbox.register("mate", tools.cxTwoPoint)
        toolbox.register("mutate", self.constrained_mutate) # use new custom mutation func for minimum comp heights
        toolbox.register("select", tools.selTournament, tournsize=3)

        # Legacy traits
        # toolbox.register("attr_height", random.randint, 10, self.height)
        # toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_height, self.columns * len(self.components))
        # toolbox.register("mutate", tools.mutUniformInt, low=10, up=self.height, indpb=0.1)

        return toolbox
    
    def constrained_mutate(self, individual):
        for i, height in enumerate(individual):
            component_index = i % len(self.components)
            component = self.components[component_index]
            min_height = self.min_heights[component]

            # Generate a new valid height as an integer multiple
            individual[i] = random.randint(0, int(self.height // min_height)) * min_height
        
        # # Debug: Check the mutated individual
        # print("Mutated Individual:", individual)

        return (individual,)

    def evaluate(self, individual):
        """Evaluate fitness based on adherence to user preferences"""
        fitness = 0
        
        # Calculate total space taken up by component
        total_space_used = sum(individual)
        component_allocation = {
            component: sum(individual[self.columns * i : self.columns * (i + 1)])
            for i, component in enumerate(self.components)
        }

        # Penalise discrepancy in component percentage
        for component, target_percentage in self.preferences.items():
            allocated_percentage = (component_allocation[component] / (self.columns * self.height)) * 100
            fitness -= abs(allocated_percentage - target_percentage)  # Penalise deviation

        # Ensure space does not exceed constraints and Penalise under utilisation of space
        unused_space = (self.height * self.columns) - total_space_used
        if unused_space < 0:
            fitness -= 100  # Heavy penalty for exceeding space
        else:
            fitness -= unused_space / 50

        # Ensure space does not exceed constraints for each column
        num_components = len(self.preferences.keys())
        for col in range(self.columns):
            column_height = sum(individual[(col * num_components):((col + 1) * num_components)]) # [col::self.columns] seems to not work
            if column_height > self.height:
                fitness -= 100 + (column_height - self.height)  # Penalise exceeding column space heavily

        # Penalise any violation of minimum height constraint
        for col in range(self.columns):
            for comp_index, component in enumerate(self.components):
                height = individual[col * len(self.components) + comp_index]
                min_height = self.min_heights[component]
                if height == 0:
                    pass
                if height % min_height != 0:
                    fitness -= 100

        return fitness,

    def optimise(self, population_size=None, generations=None, cxpb=0.5, mutpb=0.2):
        if population_size is None:
            population_size = int(self.alg_pref["Population"])
        if generations is None:
            generations = int(self.alg_pref["Generations"])
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
        fig = self.plot_progress(logbook)

        return best_individual, fig
    
    def plot_progress(self, logbook):
        generations = logbook.select("gen")
        max_fitness = logbook.select("max")
        avg_fitness = logbook.select("avg")

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(generations, max_fitness, label="Max Fitness", color="blue")
        ax.plot(generations, avg_fitness, label="Average Fitness", color="green")
        ax.set_title("Algorithm Progress")
        ax.set_xlabel("Generations")
        ax.set_ylabel("Fitness")
        ax.legend(loc="best")
        ax.grid(True)

        return fig  # Return the figure

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