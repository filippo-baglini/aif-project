import numpy as np

def manhattan_distance(pos, target):
        """Calculate Manhattan distance between two points."""
        return np.abs(target[0] - pos[0]) + np.abs(target[1] - pos[1])

def manhattan_distance_accounting_for_walls(pos, target, vis_obs):
        """Calculate Manhattan distance between two points."""
        distances = [target[0] - pos[0], target[1] - pos[1]]
        additional_distance = 0
        if distances[0] < 0: #TARGET IS HIGHER THAN THE AGENT
                for i, row in enumerate(vis_obs):
                        if i < target[0]:
                                continue
                        if i == pos[0]:
                                break
                        if vis_obs[i, pos[1]][0] == 2:
                                additional_distance += 5
        
        if distances[0] > 0: #TARGET IS LOWER THAN THE AGENT
                for i, row in enumerate(vis_obs):
                        if i < pos[0]:
                                continue
                        if i == target[0]:
                                break
                        if vis_obs[i, pos[1]][0] == 2:
                                additional_distance += 5
        
        if distances[1] < 0: #TARGET IS TO THE LEFT OF THE AGENT
                row = vis_obs[pos[1]]
                for i, col in enumerate(row):
                        if i < target[1]:
                                continue 
                        if i == pos[1]:
                                break
                        if row[i][0] == 2:
                                additional_distance += 5
        
        if distances[1] > 0: #TARGET IS TO THE RIGHT OF THE AGENT
                row = vis_obs[pos[1]]
                for i, col in enumerate(row):
                        if i < pos[1]:
                                continue 
                        if i == target[1]:
                                break
                        if row[i][0] == 2:
                                additional_distance += 5

        return np.abs(target[0] - pos[0]) + np.abs(target[1] - pos[1]) + additional_distance