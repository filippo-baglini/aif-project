import numpy as np

from goal_parser import understand_goal
from utils import manhattan_distance
import heapq

class Planner:

    def __init__(self, bot):
        self.pos = bot.environment.unwrapped.agent_pos
        self.f_vec = bot.environment.unwrapped.dir_vec
        self.r_vec = bot.environment.unwrapped.right_vec
        self.vis_mask = bot.vis_mask
        self.vis_obs = bot.vis_obs
        self.actions = bot.actions

        self.goal_type, self.goal_color = understand_goal(bot.mission)

        self.path = []
        

    def look_for_goal(self):

        for row_index, row in enumerate(self.vis_obs):
            for col_index, element in enumerate(row):
                if isinstance(element, tuple):
                    if element[0] == self.goal_type and element[1] == self.goal_color:
                        # self.goal_pos = (row_index, col_index)

                        return (row_index, col_index)
        return None

    def look_for_door(self):
        for row_index, row in enumerate(self.vis_obs):
            for col_index, element in enumerate(row):
                if isinstance(element, tuple):
                    if element[0] == 4:
                        return (row_index, col_index)
        return None
    
     


    def a_star_search(self, target):
        """
        A* search algorithm for a grid.
        
        grid: 2D list representing the environment (0: free space, 1: obstacle).
        start: Tuple (x, y) for the start position.
        goal: Tuple (x, y) for the goal position.
        
        Returns the best path as a list of (x, y) tuples or None if no path exists.
        """

        

        # Priority queue for open set
        open_set = []
        heapq.heappush(open_set, (0, self.pos))  # (f-score, cell)

        # g-scores (costs to reach each cell)
        g_score = {self.pos: 0}
        f_score = {self.pos: manhattan_distance(self.pos, target)}
        # Path tracking
        came_from = {}

        while open_set:
            # Pop the cell with the lowest f-score
            current_f, current = heapq.heappop(open_set)

            # Goal reached
            if current == target:
                # Reconstruct path
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                # path.append(self.goal_pos)            # Can use to see immediatley target coords
                return path[::-1]  # Reverse the path

            # Explore neighbors
            for neighbor in self.neighbors(current):
                # # Tentative g-score
                # tentative_g = g_score[current] + 1  # Assuming uniform movement cost

                # Check if a better direction is already faced (this is where your rotation logic applies)
                direction_to_cell = (neighbor[0] - current[0], neighbor[1] - current[1])
                if np.array_equal(direction_to_cell, np.array(self.f_vec)):
                    # No rotation needed, just moving forward
                    tentative_g = g_score[current] + 1  # Moving forward
                else:
                    # Rotation + move forward (rotate 90 degrees)
                    tentative_g = g_score[current] + 2  # Rotate and move

                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    # Update g-score and f-score
                    g_score[neighbor] = tentative_g
                    f_score = tentative_g + manhattan_distance(neighbor, target)
                    heapq.heappush(open_set, (f_score, neighbor))
                    came_from[neighbor] = current

        # No path found
        return None
    
    def neighbors(self,cell):
            """Return valid neighbors (up, down, left, right)."""
            directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
            result = []
            for d in directions:
                neighbor = (cell[0] + d[0], cell[1] + d[1])
                if isinstance(self.vis_obs[cell[0], cell[1]], tuple):
                    continue
                    # if self.vis_obs[cell[0], cell[1]][0] != 5 or self.vis_obs[cell[0], cell[1]][0] != 6 :
                    #     continue
                if 0 <= neighbor[0] < len(self.vis_obs[0]) and 0 <= neighbor[1] < len(self.vis_obs[1]):  #Bound check for cell
                    result.append(neighbor)
            return result
    
    def move_to_target(self, target):
        """
        Move the agent along the path returned by A* until the goal is reached.

        Parameters:
            path (list): A list of (x, y) tuples representing the path from A*.
        """

        # Check if the path is empty
        if not self.path:
            self.path = self.a_star_search(target)
            # print("No path available.")
            # return self.actions.done
        # Remove the start position (current position) from the path, if present
        if self.pos == self.path[0]:
            self.path = self.path[1:]

        # Iterate through the path
        cell_pos = self.path.pop(0)
        # print(cell_pos)
        pos = self.pos
        f_vec = self.f_vec
        r_dir = self.r_vec

        # Calculate direction to the next cell
        direction_to_cell = cell_pos[0] - pos[0], cell_pos[1] - pos[1]

        # Determine the action based on the direction
        if np.array_equal(direction_to_cell, np.array(f_vec)):
            # print(f"Move forward to {cell_pos}")
            if isinstance(self.vis_obs[cell_pos[0], cell_pos[1]], tuple):
                return self.actions.pickup  # Interact with objects if necessary
            return self.actions.forward

        elif np.array_equal(direction_to_cell, np.array(r_dir)):
            # print("Rotate clockwise (90 degrees)")
            return self.actions.right

        elif np.array_equal(direction_to_cell, -np.array(r_dir)):
            # print("Rotate counterclockwise (90 degrees)")
            return self.actions.left

        else:
            # print("Unexpected state. Cannot determine action.")
            return self.actions.done



    # def neighbors_mask(self,cell):
    #         """Return valid neighbors (up, down, left, right)."""
    #         directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    #         result = []
    #         for d in directions:
    #             neighbor = (cell[0] + d[0], cell[1] + d[1])

    #             if 0 <= neighbor[0] < len(self.vis_mask[0]) and 0 <= neighbor[1] < len(self.vis_mask[1]):  #Bound check for cell
    #                 result.append(neighbor)
    #         return result
        
    # def find_frontiers(self):
    #     frontiers = []

    #     rows, cols = self.vis_mask.shape
    #     for r in range(rows):
    #         for c in range(cols):
    #             if self.vis_mask[r, c] == 0:  # Unseen cell
    #                 neighbors = self.neighbors_mask((c, r))
    #                 for nr, nc in neighbors:
    #                     if self.vis_mask[nr, nc] == 1:  # Adjacent to seen cell

    #                         return self.move_to_target((c, r))
