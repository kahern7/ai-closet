from closet_designer import ClosetDesigner

if __name__ == "__main__":
    percentages = {
        "drawers": 30,
        "hanging": 50,
        "shelves": 20
    }

    # set max size for each component (inches)
    max_size = {
        "drawers": 10,
        "hanging": 20,
        "shelves": 5
    }

    designer = ClosetDesigner()
    arrangement = designer.design_closet(percentages)
    designer.visualise_closet(arrangement)