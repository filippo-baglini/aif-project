
class Subgoal:
    def __init__(self, planner):
        self.planner = planner

    def __call__(self):
        raise NotImplementedError

class GoNextToSubgoal(Subgoal): #This class is used to move the agent to a target position and the reason dictates how the agent will behave when it reaches the target
    def __init__(self, planner, target, reason="GoNextTo", target_pos=None):
        super().__init__(planner)
        self.target = target
        self.reason = reason
        self.target_pos = target_pos

        self.action = None

    def __call__(self):
        
        self.action = None

        if self.target_pos is None: #If target position is not defined we request ExploreSubgoal to handle what target position to consider
            self.planner.sub_goals.insert(0, ExploreSubgoal(self.planner, self.target, self.reason))
            return self.planner.actions.done
        
        if self.reason == "Explore": #Continous scan for target even during exploration towards frontier to not waste steps if target is found
            if self.planner.look_for_goal(self.target[0], self.target[1], self.target[2]) != None:
                self.planner.prev_frontier = None
                self.action = self.planner.actions.done
            if self.planner.vis_mask[self.target_pos]:
                self.action = self.planner.actions.done
         
        if self.reason == "PutNext": 
            if self.target[0] != 4:
                prova_target = self.planner.look_for_goal(self.target[0], self.target[1], self.target[2])
                neighbors = self.planner.neighbors(prova_target)
                if (self.target not in neighbors):
                    target = self.planner.find_closest_drop_cell(prova_target)
                    self.target_pos = target

        neighbors = self.planner.neighbors(self.target_pos)
        if self.reason == "Open":
            if self.planner.vis_obs[self.target_pos][2] == 2 or any(self.planner.vis_obs[n[0], n[1]][2] == 2 for n in neighbors): #Check if door we are supposed to open is locked
                if self.planner.vis_obs[self.target_pos][2] == 2:
                    color=self.planner.vis_obs[self.target_pos][1]
                else:
                    for n in neighbors:
                        if self.planner.vis_obs[n[0], n[1]][2] == 2:
                            color = self.planner.vis_obs[n][1]
                if self.planner.carrying_object is not None: #Check if carrying object 

                    if self.planner.carrying_object[1] != color or self.planner.carrying_object[0] != 5: #Check if carrying object is not key we need
                        self.planner.sub_goals.insert(0, GoNextToSubgoal(self.planner, [5,color,None], "PickUp_Keep_important")) #If not key we need we init a new subgoal to pick up the key

                        return self.planner.actions.done
                    
                else:
                    self.planner.sub_goals.insert(0, GoNextToSubgoal(self.planner, [5,color,None], "PickUp_Keep_important")) #If not carrying object we init a new subgoal to pick up the key

                    return self.planner.actions.done
                
        if self.action is None:
            self.action = self.planner.move_to_target(self.target_pos) #We call function to move towards target position

        if self.action == "FAILURE": #If we get a failure we interrupt bot and stop environment
            return "FAILURE"

        if self.action == "BLOCKED": #Handles blocked frontal path

            if self.planner.carrying: #Check if we are carrying 
                empty_cell = self.planner.find_closest_empty_cell(self.planner.pos)

                if self.planner.carrying_target in self.planner.important_objects: #Check if we are carrying important object for next subgoal

                    self.planner.save_path = self.planner.path #Save the current path we were following
                    
                    #Init subgoal where we drop important object and save coords
                    #Init subgoal to pick up and move blocking object
                    #Init subgoal to to return to dropped important item and pick it up again
                    self.planner.sub_goals.insert(0, GoNextToSubgoal(self.planner, self.planner.carrying_target, "PickUp_Keep_important"))
                    self.planner.sub_goals.insert(0, GoNextToSubgoal(self.planner, self.planner.target_in_cell(self.planner.path[0], self.target), "PickUp_NoKeep_Move", self.planner.cell_in_front()))
                    self.planner.sub_goals.insert(0, GoNextToSubgoal(self.planner, self.planner.carrying_target, "Drop_important", empty_cell))
                    
                else:
                    if self.reason == "Drop": #Check if item was supposed to be dropped somewhere specific

                        self.planner.save_path.extend(self.planner.path) #Extends the current path with the new path for dropping item

                        #Init subgoal where we drop object temporarily
                        #Init subgoal to pick up and move blocking object
                        #Init subgoal to to return to dropped item and pick it up again
                        self.planner.sub_goals.insert(0, GoNextToSubgoal(self.planner, self.planner.carrying_target, "PickUp_Keep"))
                        self.planner.sub_goals.insert(0, GoNextToSubgoal(self.planner, self.planner.target_in_cell(self.planner.path[0], self.target), "PickUp_NoKeep_Move", self.planner.cell_in_front()))
                        self.planner.sub_goals.insert(0, GoNextToSubgoal(self.planner, self.planner.carrying_target, "Drop", empty_cell))
                        
                    else:
                        self.planner.sub_goals.insert(0, GoNextToSubgoal(self.planner, self.target, "Drop", empty_cell))

            else:
                #If not carrying we init a new subgoal to pick up the object blocking our path
                self.planner.sub_goals.insert(0, PickupSubgoal(self.planner, self.target))

            return self.planner.actions.done
        
        if self.action == "BLOCKED_SIDE": #Handles blocked side path and we are carrying object

            empty_cell = self.planner.find_closest_empty_cell(self.planner.pos)

            if self.planner.carrying_target in self.planner.important_objects: #Check if we are carrying important object for next subgoal
   
                self.planner.save_path = self.planner.path #Save the current path we were following

                #Init subgoal where we drop important object and save coords
                #Init subgoal to pick up and move blocking object
                #Init subgoal to to return to dropped important item and pick it up again
                self.planner.sub_goals.insert(0, GoNextToSubgoal(self.planner, self.planner.carrying_target, "PickUp_Keep_important"))
                self.planner.sub_goals.insert(0, GoNextToSubgoal(self.planner, self.planner.target_in_cell(self.planner.path[0], self.target), "PickUp_NoKeep_Move", self.planner.path[0]))
                self.planner.sub_goals.insert(0, GoNextToSubgoal(self.planner, self.planner.carrying_target, "Drop_important", empty_cell))

            else:
                if self.reason == "Drop": #Check if item was supposed to be dropped somewhere specific
                    
                    self.planner.save_path.extend(self.planner.path)

                    #Init subgoal where we drop object temporarily
                    #Init subgoal to pick up and move blocking object
                    #Init subgoal to to return to dropped item and pick it up again
                    self.planner.sub_goals.insert(0, GoNextToSubgoal(self.planner, self.planner.carrying_target, "PickUp_Keep"))
                    self.planner.sub_goals.insert(0, GoNextToSubgoal(self.planner, self.planner.target_in_cell(self.planner.path[0], self.target), "PickUp_NoKeep_Move", self.planner.path[0]))
                    self.planner.sub_goals.insert(0, GoNextToSubgoal(self.planner, self.planner.carrying_target, "Drop", empty_cell))

                else:
                    #If carrying useless object we init a new subgoal to drop it
                    self.planner.sub_goals.insert(0, GoNextToSubgoal(self.planner, self.target, "Drop", empty_cell))

            return self.planner.actions.done 

        if self.action == "OPEN DOOR": #Handles open door subgoal
            self.planner.sub_goals.insert(0, OpenSubgoal(self.planner))

            return self.planner.actions.done
        
        if self.action == self.planner.actions.done: #If we reached target position we handle the reason for the subgoal
            self.planner.sub_goals.pop(0)

            if self.reason == "PickUp_Keep":
                self.planner.sub_goals.insert(0, PickupSubgoal(self.planner, self.target))

            elif self.reason == "PickUp_NoKeep": 
                self.planner.sub_goals.insert(0, DropSubgoal(self.planner))
                self.planner.sub_goals.insert(0, PickupSubgoal(self.planner, self.target))

            elif self.reason == "PickUp_NoKeep_Move": 
                empty_cell = self.planner.find_closest_empty_cell_avoiding_previous_path(self.planner.cell_in_front())
                #We call avoid path funtion since we typically move the object to not block the path we need to bring another object through
                self.planner.sub_goals.insert(0, GoNextToSubgoal(self.planner, self.target, "Drop", empty_cell))
                self.planner.sub_goals.insert(0, PickupSubgoal(self.planner, self.target))

            elif self.reason == "PickUp_Keep_important": 
                self.planner.sub_goals.insert(0, PickupSubgoal(self.planner, self.target))

                if self.target not in self.planner.important_objects:
                    self.planner.important_objects.append(self.target)

            elif self.reason == "Drop_important":
                self.planner.sub_goals.insert(0, DropSubgoal(self.planner))
                self.planner.important_objects_coords.append(self.planner.cell_in_front())
                
            elif self.reason == "PutNext":
                self.planner.important_objects.remove(self.planner.carrying_target) 
                self.planner.sub_goals.insert(0, DropSubgoal(self.planner))

            elif self.reason == "Open":
                self.planner.sub_goals.insert(0, OpenSubgoal(self.planner))

            elif self.reason == "Drop":
                self.planner.sub_goals.insert(0, DropSubgoal(self.planner))

        return self.action
            

