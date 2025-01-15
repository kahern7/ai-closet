def drawer_centre(individual: list[int]) -> int:
    """function to penalise the algorithm for failing to centre the drawers

    Args:
        individual (list[int]): population individual containing components height ints

    Returns:
        int: penalty value to be subtracted from overall fitness of individual
    """
    COLUMNS = 4
    HEIGHT = 2174
    MIN_HEIGHT = 224
    INDEX = 0
    NUM_COMPONENTS = 2
    COMP_ALLOC = 25
    
    penalty = 0
    drawer_heights = [d for d in individual[INDEX::NUM_COMPONENTS]]
    
    # Penalise drawers exceeding total allowed height
    total_drawer_height = sum(drawer_heights)
    max_drawer_height_per_column = ((HEIGHT // 2) // MIN_HEIGHT + 1) * MIN_HEIGHT
    if total_drawer_height > COLUMNS * max_drawer_height_per_column:
        penalty += 100 + total_drawer_height - COLUMNS * max_drawer_height_per_column
        return penalty
    
    # Identify columns with drawers
    drawer_columns = [i for i, height in enumerate(drawer_heights) if height > 0]
    
    # Find minimum required columns based off percentage
    min_required_columns = ((COLUMNS * COMP_ALLOC * 2) + 99) // 100 # Ceiling division
    
    # ensure min required columns allow for symmetric columns
    mid = COLUMNS // 2
    if COLUMNS % 2 != min_required_columns % 2:
        min_required_columns + 1
    if COLUMNS % 2 == 0:
        ideal_positions = list(range((mid - 1) - ((min_required_columns - 1) // 2), (mid + (min_required_columns - 1) // 2) + 1))
    else:
        ideal_positions = list(range(mid - (min_required_columns // 2), mid + (min_required_columns // 2) + 1))
        
    # Penalise for deviation from ideal positions
    for actual_pos, ideal_pos in zip(drawer_columns, ideal_positions):
        penalty += abs(actual_pos - ideal_pos) * 10  # Penalise misalignment
    
    # Penalise extra drawer columns beyond the ideal count
    if len(drawer_columns) > len(ideal_positions):
        extra_drawer_columns = drawer_columns[len(ideal_positions):]
        penalty += len(extra_drawer_columns) * 50  # Heavy penalty for additional columns
    
    return penalty
        
if __name__ == "__main__":
    individual1 = [896, 2016, 1568, 672, 2048, 192, 1312, 1856]
    individual2 = [896, 608, 0, 1568, 224, 704, 896, 1568]
    penalty1 = drawer_centre(individual1)
    penalty2 = drawer_centre(individual2)
    print(f"penalty1: {penalty1}\npenalty2: {penalty2}")