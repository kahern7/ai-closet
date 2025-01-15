mid = 2
min_required_columns = 4

lower_bound = ((min_required_columns - 1) // 2)

upper_bound = ((min_required_columns - 1) // 2)

ideal_positions = list(range(mid - 1 - (min_required_columns - 1) // 2, mid + 1 + (min_required_columns - 1) // 2))

print(f"mid: {mid}\nmin_required_columns: {min_required_columns}\nlower_bound: {lower_bound}\nupper_bound: {upper_bound}\nideal_positions: {ideal_positions}")