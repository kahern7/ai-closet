from deap import base, creator, tools, algorithms
import matplotlib.pyplot as plt
import random
from optimiser.constraints import ClosetConstraints
import inspect

class ClosetOptimiser:
    def __init__(self, width: int, height: int, preferences: dict[str, int], alg_pref: dict[str, int]) -> None:
        self.width: int = width
        self.height:int = height
        self.preferences: dict[str, int] = {k: v for k, v in preferences.items() if v > 0 or k == "shelves"}  # Filter out zero-preference components
        self.columns: int = 4
        self.components: list[str] = list(self.preferences.keys())  # Use filtered components
        self.min_heights: dict[str, int] = {  # Minimum heights for components
            "shelves": 32,
            "drawers": (7*32), # 224 mm
            "short_hanging": (29*32), # 928 mm
            "long_hanging": (47*32) # 1504 mm
        }
        self.alg_pref: dict[str, int] = alg_pref
        self.toolbox: base.Toolbox = self.setup_toolbox()
    
    def setup_toolbox(self) -> base.Toolbox:
        """Define the DEAP toolbox"""
        # Avoid overwriting exisiting class
        try:
            del creator.Individual
            del creator.FitnessMax
        except Exception as e:
            pass

        creator.create("FitnessMax", base.Fitness, weights=(1.0,))
        creator.create("Individual", list, fitness=creator.FitnessMax)

        toolbox: base.Toolbox = base.Toolbox()

        def attr_height(component: str) -> int:
            min_height: int = self.min_heights[component]
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
    
    def constrained_mutate(self, individual: list[int]) -> tuple[list[int]]:
        for i, height in enumerate(individual):
            component_index: int = i % len(self.components)
            component: str = self.components[component_index]
            min_height: int = self.min_heights[component]

            # Generate a new valid height as an integer multiple
            individual[i] = random.randint(0, int(self.height // min_height)) * min_height
        
        # # Debug: Check the mutated individual
        # print("Mutated Individual:", individual)

        return (individual,)

    def evaluate(self, individual: list[int]) -> int:
        """Evaluate fitness based on adherence to user preferences"""
        # create config dict and pass to ClosetConstraints class
        config: dict = {
            "width": self.width,
            "height": self.height,
            "preferences": self.preferences,
            "columns": self.columns,
            "components": self.components,
            "min_heights": self.min_heights,
        }
        cc = ClosetConstraints(config)
        fitness = 0
        # Dynamically find all constraint methods starting with "con_"
        for name, method in inspect.getmembers(cc, predicate=inspect.ismethod):
            if name.startswith(("con_")):
                fitness -= method(individual)

        return fitness,

    def optimise(self, population_size:int=None, generations:int=None, cxpb:float=0.5, mutpb:float=0.2) -> tuple[list[int], plt.Figure]:
        if population_size is None:
            population_size = int(self.alg_pref["Population"])
        if generations is None:
            generations = int(self.alg_pref["Generations"])
        population = self.toolbox.population(n=population_size)

        # Statistics for tracking performance
        stats: tools.Statistics = tools.Statistics(lambda ind: ind.fitness.values[0])
        stats.register("max", max)
        stats.register("avg", lambda fits: sum(fits) / len(fits))
        
        logbook: tools.Logbook = tools.Logbook()  # Logbook to store the evolution history
        logbook.header = ["gen", "max", "avg"]  # Columns for tracking

        # Evolutionary algorithm with tracking
        for gen in range(generations):
            offspring: list = algorithms.varAnd(population, self.toolbox, cxpb, mutpb)
            fits = self.toolbox.map(self.toolbox.evaluate, offspring)
            for ind, fit in zip(offspring, fits):
                ind.fitness.values = fit
            population[:] = self.toolbox.select(offspring, k=len(population))
            
            # Record stats for the current generation
            record: dict = stats.compile(population)
            logbook.record(gen=gen, **record)
        
        # Get the best solution
        best_individual: list[int] = tools.selBest(population, k=1)[0]
        fig: plt.Figure = self.plot_progress(logbook)

        return best_individual, fig
    
    def plot_progress(self, logbook: tools.Logbook) -> plt.Figure:
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

        return fig

    def map_individual_to_arrangement(self, individual: list[int]) -> dict:
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
    WIDTH: int = 100  # inches
    HEIGHT: int = 96  # inches
    COLUMNS: int = 4
    COMPONENTS: list[str] = ["drawers", "shelves", "hanging"]

    # User preferences (% allocation)
    preferences: dict[str: int] = {"drawers": 35, "shelves": 15, "hanging": 50}

    optimizer: ClosetOptimiser = ClosetOptimiser(WIDTH, HEIGHT, COLUMNS, COMPONENTS, preferences)
    best_individual: tuple[list[int], plt.Figure] = optimizer.optimise()
    arrangement: dict = optimizer.map_individual_to_arrangement(best_individual)
    # optimizer.visualise_closet(arrangement)
    plt.show()