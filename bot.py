import numpy as np
from utils import parse_mission

from minigrid.core.constants import OBJECT_TO_IDX, COLOR_TO_IDX

class Bot:

    def __init__ (self, environment):

        #environment to solve
        self.environment = environment


        #Initial goal
        self.mission = self.environment.unwrapped.mission
        self.actions = self.environment.unwrapped.actions

        self.vis_mask = np.zeros(
            shape=(environment.unwrapped.width, environment.unwrapped.height), dtype=bool
        )

        fill_value = (0, 0, 0)

        self.vis_obs= np.zeros(
            shape=(environment.unwrapped.width, environment.unwrapped.height), dtype=object
        )

        self.goal_type = None
        self.goal_color = None
        self.goal_pos = None
        self.scanned = 0
        


    def manhattan_distance(self, pos, target):
        """Calculate Manhattan distance between two points."""
        return np.abs(target[0] - pos[0]) + np.abs(target[1] - pos[1])


    def understand_goal(self):
        goal = parse_mission(self.mission) #extract the goal from the mission information
        goal_type, goal_color = goal
        self.goal_type = OBJECT_TO_IDX[goal_type]
        self.goal_color = COLOR_TO_IDX[goal_color]


        

    def take_action(self, environment):

        while not self.goal_type:
            self.understand_goal()

        self._process_obs()

        return self.plan()

    def _process_obs(self):
        """Parse the contents of an observation/image, update our state,
        rotate the vis_mask to the right, and make it specular."""

        obs_grid, vis_mask = self.environment.unwrapped.gen_obs_grid()

        view_size = self.environment.unwrapped.agent_view_size
        pos = self.environment.unwrapped.agent_pos
        f_vec = self.environment.unwrapped.dir_vec
        r_vec = self.environment.unwrapped.right_vec

        # Compute the absolute coordinates of the top-left corner
        # of the agent's view area
        top_left = pos + f_vec * (view_size - 1) - r_vec * (view_size // 2)

        # Mark everything in front of us as visible
        for vis_j in range(0, view_size):
            for vis_i in range(0, view_size):
                if not vis_mask[vis_i, vis_j]:
                    continue

                # Compute the world coordinates of this cell
                abs_i, abs_j = top_left - (f_vec * vis_j) + (r_vec * vis_i)

                if abs_i < 0 or abs_i >= self.vis_mask.shape[0]:
                    continue
                if abs_j < 0 or abs_j >= self.vis_mask.shape[1]:
                    continue

                self.vis_mask[abs_i, abs_j] = True
                # self.vis_type [abs_i, abs_j]
                
                if obs_grid.get(vis_i, vis_j) == None:
                    self.vis_obs[abs_i, abs_j] = 1
                else:
                    self.vis_obs[abs_i, abs_j] = obs_grid.get(vis_i, vis_j).encode()
                # print(obj)

        rotated_mask = self.vis_mask.T[:, ::-1]
        specular_mask = rotated_mask[:, ::-1]

        rotated_obs = self.vis_obs.T[:, ::-1]
        specular_obs = rotated_obs[:, ::-1]


        # print(specular_obs)

    def look_for_goal(self):

        for row_index, row in enumerate(self.vis_obs):
            for col_index, element in enumerate(row):
                if isinstance(element, tuple):
                    if element[0] == self.goal_type and element[1] == self.goal_color:
                        return (row_index, col_index)
        return None

    def look_for_door(self):
        for row_index, row in enumerate(self.vis_obs):
            for col_index, element in enumerate(row):
                if isinstance(element, tuple):
                    if element[0] == 4:
                        return (row_index, col_index)
        return None
    
    def plan(self):
        self.goal_pos = self.look_for_goal()

        if self.scanned == 4:
            print("Scanned room now looking for door")
            door = self.look_for_door()
            return self.move_to_cell(door)
        
        
        while not self.goal_pos:
            self.scanned += 1
            return self.actions.left
        
        self.scanned = 0
                      
        return self.move_to_cell(self.goal_pos)
        
    
    def find_best_cell(self, target):
        pos = self.environment.unwrapped.agent_pos
        f_vec = self.environment.unwrapped.dir_vec

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
            distance = self.manhattan_distance(cell, target)

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
        pos = self.environment.unwrapped.agent_pos
        f_vec = self.environment.unwrapped.dir_vec
        r_dir = self.environment.unwrapped.right_vec

        direction_to_cell = cell_pos[0]-pos[0], cell_pos[1]-pos[1]

        
        if np.array_equal(direction_to_cell, np.array(f_vec)):
            print("Move forward")
            if isinstance(self.vis_obs[cell_pos[0], cell_pos[1]], tuple):
                if self.vis_obs[cell_pos[0], cell_pos[1]][0]:
                    return self.actions.toggle
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



    