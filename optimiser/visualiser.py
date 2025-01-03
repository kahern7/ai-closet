import matplotlib.pyplot as plt

def map_individual_to_arrangement(individual, columns, preferences):
    arrangement = {}
    num_components = len(preferences.keys())
    for col in range(columns):
        for comp_index, component in enumerate(preferences.keys()):
            height = individual[col * num_components + comp_index]
            arrangement[(col, component)] = height
    return arrangement

def visualise_closet(best_arrangement, width, height, columns, preferences):
    arrangement = map_individual_to_arrangement(best_arrangement, columns, preferences)
    fig, ax = plt.subplots(figsize=(10, 8))
    colours = {"drawers": "orange", "shelves": "green", "short_hanging": "blue", "long_hanging": "purple"}
    col_width = width / columns
    column_positions = [(col + 0.5) * col_width - width / 2 for col in range(columns)]

    for (column, component), comp_height in arrangement.items():
        x_position = column_positions[column]
        ax.bar(
            x_position,
            comp_height,
            width=col_width * 0.8,
            bottom=0,
            colour=colours.get(component, "grey"),
            edgecolour="black",
        )

    ax.set_xlim(-width / 2, width / 2)
    ax.set_ylim(0, height)
    plt.title("Optimised Closet Arrangement")
    plt.xlabel("Width (inches)")
    plt.ylabel("Height (inches)")
    plt.show()
