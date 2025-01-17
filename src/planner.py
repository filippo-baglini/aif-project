import numpy as np

from .goal_parser import understand_goal
from .utils import manhattan_distance, manhattan_distance_accounting_for_walls
from .environment_handler import _process_obs
from .subgoals import *
import heapq

class Planner:

    def __init__(self, env):
        self.env = env

        pos = env.unwrapped.agent_pos
        self.pos = (pos[0].item(), pos[1].item())
        self.starting_pos = self.pos

        self.f_vec = env.unwrapped.dir_vec
        self.r_vec = env.unwrapped.right_vec
        self.starting_compass = self.f_vec 

        self.vis_mask = np.zeros(shape=(env.unwrapped.width, env.unwrapped.height), dtype=bool)
        self.vis_obs= np.zeros(shape=(env.unwrapped.width, env.unwrapped.height), dtype=object)
        for i in range(env.unwrapped.width):
            for j in range(env.unwrapped.height):
                self.vis_obs[i, j] = (0, -1, 0)

        self.doors_coords = {}
        
        self.mission = env.unwrapped.instrs
        self.actions = env.unwrapped.actions

        self.sub_goals = []
        understand_goal(self, self.mission)

        self.target = None
        self.path = []
        self.save_path = []
        self.prev_frontier = None
        self.drop_pos = None

        self.carrying = False
        self.carrying_object = None
        self.carrying_target = None

        self.important_objects = []
        self.important_objects_coords = []

    def __call__(self):

        pos = self.env.unwrapped.agent_pos
        self.pos = (pos[0].item(), pos[1].item())
        
        self.f_vec = self.env.unwrapped.dir_vec
        self.r_vec = self.env.unwrapped.right_vec
        self.vis_mask , self.vis_obs, self.doors_coords = _process_obs(self.env, self.vis_mask, self.vis_obs, self.doors_coords)

    def look_for_goal(self, goal_type, goal_color, goal_loc = None):

        goals = []
        min_distance = 999
        best_goal = None
        for col_index, col in enumerate(self.vis_obs):
            if col_index == 0 or col_index == len(self.vis_obs) - 1:
                continue
            for row_index, element in enumerate(col):
                if row_index == 0 or row_index == len(col) - 1:
                    continue
                if self.pos == (col_index, row_index):
                    continue
                if isinstance(element, tuple):
                    if goal_color is not None and goal_type is not None:
                        if element[0] == goal_type and element[1] == goal_color:
                            if goal_loc is not None: 
                                if(self.find_relative_position(goal_loc, col_index, row_index)):
                                   goals.append((col_index, row_index)) 
                            else:
                                goals.append((col_index, row_index))

                    elif goal_color is None:
                        if element[0] == goal_type:
                            if goal_loc is not None: 
                                if (self.find_relative_position(goal_loc, col_index, row_index)):
                                    goals.append((col_index, row_index))
                            else:
                                goals.append((col_index, row_index))

                    elif goal_type is None:
                        if element[0] != 2 and element[1] == goal_color:
                            if goal_loc is not None: 
                                if (self.find_relative_position(goal_loc, col_index, row_index)):
                                    goals.append((col_index, row_index))
                            else:
                                goals.append((col_index, row_index))

        for goal in goals:
            if goal_loc is not None:
                distance = manhattan_distance(self.starting_pos, goal)
            else:
                distance = manhattan_distance(self.pos, goal)
            if (distance < min_distance):
                min_distance = distance
                best_goal = goal

        return best_goal

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
            _, current = heapq.heappop(open_set)

            # Goal reached
            if current == target:
                # Reconstruct path
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                return path[::-1]  # Reverse the path

            # Explore neighbors
            for neighbor in self.neighbors(current):

                if (self.vis_obs[neighbor[0], neighbor[1]][0] in (2, 9) or (self.vis_obs[neighbor[0], neighbor[1]][0] == 0 and neighbor != target)):
                    continue
                
                else:
                    # Check if a better direction is already faced (this is where your rotation logic applies)
                    direction_to_cell = (neighbor[0] - current[0], neighbor[1] - current[1])
                    if np.array_equal(direction_to_cell, np.array(self.f_vec)):
                        if(self.vis_obs[neighbor[0], neighbor[1]][0] in (5, 6, 7)):
                            if self.carrying:
                                tentative_g = g_score[current] + 5 #Rotate, drop the carried item, rotate, pick up, move forward
                            else:
                                tentative_g = g_score[current] + 2 #Pick up the item and then move forward
                        else:
                        # No rotation needed, just moving forward
                            tentative_g = g_score[current] + 1  # Moving forward
                    elif np.array_equal(direction_to_cell, -np.array(self.f_vec)):
                        if(self.vis_obs[neighbor[0], neighbor[1]][0] in (5, 6, 7)):
                            if self.carrying:
                                tentative_g = g_score[current] + 7
                            else:  
                                tentative_g = g_score[current] + 4
                        #cell behind us, 2 rotaton and 1 forward
                        else:
                            tentative_g =  g_score[current] + 3
                    else:
                        if(self.vis_obs[neighbor[0], neighbor[1]][0] in (5, 6, 7)):
                            if self.carrying:
                                tentative_g = g_score[current] + 6
                            else:
                                tentative_g = g_score[current] + 3
                        # Rotation + move forward (rotate 90 degrees)
                        else:
                            tentative_g = g_score[current] + 2  # Rotate and move

                    if neighbor not in g_score or tentative_g < g_score[neighbor]:
                        # Update g-score and f-score
                        g_score[neighbor] = tentative_g
                        f_score = tentative_g + manhattan_distance(neighbor, target)
                        heapq.heappush(open_set, (f_score, neighbor))
                        came_from[neighbor] = current

        # No path found
        print("Path not found")
        return "FAILURE"
    
    def neighbors(self,cell):
            """Return valid neighbors (up, down, left, right)."""
            directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
            result = []
            for d in directions:
                neighbor = (cell[0] + d[0], cell[1] + d[1])
                
                if 0 <= neighbor[0] < np.shape(self.vis_obs)[0] and 0 <= neighbor[1] < np.shape(self.vis_obs)[1]:  #Bound check for cell
                    result.append(neighbor)
            return result
    
    def move_to_target(self, target):
        """
        Move the agent along the path returned by A* until the goal is reached.

        Parameters:
            path (list): A list of (x, y) tuples representing the path from A*.
        """
        # Use A star only if path empty or if new target to goal
        if len(self.path) == 0 or self.target != target:
            self.path = self.a_star_search(target)
            self.target = target

        # Iterate through the path
        if (len(self.path) == 0):
            print("PROBLEM, A* RETURNED A PATH OF LENGTH 0, NEED TO DEBUG")
            return "FAILURE"
        
        cell_pos = self.path[0]
        pos = self.pos
        f_vec = self.f_vec
        r_dir = self.r_vec

        # Calculate direction to the next cell
        direction_to_cell = (cell_pos[0] - pos[0], cell_pos[1] - pos[1])

        if np.array_equal(direction_to_cell, np.array(f_vec)) and cell_pos != target: 
            if self.step_is_blocked(cell_pos):
                return "BLOCKED"

            if self.step_is_door(cell_pos):
                return "OPEN DOOR"
 
            if self.carrying:
                prev_cell = self.pos
                if self.pos in self.doors_coords.keys():
                    self.vis_obs[prev_cell[0], prev_cell[1]] = (*self.doors_coords[self.pos],)
                else:
                    self.vis_obs[prev_cell[0], prev_cell[1]] = (1, -1, 0)

            self.path.pop(0)
            return self.actions.forward
        
        elif np.array_equal(direction_to_cell, np.array(f_vec)) and cell_pos == target:
            if self.step_is_blocked(cell_pos) and self.target_in_cell(self.cell_in_front(), self.sub_goals[0].target) != self.sub_goals[0].target:
                return "BLOCKED"
            
            self.path.pop(0)
            return self.actions.done
        
        elif np.array_equal(direction_to_cell, np.array(r_dir)):
            if self.step_is_blocked(cell_pos) and self.carrying and self.path[0] != target:
                return "BLOCKED_SIDE"
            # print("Rotate clockwise (90 degrees)")
            return self.actions.right

        elif np.array_equal(direction_to_cell, -np.array(r_dir)):
            if self.step_is_blocked(cell_pos) and self.carrying and self.path[0] != target:
                return "BLOCKED_SIDE"
            # print("Rotate counterclockwise (90 degrees)")
            return self.actions.left
        
        elif np.array_equal(direction_to_cell, -np.array(f_vec)):
            # print("Rotate twice")
            return self.actions.left

        else:
            print("Unexpected state. Cannot determine action.")
            return "FAILURE"

    def find_frontiers(self, exclude_frontier = None): #Function for finding frontier for exploration

        target = None
        cols, rows = self.vis_mask.shape
        unseen_cells = []
        min_distance = 999
        for c in range(cols):
            if c == 0 or c == cols - 1: #Avoid considering first and last column as frontier (the edges of the grid are always walls)
                continue
            for r in range(rows):
                if r == 0 or r == rows - 1: #Avoid considering first and last column as frontier (the edges of the grid are always walls)
                    continue
                if not self.vis_mask[c, r]:
                    neighbors = self.neighbors([c, r])
                    for nc, nr in neighbors:
                        if self.vis_mask[nc, nr] == 1:  #Adjacent to seen cell
                            if self.vis_obs[nc, nr][0] != 2:
                                if (exclude_frontier is not None and exclude_frontier == (c, r)):
                                    break
                                unseen_cell = (c, r) #remeber self.vis_mask has rows and columns inverted compared to visual render
                                unseen_cells.append(unseen_cell)
                                break

        for cell in unseen_cells:
            if any(self.vis_obs[n[0], n[1]][2] == 2 for n in self.neighbors(cell)):
                distance = manhattan_distance_accounting_for_walls(self.pos, cell, self.vis_obs) + 100
            else:
                distance = manhattan_distance_accounting_for_walls(self.pos, cell, self.vis_obs)
            if distance < min_distance:
                min_distance = distance
                target = cell

        return target
    
    def find_new_frontiers(self, old_frontier):
        new_frontier = self.find_frontiers(old_frontier)
        return new_frontier

    
    def find_closest_empty_cell(self, cell, reason=None): 

        neighbors = self.neighbors(cell)
        empty_cell = []
        empty_cell_distance = []
        for col_index, col in enumerate(self.vis_obs):
            if col_index == 0 or col_index == len(self.vis_obs) - 1:
                continue
            for row_index, element in enumerate(col):
                if row_index == 0 or row_index == len(col) - 1:
                    continue
                if self.pos == (col_index, row_index):
                    continue

                if self.vis_obs[col_index, row_index][0] == 1:
                    if self.drop_pos is not None and (col_index, row_index) == self.drop_pos:
                        pass

                    else:
                        empty_cell.append((col_index, row_index))
                        empty_cell_distance.append(manhattan_distance(cell, (col_index, row_index)))

        if reason is None:
            for empty in empty_cell:
                if empty in neighbors:
                    if empty == self.cell_in_front():
                        return empty

        best_cell = None
        lowest_distance = float("inf")
        for i, e in enumerate(empty_cell):
            if empty_cell_distance[i] < lowest_distance:
                lowest_distance = empty_cell_distance[i]
                best_cell = e

        if best_cell:
            return best_cell
    

    def find_closest_drop_cell(self, cell, reason=None):
    
        min_distance = 999
        empty_cells = []
        blocked_cells = []

        for n in self.neighbors(cell):

            if n == self.pos:
                continue
            
            if self.vis_obs[n[0], n[1]][0] in (5, 6, 7):
                blocked_cells.append(n)
            
            if self.vis_obs[n[0], n[1]][0] == 1:
                empty_cells.append(n)

        if len(empty_cells) == 0:
            min_distance = 999
            for blocked_cell in blocked_cells:
                distance = manhattan_distance(self.pos, blocked_cell)
                if distance < min_distance:
                    best_cell = blocked_cell
                    min_distance = distance
        else:
            min_distance = 999
            for empty_cell in empty_cells:
                distance = manhattan_distance(self.pos, empty_cell)
                if distance < min_distance:
                    best_cell = empty_cell
                    min_distance = distance

        return best_cell

    def find_closest_empty_cell_avoiding_previous_path(self, cell):
        neighbors = self.neighbors(cell)
        empty_cell = []
        empty_cell_distance = []
        for col_index, col in enumerate(self.vis_obs):
            if col_index == 0 or col_index == len(self.vis_obs) - 1:
                continue
            for row_index, element in enumerate(col):
                if row_index == 0 or row_index == len(col) - 1:
                    continue
                if self.pos == (col_index, row_index):
                    continue

                if self.vis_obs[col_index, row_index][0] == 1:
                    if self.drop_pos is not None and (col_index, row_index) == self.drop_pos:
                        pass
                    elif (col_index, row_index) in self.save_path:
                        pass
                    else:
                        empty_cell.append((col_index, row_index))
                        empty_cell_distance.append(manhattan_distance(cell, (col_index, row_index)))

        for empty in empty_cell:
            if empty in neighbors:
                if empty == self.cell_in_front():
                    return empty

        best_cell = None
        lowest_distance = float("inf")
        for i, e in enumerate(empty_cell):
            if empty_cell_distance[i] < lowest_distance:
                lowest_distance = empty_cell_distance[i]
                best_cell = e

        if best_cell:
            return best_cell


    def cell_in_front(self):
        return (self.pos[0] + self.f_vec[0], self.pos[1] + self.f_vec[1])
    
    def object_in_front(self):
        return self.vis_obs[self.cell_in_front()]

    def door_in_cell(self, cell):
        return [self.vis_obs[cell[0], cell[1]][0], self.vis_obs[cell[0], cell[1]][1], None]
    
    def target_in_front(self):
        return [self.object_in_front()[0], self.object_in_front()[1], None]
    
    def target_in_cell(self, cell, target):

        target_type = target[0] if target is not None else None
        target_color = target[1] if target is not None else None
        target_loc = target[2] if target is not None else None

        if target_type is not None and target_color is not None:
            
            if target_loc is not None:
                
                if self.find_relative_position(target_loc, cell[0], cell[1]):
                    return [self.vis_obs[cell][0], self.vis_obs[cell][1], target_loc]

            else:
                return [self.vis_obs[cell][0], self.vis_obs[cell][1], None]
            
        elif target_type is not None:
            if target_loc is not None:
                if self.find_relative_position(target_loc, cell[0], cell[1]):
                    return [self.vis_obs[cell][0], None, target_loc]
            else:
                return [self.vis_obs[cell][0], None, None]
            
        elif target_color is not None:
            if target_loc is not None:
                if self.find_relative_position(target_loc, cell[0], cell[1]):
                    return [None, self.vis_obs[cell][1], target_loc]
            else:
                return [None, self.vis_obs[cell][1], None]
    

    def step_is_blocked(self, cell):
        for i in range(5,8):
            if self.vis_obs[cell[0], cell[1]][0] == i:
                return True
        return False
    
    def step_is_door(self, cell):
        if self.vis_obs[cell[0], cell[1]][0] == 4 and self.vis_obs[cell[0], cell[1]][2] == 1:
            return True
        return False
    

    def find_relative_position(self, goal_loc, goal_col, goal_row): #Used for env where we need to find the relative position of the goal to the agent's starting position

        relative_position = (goal_col - self.starting_pos[0], goal_row - self.starting_pos[1])

        if (goal_loc == "front"):
            if (relative_position[1] < 0 and np.array_equal(self.starting_compass, [0, -1])): #TARGET IS HIGHER THAN THE AGENT'S STARTING POSITION AND AGENT'S STARTING DIRECTION WAS UP
                return True
            elif (relative_position[1] > 0 and np.array_equal(self.starting_compass, [0, 1])): #TARGET IS LOWER THAN THE AGENT'S STARTING POSITION AND AGENT'S STARTING DIRECTION WAS DOWN
                return True
            elif (relative_position[0] < 0 and np.array_equal(self.starting_compass, [-1, 0])): #TARGET IS TO THE LEFT OF THE AGENT'S STARTING POSITION AND AGENT'S STARTING DIRECTION WAS LEFT
                return True
            elif (relative_position[0] > 0 and np.array_equal(self.starting_compass, [1, 0])): #TARGET IS TO THE RIGHT OF THE AGENT'S STARTING POSITION AND AGENT'S STARTING DIRECTION WAS RIGHT
                return True
            return False
        
        elif (goal_loc == "behind"):
            if (relative_position[1] < 0 and np.array_equal(self.starting_compass, [0, 1])): #TARGET IS HIGHER THAN THE AGENT'S STARTING POSITION AND AGENT'S STARTING DIRECTION WAS DOWN
                return True
            elif (relative_position[1] > 0 and np.array_equal(self.starting_compass, [0, -1])): #TARGET IS LOWER THAN THE AGENT'S STARTING POSITION AND AGENT'S STARTING DIRECTION WAS UP
                return True
            elif (relative_position[0] < 0 and np.array_equal(self.starting_compass, [1, 0])): #TARGET IS TO THE LEFT OF THE AGENT'S STARTING POSITION AND AGENT'S STARTING DIRECTION WAS RIGHT
                return True
            elif (relative_position[0] > 0 and np.array_equal(self.starting_compass, [-1, 0])): #TARGET IS TO THE RIGHT OF THE AGENT'S STARTING POSITION AND AGENT'S STARTING DIRECTION WAS LEFT
                return True
            return False
        
        elif (goal_loc == "left"):
            if (relative_position[1] < 0 and np.array_equal(self.starting_compass, [1, 0])): #TARGET IS HIGHER THAN THE AGENT'S STARTING POSITION AND AGENT'S STARTING DIRECTION WAS RIGHT
                return True
            elif (relative_position[1] > 0 and np.array_equal(self.starting_compass, [-1, 0])): #TARGET IS LOWER THAN THE AGENT'S STARTING POSITION AND AGENT'S STARTING DIRECTION WAS LEFT
                return True
            elif (relative_position[0] < 0 and np.array_equal(self.starting_compass, [0, -1])): #TARGET IS TO THE LEFT OF THE AGENT'S STARTING POSITION AND AGENT'S STARTING DIRECTION WAS UP
                return True
            elif (relative_position[0] > 0 and np.array_equal(self.starting_compass, [0, 1])): #TARGET IS TO THE RIGHT OF THE AGENT'S STARTING POSITION AND AGENT'S STARTING DIRECTION WAS DOWN
                return True
            return False
        
        elif (goal_loc == "right"):
            if (relative_position[1] < 0 and np.array_equal(self.starting_compass, [-1, 0])): #TARGET IS HIGHER THAN THE AGENT'S STARTING POSITION AND AGENT'S STARTING DIRECTION WAS LEFT
                return True
            elif (relative_position[1] > 0 and np.array_equal(self.starting_compass, [1, 0])): #TARGET IS LOWER THAN THE AGENT'S STARTING POSITION AND AGENT'S STARTING DIRECTION WAS RIGHT
                return True
            elif (relative_position[0] < 0 and np.array_equal(self.starting_compass, [0, 1])): #TARGET IS TO THE LEFT OF THE AGENT'S STARTING POSITION AND AGENT'S STARTING DIRECTION WAS DOWN
                return True
            elif (relative_position[0] > 0 and np.array_equal(self.starting_compass, [0, -1])): #TARGET IS TO THE RIGHT OF THE AGENT'S STARTING POSITION AND AGENT'S STARTING DIRECTION WAS UP
                return True
            return False
        


    def execute_subgoals(self):
        if len(self.sub_goals) > 500:
            print("Infinite recursion, something is wrong")
            return "FAILURE"
        
        if self.sub_goals:
            current_subgoal = self.sub_goals[0]
            action = current_subgoal()
            
            if action is self.actions.done:
                action = self.execute_subgoals()

            if action == "FAILURE":
                return "FAILURE"
                
            return action

        else:
            print("All subgoals completed, but mission is not terminated")
            return "FAILURE"