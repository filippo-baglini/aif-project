import numpy as np

from goal_parser import understand_goal
from utils import manhattan_distance

class Planner:

    def __init__(self, bot):
        self.pos = bot.environment.unwrapped.agent_pos
        self.f_vec = bot.environment.unwrapped.dir_vec
        self.r_vec = bot.environment.unwrapped.right_vec
        self.vis_mask = bot.vis_mask
        self.vis_obs = bot.vis_obs
        self.actions = bot.actions

        self.goal_type, self.goal_color = understand_goal(bot.mission)
        self.goal_pos = None
        

    def look_for_goal(self):

        for row_index, row in enumerate(self.vis_obs):
            for col_index, element in enumerate(row):
                if isinstance(element, tuple):
                    if element[0] == self.goal_type and element[1] == self.goal_color:
                        self.goal_pos = (row_index, col_index)

                        return not None
        return None

    def look_for_door(self):
        for row_index, row in enumerate(self.vis_obs):
            for col_index, element in enumerate(row):
                if isinstance(element, tuple):
                    if element[0] == 4:
                        return (row_index, col_index)
        return None
    
    
        
    
    def find_best_cell(self, target):
        pos = self.pos
        f_vec = self.f_vec

        possible_cells = [
            (pos[0] - 1, pos[1]),  # up
            (pos[0] + 1, pos[1]),  # down
            (pos[0], pos[1] - 1),  # left
            (pos[0], pos[1] + 1),  # right
        ]

        best_cell = None
        min_distance = float('inf')
        
        for cell in possible_cells:
            # Skip walls or invalid cells
            if isinstance(self.vis_obs[cell[0], cell[1]], tuple):
                    if self.vis_obs[cell[0], cell[1]][0] != self.goal_type:
                        continue

            # Calculate Manhattan distance to goal
            distance = manhattan_distance(cell, target)

            # Update the best cell if this one is closer
            if distance < min_distance:
                min_distance = distance
                best_cell = cell
                
            #Check if a better cell is faced already by agent
            elif distance == min_distance:
                direction_to_cell = (cell[0] - pos[0], cell[1] - pos[1])
                direction_to_cell = direction_to_cell
                if np.array_equal(direction_to_cell, np.array(f_vec)):
                    best_cell = cell


        return best_cell, min_distance    

            
    def move_to_cell(self, target):

        cell_pos, dist = self.find_best_cell(target)
        pos = self.pos
        f_vec = self.f_vec
        r_dir = self.r_vec

        direction_to_cell = cell_pos[0]-pos[0], cell_pos[1]-pos[1]

        
        if np.array_equal(direction_to_cell, np.array(f_vec)):
            print("Move forward")
            if isinstance(self.vis_obs[cell_pos[0], cell_pos[1]], tuple):
                # if self.vis_obs[cell_pos[0], cell_pos[1]][0]:
                #     return self.actions.toggle
                return self.actions.pickup
            return self.actions.forward
        if np.array_equal(direction_to_cell, np.array(r_dir)):
            print("Rotate clockwise (90 degrees)")
            return self.actions.right
        elif np.array_equal(direction_to_cell, -np.array(r_dir)):
            print("Rotate counterclockwise (90 degrees)")
            return self.actions.left
        else:
            print("Reached Goal")
            return self.actions.done
        
    def move_to_goal(self):
        return self.move_to_cell(self.find_best_cell(self.goal_pos)[0])