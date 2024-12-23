from closet_designer import ClosetDesigner

if __name__ == "__main__":
    percentages = {
        "drawers": 50,
        "hanging": 30,
        "shelves": 20
    }

    designer = ClosetDesigner()
    arrangement = designer.design_closet(percentages)
    designer.visualise_closet(arrangement)