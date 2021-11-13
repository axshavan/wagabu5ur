#!/bin/python3

GRID_STEPX = 5
GRID_STEPY = 5


def grid(pixelmap, stepx:int = 0, stepy:int = 0) -> list:
    stepx = int(stepx)
    stepy = int(stepy)
    if stepx < 1:
        stepx = GRID_STEPX
    if stepy < 1:
        stepy = GRID_STEPY

    # ...

    return []
