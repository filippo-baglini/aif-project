import numpy as np

def manhattan_distance(pos, target):
        """Calculate Manhattan distance between two points."""
        return np.abs(target[0] - pos[0]) + np.abs(target[1] - pos[1])

def manhattan_distance_accounting_for_walls(pos, target, vis_obs):
        """Calculate Manhattan distance between two points."""
        distances = [target[0] - pos[0], target[1] - pos[1]]
        return np.abs(target[0] - pos[0]) + np.abs(target[1] - pos[1])