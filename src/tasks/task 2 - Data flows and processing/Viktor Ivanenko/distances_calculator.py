# Created by Viktor Ivanenko
from geopy import distance
import numpy as np

def distance_calculator(*args):

    """ Takes all the route locations points coordinates and returns summary distance. 
    Could deal with unlimited points. 
    Points coordinates should be inputed within a list argument."""

    list_args = []
    list_args.append(*args)
    indx=len(*args)
    dist_list = []
    for ind in range(indx):
        if ind > 0:
            dist = distance.distance(list_args[0][ind-1], list_args[0][ind])
            dist_list.append(dist)

    return np.sum(dist_list)

# Checkers
print(distance_calculator([(41.49008, -71.312796), (41.499498, -81.695391), (41.499498, -71.312796)]))
print(distance_calculator([(41.49008, -71.312796), (41.499498, -81.695391), (41.499498, -71.312796), (41.495432, -81.695391)]))
print(help(distance_calculator))
