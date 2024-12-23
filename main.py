from closet_designer import ClosetDesigner

if __name__ == "__main__":
    percentages = {
        "drawers": 50,
        "hanging": 30,
        "shelves": 20
    }

    designer = ClosetDesigner()
    arrangement = designer.design_closet(percentages)

    # Print the arrangement
    for location, size in arrangement.items():
        print(f"Column {location[0]}, Component: {location[1]}, Height Allocated: {size} inches")
