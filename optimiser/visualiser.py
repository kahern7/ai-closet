import matplotlib.pyplot as plt

def visualise_closet(arrangement: dict, width: int, height: int, columns: int) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(10, 8))
    colors: dict[str: str] = {"drawers": "orange", "shelves": "green", "short_hanging": "blue", "long_hanging": "purple"}
    col_width: float = width / columns
    column_positions: list[float] = [((col + 0.5) * col_width - width / 2) for col in range(columns)]

    for col_index, x_position in enumerate(column_positions):
        y_start: int = 0
        comp_text: str = f""
        for (column, component), comp_height in arrangement.items():
            if column == col_index and comp_height > 0:
                ax.bar(
                    x_position,
                    comp_height,
                    width=col_width,
                    bottom=y_start,
                    color=colors.get(component, "grey"),
                    edgecolor="black"
                )
                if comp_height > 128: # put text on one line when comp is small
                    comp_text = f"{component}\n{comp_height} mm"
                else:
                    comp_text = f"{component} {comp_height} mm"
                ax.text(
                    x_position,
                    y_start + comp_height / 2,
                    comp_text,
                    ha="center",
                    va="center",
                    color="white",
                    fontsize=10
                )
                y_start += comp_height

    ax.set_xlim(-width / 2, width / 2)
    ax.set_ylim(0, height)
    ax.set_title("Closet Space Arrangement")
    ax.set_xlabel("Width (mm)")
    ax.set_ylabel("Height (mm)")
    plt.grid(visible=False)
    
    return fig