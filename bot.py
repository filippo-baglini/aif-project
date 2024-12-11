import numpy as np
import gymnasium as gym
from minigrid.utils.baby_ai_bot import BabyAIBot

class Bot:

    def __init__ (self, environment):
        
        #environment to solve
        self.environment = environment

        #Initial goal
        self.mission = self.environment.unwrapped.mission

        self.vis_mask = np.zeros(
            shape=(environment.unwrapped.width, environment.unwrapped.height), dtype=bool
        )

        print (self.vis_mask)

    def take_action(self, environment):
        
        #return(self.environment.action_space.sample())
        return(0)
    
    def _process_obs(self):
        """Parse the contents of an observation/image, update our state, 
        rotate the vis_mask to the right, and make it specular."""
        
        _, vis_mask = self.environment.unwrapped.gen_obs_grid()

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

        # Rotate the visibility mask to the right (90 degrees clockwise)
        rotated_mask = self.vis_mask.T[:, ::-1]

        # Make the rotated mask specular (flip along the vertical axis)
        specular_mask = rotated_mask[:, ::-1]

        # Print the resulting mask for debugging
        # print("Original Visibility Mask:")
        # print(self.vis_mask)
        print("Rotated and Specular Visibility Mask:")
        print(specular_mask)

        # Optionally save the modified mask
        #self.vis_mask = specular_mask


