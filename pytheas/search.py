"""
Searching algorithms. This module is copied from Voyager. It was developed by Victor Wåhlstrand Skärström (@waahlstrand on Github).

This script contains tools to calculate paths and routes through a simulation.

This file can be imported as module and contains the following functions:
    * heuristic - Generic measure between two positions
And the following classes:
    * Grid - represents the map as an approximately equidistant grid
    * WeightedGrid - inherits from Grid, used to symbolize a map where not all positions are equally likely to traverse
    * PriorityQueue - used in A-star algorithm to deal with queues and stacking
    * Astar - implementation of A-star algorithm
"""


from typing import Dict, Tuple, List, Iterator, Optional, TypeVar
import heapq
import numpy as np
import cv2

T = TypeVar('T')
Position = Tuple[int, int]

def heuristic(a: Position, b: Position) -> float:
    """Distance measure between two positions.

    Args:
        a (Position): Current position
        b (Position): Other position

    Returns:
        float: A measure of the distance between the points
    """
    
    (x1, y1) = a
    (x2, y2) = b
    return abs(x1 - x2) + abs(y1 - y2)

class Grid:
    """
    Represents the map as an approximately equidistant grid, with methods to find if
    the current position is in bounds, if there are obstacles "walls", and which are the closest places to go.

    Attributes:
        width (int): width of the grid
        height (int): height of the grid
        walls (Position): walls of the map, defined as unpassable steps in the A-star algorithm
    Methods:
        in_bounds(id): Checks if the current position is in bounds
        passable(id): Checks if current position has any obstacles around (walls)
        neighbors(id): Calculates all traversable neighbors of a current position
    """
    def __init__(self, width: int, height: int):
        """
        Args:
            width (int): width of map
            height (int): height of map
        """
        self.width = width
        self.height = height
        self.walls: List[Position] = []
    
    def in_bounds(self, id: Position) -> bool:
        """Checks if the current position is in bounds of the map.

        Args:
            id (Position): Current position

        Returns:
            bool: Whether position is in bounds
        """
        (x, y) = id
        return 0 <= x < self.width and 0 <= y < self.height
    
    def passable(self, id: Position) -> bool:
        """Checks if the current position has any obstacles, so called "walls". 

        Args:
            id (Position): Current position

        Returns:
            bool: Whether the position is passable, or if it has walls
        """
        return id not in self.walls
    
    def neighbors(self, id: Position) -> Iterator[Position]:
        """Calculates the traversable neighbours of the current position as an iterator

        Args:
            id (Position): Current position

        Returns:
            Position: A traversable neighbour to the current position

        Yields:
            Iterator[Position]: An iterator with the traversable neighbours
        """
        (x, y) = id
        neighbors = [(x+1, y), (x-1, y), (x, y+1), (x, y-1), (x+1, y+1), (x-1, y-1), (x+1, y-1), (x-1, y+1)]
        if (x + y) % 2 == 0: neighbors.reverse() # S N W E
        results = filter(self.in_bounds, neighbors)
        results = filter(self.passable, results)
        return results

