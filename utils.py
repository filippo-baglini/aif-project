import numpy as np

def manhattan_distance(pos, target):
        """Calculate Manhattan distance between two points."""
        return np.abs(target[0] - pos[0]) + np.abs(target[1] - pos[1])

def manhattan_distance_accounting_for_walls(pos, target, vis_obs):
        """Calculate Manhattan distance between two points."""

        distances = [target[0] - pos[0], target[1] - pos[1]]
        additional_distance = 0
        
        # Base Manhattan distance (no wall penalty)
        base_distance = np.abs(distances[0]) + np.abs(distances[1])
        
        if distances[1] < 0: #TARGET IS HIGHER THAN THE AGENT
                interval=[pos[0], target[0]]
                agent_column = vis_obs[pos[0]]
                for i, element in enumerate(agent_column):
                       if i <= target[1]:
                              continue
                       if i >= pos[1]:
                              break
                       if element[0] == 2:
                              for j, col in enumerate(vis_obs):
                                     if col[i] == 4:
                                            if j in range(min(interval), max(interval) + 1):
                                                break 
                                            else:
                                                min_dist = min(np.abs(pos[0]-j),np.abs(target[0]-j))
                                                additional_distance += min_dist*2
                                                #return base_distance + additional_distance

        
        if distances[1] > 0: #TARGET IS LOWER THAN THE AGENT
                interval=[pos[0], target[0]]
                agent_column = vis_obs[pos[0]]
                for i, element in enumerate(agent_column):
                       if i <= pos[1]:
                              continue
                       if i >= target[1]:
                              break
                       if element[0] == 2:
                              for j, col in enumerate(vis_obs):
                                     if col[i] == 4:
                                            if j in range(min(interval), max(interval) + 1):
                                                break 
                                            else:
                                                min_dist = min(np.abs(pos[0]-j),np.abs(target[0]-j))
                                                additional_distance += min_dist*2
                                                #return base_distance + additional_distance
                                        
        if distances[0] < 0: #TARGET IS TO THE LEFT OF THE AGENT
                interval=[pos[0], target[0]]
                agent_row_index = pos[1]
                for i, col in enumerate(vis_obs):
                       if i <= target[0]:
                              continue
                       if i >= pos[0]:
                              break
                       if col[agent_row_index] == 2:
                              for j, element in enumerate(col):
                                     if col[j] == 4:
                                            if j in range(min(interval), max(interval) + 1):
                                                break 
                                            else:
                                                min_dist = min(np.abs(pos[1]-j),np.abs(target[1]-j))
                                                additional_distance += min_dist*2
                                                #return base_distance + additional_distance
        
        if distances[0] > 0: #TARGET IS TO THE RIGHT OF THE AGENT
                interval=[pos[0], target[0]]
                agent_row_index = pos[1]
                for i, col in enumerate(vis_obs):
                       if i <= pos[0]:
                              continue
                       if i >= target[0]:
                              break
                       if col[agent_row_index] == 2:
                              for j, element in enumerate(col):
                                     if col[j] == 4:
                                            if j in range(min(interval), max(interval) + 1):
                                                break 
                                            else:
                                                min_dist = min(np.abs(pos[1]-j),np.abs(target[1]-j))
                                                additional_distance += min_dist*2
                                                #return base_distance + additional_distance

        return base_distance + additional_distance

def manhattan_distance_accounting_for_objects(pos, target, vis_obs):
        """Calculate Manhattan distance between two points."""

        distances = [target[0] - pos[0], target[1] - pos[1]]
        additional_distance = 0
        
        # Base Manhattan distance (no wall penalty)
        base_distance = np.abs(distances[0]) + np.abs(distances[1])
        
        if distances[1] < 0: #TARGET IS HIGHER THAN THE AGENT
                interval=[pos[0], target[0]]
                target_column = vis_obs[target[0]]
                for i, element in enumerate(target_column):
                       if i <= target[1]:
                              continue
                       if i > pos[1]:
                              break
                       if element[0] in (5, 6, 7):
                                additional_distance += 3
                                                #return base_distance + additional_distance

        
        if distances[1] > 0: #TARGET IS LOWER THAN THE AGENT
                interval=[pos[0], target[0]]
                target_column = vis_obs[target[0]]
                for i, element in enumerate(target_column):
                       if i <= pos[1]:
                              continue
                       if i > target[1]:
                              break
                       if element[0] in (5, 6, 7):
                                additional_distance += 3
                                                #return base_distance + additional_distance
                                        
        if distances[0] < 0: #TARGET IS TO THE LEFT OF THE AGENT
                #sprint("ENTRATO")
                interval=[pos[0], target[0]]
                target_row_index = target[1]
                for i, col in enumerate(vis_obs):
                       #print(col[target_row_index])
                       if i < target[0]:
                              continue
                       if i >= pos[0]:
                              break
                       if col[target_row_index][0] in (5, 6, 7):
                              additional_distance += 3
                #print("TARGET, ADDITIONAL", target, additional_distance)
        
        if distances[0] > 0: #TARGET IS TO THE RIGHT OF THE AGENT
                interval=[pos[0], target[0]]
                target_row_index = target[1]
                for i, col in enumerate(vis_obs):
                       if i < pos[0]:
                              continue
                       if i >= target[0]:
                              break
                       if col[target_row_index][0] in (5, 6, 7):
                              additional_distance += 3
                                                #return base_distance + additional_distance

        return base_distance + additional_distance