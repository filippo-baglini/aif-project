import numpy as np

#seed 4: failed
###seed 4: failed

#seed 3 (91): 2271 ->2390 penalty=3,2278 penalty=4 (90), 2211 penalty=10 (89)
###seed 3 (91): 2445-2445(min) 

#seed 2: 2520 ->2496 penalty=5, 2467 penalty 4, 2442 penalty 3
###seed 2: 2450-2450(min)

#seed 1: 2267 ->2224 penalty=5, 2200 penalty 4, 2253 penalty 3
###seed 1: 2314-2325 (min)

def manhattan_distance(pos, target):
        """Calculate Manhattan distance between two points."""
        return np.abs(target[0] - pos[0]) + np.abs(target[1] - pos[1])

# def manhattan_distance_accounting_for_walls(pos, target, vis_obs, wall_penalty=4):
#         return np.abs(target[0] - pos[0]) + np.abs(target[1] - pos[1])

# def manhattan_distance_accounting_for_walls(pos, target, vis_obs, wall_penalty=5):
#         """Calculate Manhattan distance between two points."""
#          distances = [target[0] - pos[0], target[1] - pos[1]]
#         additional_distance = 0
#         if distances[0] < 0: #TARGET IS HIGHER THAN THE AGENT
#                 for i, row in enumerate(vis_obs):
#                         if i < target[0]:
#                                 continue
#                         if i == pos[0]:
#                                 break
#                         if vis_obs[i, pos[1]][0] == 2:
#                                 additional_distance += 5
        
#         if distances[0] > 0: #TARGET IS LOWER THAN THE AGENT
#                 for i, row in enumerate(vis_obs):
#                         if i < pos[0]:
#                                 continue
#                         if i == target[0]:
#                                 break
#                         if vis_obs[i, pos[1]][0] == 2:
#                                 additional_distance += 5
        
#         if distances[1] < 0: #TARGET IS TO THE LEFT OF THE AGENT
#                 row = vis_obs[pos[1]]
#                 for i, col in enumerate(row):
#                         if i < target[1]:
#                                 continue 
#                         if i == pos[1]:
#                                 break
#                         if row[i][0] == 2:
#                                 additional_distance += 5
        
#         if distances[1] > 0: #TARGET IS TO THE RIGHT OF THE AGENT
#                 row = vis_obs[pos[1]]
#                 for i, col in enumerate(row):
#                         if i < pos[1]:
#                                 continue 
#                         if i == target[1]:
#                                 break
#                         if row[i][0] == 2:
#                                 additional_distance += 5

#         return np.abs(target[0] - pos[0]) + np.abs(target[1] - pos[1]) + additional_distance



def manhattan_distance_accounting_for_walls(pos, target, vis_obs):
        """Calculate Manhattan distance between two points."""


        distances = [target[0] - pos[0], target[1] - pos[1]]
        additional_distance = 0
        
        # Base Manhattan distance (no wall penalty)
        base_distance = np.abs(distances[0]) + np.abs(distances[1])
        
        if distances[0] < 0: #TARGET IS HIGHER THAN THE AGENT
                for i,row in enumerate(vis_obs):
                        if i < target[0]:
                                continue
                        if i == pos[0]:
                                break
                        # if vis_obs[i, pos[1]][0] == 4: #door
                        #         additional_distance += np.abs(pos[0]-vis_obs[i, pos[1]][0])*2
                        if vis_obs[i, pos[1]][0] == 2: #wall
                            for j,element in enumerate(row):
                                #print(i, j)
                                if vis_obs[i,j][0] == 4: #door
                                    intervall=[pos[1], target[1]]
                                    if j in range(min(intervall), max(intervall) + 1):
                                        break
                                    else:
                                        min_dist= min(np.abs(pos[1]-j),np.abs(target[1]-j))
                                        additional_distance +=min_dist*2
                                        # additional_distance +=np.abs(pos[1]-j)*2

        
        if distances[0] > 0: #TARGET IS LOWER THAN THE AGENT
                for i,row in enumerate(vis_obs):
                        if i < pos[0]:
                                continue
                        if i == target[0]:
                                break
                        if vis_obs[i, pos[1]][0] == 2: #wall
                            for j,element in enumerate(row):
                                if vis_obs[i,j][0] == 4: #door
                                    intervall=[pos[1], target[1]]
                                    if j in range(min(intervall), max(intervall) + 1):
                                        break
                                    else:
                                        min_dist= min(np.abs(pos[1]-j),np.abs(target[1]-j))
                                        additional_distance +=min_dist*2
                                        # additional_distance +=np.abs(pos[1]-j)*2
                                        
        if distances[1] < 0: #TARGET IS TO THE LEFT OF THE AGENT
                row = vis_obs[pos[1]]
                for i,col in enumerate(row):
                        if i < target[1]:
                                continue 
                        if i == pos[1]:
                                break
                        if row[i][0] == 2: #wall
                            for j,element in enumerate(col):
                                if vis_obs[j,i][0] == 4: #door
                                    intervall=[pos[0], target[0]]
                                    if j in range(min(intervall), max(intervall) + 1):
                                        break
                                    else:
                                        min_dist= min(np.abs(pos[0]-j),np.abs(target[0]-j))
                                        additional_distance +=min_dist*2
                                        #additional_distance +=np.abs(pos[0]-j)*2
        
        if distances[1] > 0: #TARGET IS TO THE RIGHT OF THE AGENT
                row = vis_obs[pos[1]]
                for i,col in enumerate(row):
                        if i < pos[1]:
                                continue 
                        if i == target[1]:
                                break
                        if row[i][0] == 2: #wall
                            for j,element in enumerate(col):
                                if vis_obs[j,i][0] == 4: #door
                                    intervall=[pos[0], target[0]]
                                    if j in range(min(intervall), max(intervall) + 1):
                                        break
                                    else:
                                        min_dist= min(np.abs(pos[0]-j),np.abs(target[0]-j))
                                        additional_distance +=min_dist*2
                                        #additional_distance +=np.abs(pos[0]-j)*2


        
        return base_distance + additional_distance