class WeightedGrid(Grid):
    """
    The WeightedGrid is a Grid used to symbolize a map where not all positions are equally likely to traverse. Some are more likely,
    these regions being weighted.

    Attributes:
        weights: weights of different points of the Grid.
        weigthed_mask: mask to superpose on Grid with weights.
    Methods:
        cost(from_node, to_node): calculate cost of movement between two points
        from_map(map, **kwargs): class method to generate WeightedGrid from an array where land is marked
        create_shoreline_contour(mask, weights=[5, 0.5], iterations=[1, 4], kernel_size=3): creates weighted shoreline contours for the map.
        mask_to_graph(mask): superposes mask on Grid.
    """

    def __init__(self, width: int, height: int):
        super().__init__(width, height)
        self.weights: Dict[Position, float] = {}
        self.weighted_mask = None
    
    def cost(self, from_node: Position, to_node: Position) -> float:
        return self.weights.get(to_node, 1)

    @classmethod
    def from_map(cls, map: np.ndarray, **kwargs):
        """Generate a WeightedGrid from a numpy array, wehere the land is symbolized as NaN.

        Args:
            map (np.ndarray): An array with land as NaN

        Returns:
            WeightedGrid: A WeightedGrid instance
        """

        map = map.values

        mask = np.isnan(map).astype(np.float)
        grid = cls(*mask.shape)

        grid.weighted_mask = cls.create_shoreline_contour(mask, **kwargs)

        grid.weights = cls.mask_to_graph(grid.weighted_mask)
        grid.walls = [(x[0], x[1]) for x in np.argwhere(np.isnan(map))]

        return grid

    @staticmethod
    def create_shoreline_contour(mask: np.ndarray, weights=[5, 0.5], iterations=[1, 4], kernel_size=3) -> np.ndarray:
        """Create a weight mask corresponding to the shoreline contour of the map.

        The contours are created using dilation of the land for a number of iterations and a given kernel size. The result is 
        a contour with a specific width, which is then assigned a specific weight.

        This mimics the tendency to avoid close shorelines and open sea.

        Args:
            mask (np.ndarray): A mask symbolizing the land
            weights (list, optional): A list of weights for each contour. Defaults to [5, 0.5].
            iterations (list, optional): Number of iterations to broaden the contour. Defaults to [1, 4].
            kernel_size (int, optional): The kernel size used for broadening of the contour. Defaults to 3.

        Returns:
            np.ndarray: A weighted array corresponding to a map with contours around the land
        """

        kernel = np.ones((kernel_size, kernel_size), np.uint8)
        weighted_mask = np.ones(mask.shape)

        for weight, iters in zip(weights, iterations):

            # Calculate shorelines at different distance
            shoreline = cv2.dilate(mask, kernel, iterations=iters)

            # Start at zero and add shorelines with weights
            weighted_mask[shoreline.astype(np.bool)] = weight

        # # Start at zero and add shorelines with weights
        weighted_mask[mask.astype(np.bool)] = np.nan    

        return weighted_mask

    @staticmethod
    def mask_to_graph(mask):
        """Superposes mask on Grid.
        Args:
            mask (np.ndarray): mask with weights to be superposed on Grid.
        Returns:
            np.ndarray: array with weighted Grid
        """

        return {index: value for index, value in np.ndenumerate(mask) if not np.isnan(value)}


class PriorityQueue:
    """Class to define PriorityQueue (used in Astar).

    Attributes:
        elements (List[Tuple[float, T]]): elements a queue used to check points in A-star algorithm.
    Methods:
        empty(): return True if self.elements is empty.
        put(item, priority): insert new element in priority list
        get: return weight for iteration step
    """
    def __init__(self):
        self.elements: List[Tuple[float, T]] = []
    
    def empty(self) -> bool:
        return not self.elements
    
    def put(self, item: T, priority: float):
        heapq.heappush(self.elements, (priority, item))
    
    def get(self) -> T:
        return heapq.heappop(self.elements)[1]

class Astar:
    """Implementation of A-star algorithm (see e.g. https://en.wikipedia.org/wiki/A*_search_algorithm)
    
    Attributes:
        graph (WeightedGrid): weighted graph over which to perform the search
    Methods:
        search(start, goal): find a route from a start position to a goal position
        recontruct_path(came_from, start, goal): reconstruct the route from the graph pointing to previous positions.
    """

    def __init__(self, graph: WeightedGrid) -> None:
        
        self.graph  = graph

    def search(self, start: Position, goal: Position) -> Tuple[Dict[Position, Position], Dict[Position, float]]:
        """Find a route from a start position to a goal position.

        Args:
            start (Position): Start position
            goal (Position): End position


        Returns:
            Tuple[Dict[Position, Position], Dict[Position, float]]: A dict as a graph pointing to the previous position, and the current cost of the route.
        """

        frontier = PriorityQueue()
        frontier.put(start, 0)
        came_from: Dict[Position, Optional[Position]] = {}
        cost_so_far: Dict[Position, float] = {}
        came_from[start] = None
        cost_so_far[start] = 0
        
        while not frontier.empty():
            current: Position = frontier.get()
            
            if current == goal:
                break
            
            for next in self.graph.neighbors(current):
                new_cost = cost_so_far[current] + self.graph.cost(current, next)
                if next not in cost_so_far or new_cost < cost_so_far[next]:
                    cost_so_far[next] = new_cost
                    priority = new_cost + heuristic(next, goal)
                    frontier.put(next, priority)
                    came_from[next] = current
        
        return came_from, cost_so_far



    def reconstruct_path(self, came_from: Dict[Position, Position], 
                               start: Position, 
                               goal: Position) -> List[Position]:
        """Reconstruct the route from the graph pointing to previous positions.

        Args:
            came_from (Dict[Position, Position]): Dictionary pointing from one position to another
            start (Position): Start position
            goal (Position): End position

        Returns:
            List[Position]: The resulting route as a list of positions
        """

        current: Position = goal
        path = []
        while current != start:
            
            path.append(current)

            current = came_from[current]

        path.reverse()
        return path