class OpenSubgoal(Subgoal):
    def __init__(self, planner):
        super().__init__(planner)
        
    def __call__(self):
        if (self.planner.vis_obs[self.planner.cell_in_front()][2] == 0): #Handles opening an already opened door
            action = self.planner.actions.toggle           
        else:
            action = self.planner.actions.toggle
            self.planner.sub_goals.pop(0)
            
        return action    
    
    
class PickupSubgoal(Subgoal):
    def __init__(self, planner, target, reason = "PickUp_Keep"):
        super().__init__(planner)
        self.target = target
        self.reason  = reason

    def __call__(self):
        if self.planner.carrying: #Handles the case where the agent is already carrying an object

            self.planner.sub_goals.pop(0)
            
            empty_cell = self.planner.find_closest_empty_cell(self.planner.pos)
            
            #Init subgoal to drop object
            #Init subgoal where we pass reason for picking up object
            self.planner.sub_goals.insert(0, GoNextToSubgoal(self.planner, self.target, self.reason))
            self.planner.sub_goals.insert(0, GoNextToSubgoal(self.planner, None, "Drop", empty_cell))
            return self.planner.actions.done
        
        action = self.planner.actions.pickup
        self.planner.carrying = True
        self.planner.carrying_target = self.target
        self.planner.carrying_object = self.planner.vis_obs[self.planner.cell_in_front()]

        self.planner.sub_goals.pop(0)

        return action


