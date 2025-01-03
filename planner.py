import numpy as np

from goal_parser import understand_goal
from utils import manhattan_distance
from environment_handler import _process_obs
import heapq
import time

class Planner:

    def __init__(self, env):
        self.env = env

        pos = env.unwrapped.agent_pos
        self.pos = (pos[0].item(), pos[1].item())

        self.f_vec = env.unwrapped.dir_vec
        self.r_vec = env.unwrapped.right_vec

        self.vis_mask = np.zeros(
            shape=(env.unwrapped.width, env.unwrapped.height), dtype=bool
        )


        self.vis_obs= np.zeros(
            shape=(env.unwrapped.width, env.unwrapped.height), dtype=object
        )

        for i in range(env.unwrapped.width):
            for j in range(env.unwrapped.height):
                self.vis_obs[i, j] = (0, 0, 0)
        
        self.mission = env.unwrapped.instrs
        self.actions = env.unwrapped.actions

        self.sub_goals = []

        understand_goal(self, self.mission)

        self.target = None
        self.path = []
        self.test = []

        self.carrying = False
        self.action_list = [self.actions.left, self.actions.drop, self.actions.right]

    def __call__(self):

        pos = self.env.unwrapped.agent_pos
        self.pos = (pos[0].item(), pos[1].item())
        
        self.f_vec = self.env.unwrapped.dir_vec
        self.r_vec = self.env.unwrapped.right_vec
        self.vis_mask , self.vis_obs = _process_obs(self.env, self.vis_mask, self.vis_obs)


    def look_for_goal(self, goal_type, goal_color):
        
        goals = []
        min_distance = 999
        best_goal = None
        for row_index, row in enumerate(self.vis_obs):
            for col_index, element in enumerate(row):
                if isinstance(element, tuple):
                    if element[0] == goal_type and element[1] == goal_color:
                        # self.goal_pos = (row_index, col_index)
                        goals.append((row_index, col_index))
                        #return (row_index, col_index)
        for goal in goals:
            distance = manhattan_distance(self.pos, goal)
            if (distance < min_distance):
                min_distance = distance
                best_goal = goal
        return best_goal

    def a_star_search(self, target, reason):
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
                if self.step_is_blocked(neighbor) and neighbor != target:
                    if reason == "PutNext":
                        continue

                if (self.vis_obs[neighbor[0], neighbor[1]][0] == 2 or self.vis_obs[neighbor[0], neighbor[1]][0] == 9):
                    #print("WALL ON PATH, PATH NOT CONSIDERED")
                    continue
                
                else:
                    # Check if a better direction is already faced (this is where your rotation logic applies)
                    direction_to_cell = (neighbor[0] - current[0], neighbor[1] - current[1])
                    if np.array_equal(direction_to_cell, np.array(self.f_vec)):
                        if(self.vis_obs[neighbor[0], neighbor[1]][0] == 5 or self.vis_obs[neighbor[0], neighbor[1]][0] == 6 or self.vis_obs[neighbor[0], neighbor[1]][0] == 7):
                            tentative_g = g_score[current] + 2 #Pick up the item and then move forward
                        else:
                        # No rotation needed, just moving forward
                            tentative_g = g_score[current] + 1  # Moving forward
                    elif np.array_equal(direction_to_cell, -np.array(self.f_vec)):
                        if(self.vis_obs[neighbor[0], neighbor[1]][0] == 5 or self.vis_obs[neighbor[0], neighbor[1]][0] == 6 or self.vis_obs[neighbor[0], neighbor[1]][0] == 7):
                            tentative_g = g_score[current] + 4
                        #cell behind us, 2 rotaton and 1 forward
                        else:
                            tentative_g =  g_score[current] + 3
                    else:
                        if(self.vis_obs[neighbor[0], neighbor[1]][0] == 5 or self.vis_obs[neighbor[0], neighbor[1]][0] == 6 or self.vis_obs[neighbor[0], neighbor[1]][0] == 7):
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
        time.sleep(5000000)
        return None
    
    def neighbors(self,cell):
            """Return valid neighbors (up, down, left, right)."""
            directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
            result = []
            for d in directions:
                neighbor = (cell[0] + d[0], cell[1] + d[1])
                
                if 0 <= neighbor[0] < len(self.vis_mask[0]) and 0 <= neighbor[1] < len(self.vis_mask[1]):  #Bound check for cell
                    result.append(neighbor)
            return result
    
    def move_to_target(self, target, reason="GoNextTo"):
        """
        Move the agent along the path returned by A* until the goal is reached.

        Parameters:
            path (list): A list of (x, y) tuples representing the path from A*.
        """
        # Use A star only if path empty or if new target to goal
        if len(self.path) == 0 or self.target != target:
            # print("USE A STAR")
            print(f"Target: {target}")
            self.path = self.a_star_search(target, reason)
            self.target = target

        
        # print(f"Position: {self.pos}")
        # print(f"Target: {target}")
        # print(f"Path: {self.path}")

        # Iterate through the path
        cell_pos = self.path[0]
        pos = self.pos
        f_vec = self.f_vec
        r_dir = self.r_vec



        # Calculate direction to the next cell
        direction_to_cell = (cell_pos[0] - pos[0], cell_pos[1] - pos[1])

        if np.array_equal(direction_to_cell, np.array(f_vec)) and cell_pos != target: #IMPORTANT MISSING CONDITON TO CHECK IF CELL HE NEEDS TO MOVE IS LAST WHICH IS THE TARGET
            if self.step_is_blocked(cell_pos):
                return "BLOCKED"
            
            if self.step_is_door(cell_pos):
                return "OPEN DOOR"
            
            self.path.pop(0)
            return self.actions.forward
        elif np.array_equal(direction_to_cell, np.array(r_dir)):
            if self.step_is_blocked(cell_pos) and self.carrying:
                return "BLOCKED_SIDE"
            # print("Rotate clockwise (90 degrees)")
            return self.actions.right

        elif np.array_equal(direction_to_cell, -np.array(r_dir)):
            if self.step_is_blocked(cell_pos) and self.carrying:
                return "BLOCKED_SIDE"
            # print("Rotate counterclockwise (90 degrees)")
            return self.actions.left
        
        elif np.array_equal(direction_to_cell, -np.array(f_vec)):
            # print("Rotate twice")
            return self.actions.left

        else:
            print("Unexpected state. Cannot determine action.")
            return self.actions.done

    # def find_frontiers(self):
    #     rows, cols = self.vis_mask.shape
    #     unseen_cells = []
    #     min_distance = 999
    #     for r in range(rows):
    #         for c in range(cols):
    #             if not self.vis_mask[r, c]:
    #                 neighbors = self.neighbors([r, c])
    #                 for nr, nc in neighbors:
    #                     if  self.vis_mask[nr, nc] == 1:  # Adjacent to seen cell
    #                         if self.vis_obs[nr, nc][0] != 2: #Dont move towards wall
    #                             unseen_cell = (r, c) #remeber self.vis_mask has rows and columns inverted compared to visual render
    #                             unseen_cells.append(unseen_cell)
    #                             break
    #     for cell in unseen_cells:
    #         distance = manhattan_distance(self.pos, cell)
    #         if distance < min_distance:
    #             min_distance = distance
    #             target = cell
    #     #print(f"target cell of find frontiers: {target}")
    #             return target

    #     print("Explored all env!")
    #     return self.actions.done

    def find_frontiers(self):
        # if (len(self.path) != 0):
        #     return self.move_to_target(self.target)
        rows, cols = self.vis_mask.shape
        unseen_cells = []
        min_distance = 999
        for r in range(rows):
            if r == 0 or r == rows - 1:
                continue
            for c in range(cols):
                if c == 0 or c == cols - 1:
                    continue
                if not self.vis_mask[r, c]:
                    neighbors = self.neighbors([r, c])
                    for nr, nc in neighbors:
                        if  self.vis_mask[nr, nc] == 1:  # Adjacent to seen cell
                            if self.vis_obs[nr, nc][0] != 2: #Dont move towards wall
                                unseen_cell = (r, c) #remeber self.vis_mask has rows and columns inverted compared to visual render
                                unseen_cells.append(unseen_cell)
                                break
        for cell in unseen_cells:
            distance = manhattan_distance(self.pos, cell)
            if distance < min_distance:
                min_distance = distance
                target = cell
        #print(f"target cell of find frontiers: {target}")
        return target

    # def put_down(self):

    #     # self.path_list = self.find_closest_empty_cell()

    #     if (len(self.action_list) != 0):
    #         action = self.action_list.pop(0)
    #         print(action)
    #         return (action)
    #     self.carrying = False
    #     self.action_list = [self.actions.left, self.actions.drop, self.actions.right]
    #     return self.actions.done
    
    def find_closest_empty_cell(self, cell):
        neighbors = self.neighbors(cell)
        empty_cell = []
        empty_cell_distance = []
        for neighbor in neighbors:
            if self.vis_obs[neighbor[0], neighbor[1]][0] == 1:
                empty_cell.append(neighbor)
                empty_cell_distance.append(manhattan_distance(self.pos, neighbor))
            
        for empty in empty_cell:
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
    
    def step_is_blocked(self, cell):
        for i in range(5,8):
            if self.vis_obs[cell[0], cell[1]][0] == i:
                return True
        return False
    def step_is_door(self, cell):
        if self.vis_obs[cell[0], cell[1]][0] == 4 and self.vis_obs[cell[0], cell[1]][2] == 1:
            return True
        return False

    def execute_subgoals(self):
        print(f"Subgoals: {self.sub_goals}")
        if self.sub_goals:
            current_subgoal = self.sub_goals[0]
            print(f"Executing subgoal: {current_subgoal}")

            action = current_subgoal()
            
            if action is self.actions.done:
                # print("Subgoal completed")
                action = self.execute_subgoals()

            # print(f"returning action: {action}")
            return action

        else:
            print("All subgoals completed")
            return self.actions.done
                

                    