class DropSubgoal(Subgoal):
    def __init__(self, planner):
        super().__init__(planner)

    def __call__(self):

        action = self.planner.actions.drop
        self.planner.sub_goals.pop(0)

        self.planner.carrying = False
        self.planner.carrying_object = None
        self.planner.carrying_target = None

        return action
    

class ExploreSubgoal(Subgoal):
    def __init__(self, planner, target, reason="GoNextTo"):
        super().__init__(planner)

        self.target = target
        self.target_pos = None
        self.reason = reason

        self.frontier = None
        self.sub_goal_complete = False
        self.action = None

    def __call__(self):
        self.target_pos = self.planner.look_for_goal(self.target[0], self.target[1], self.target[2]) #Look for target position

        if self.target_pos is None: #Target isnt found we look for a frontier

            self.frontier = self.planner.find_frontiers() 

            if self.frontier == self.planner.prev_frontier: #Avoids getting stuck in a loop calling the same frontier
                self.frontier = self.planner.find_new_frontiers(self.frontier)

            if self.frontier is None: #If no frontier is found we interrupt bot and stop environment
                return "FAILURE"

            neighbors = self.planner.neighbors(self.frontier)
         
            if any(self.planner.vis_obs[n[0], n[1]][2] == 2 for n in neighbors): #Check if frontier is behind a locked door
                for n in neighbors:
                    if self.planner.vis_obs[n[0], n[1]][2] == 2:
                        target = n
                self.planner.sub_goals.pop(0)
                self.planner.prev_frontier = self.frontier

                #Init subgoal to open door and eventually look for key
                self.planner.sub_goals.insert(0, GoNextToSubgoal(self.planner, self.planner.door_in_cell(target), "Open", target))
            
            else:
                self.planner.sub_goals.pop(0)
                self.planner.prev_frontier = self.frontier

                #Init subgoal to move towards frontier
                self.planner.sub_goals.insert(0, GoNextToSubgoal(self.planner, self.target, "Explore", self.frontier))

            return self.planner.actions.done
        
        else:

            self.planner.sub_goals.pop(0)

            
            if self.reason == "PutNext":

                #If we are supposed to put object next to target we find closest empty cell and consider it as target position
                self.target_pos = self.planner.find_closest_drop_cell(self.target_pos)
                self.planner.drop_pos = self.target_pos
                self.planner.sub_goals[0].target_pos = self.target_pos

            else:

                #If target is found we move towards target position
                self.planner.sub_goals[0].target_pos = self.target_pos

            return self.planner.actions.done