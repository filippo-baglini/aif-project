import time

class Subgoal:
    def __init__(self, planner):
        self.planner = planner

    def __call__(self):
        raise NotImplementedError

class GoNextToSubgoal(Subgoal):
    def __init__(self, planner, target, reason="GoNextTo", target_pos=None):
        super().__init__(planner)
        self.target = target
        self.reason = reason
        self.target_pos = target_pos

        self.action = None

    def __call__(self):
        
        self.action = None

        if self.target_pos is None:
            #time.sleep(1)
            self.planner.sub_goals.insert(0, ExploreSubgoal(self.planner, self.target, self.reason))
            return self.planner.actions.done
        
        if self.reason == "Explore":
            if self.planner.look_for_goal(self.target[0], self.target[1], self.target[2]) != None:
                self.action = self.planner.actions.done
            if self.planner.vis_mask[self.target_pos]:
                self.action = self.planner.actions.done

        neighbors = self.planner.neighbors(self.target_pos)
        if self.reason == "Open":
            # print("OPEN")
            if self.planner.vis_obs[self.target_pos][2] == 2 or any(self.planner.vis_obs[n[0], n[1]][2] == 2 for n in neighbors):
                if self.planner.vis_obs[self.target_pos][2] == 2:
                    color=self.planner.vis_obs[self.target_pos][1]
                else:
                    for n in neighbors:
                        if self.planner.vis_obs[n[0], n[1]][2] == 2:
                            color = self.planner.vis_obs[n][1]
                if self.planner.carrying_object is not None:

                    if self.planner.carrying_object[1] != color or self.planner.carrying_object[0] != 5:
                        self.planner.sub_goals.insert(0, GoNextToSubgoal(self.planner, [5,color,None], "PickUp_Keep_important"))

                        return self.planner.actions.done
                    
                else:
                    self.planner.sub_goals.insert(0, GoNextToSubgoal(self.planner, [5,color,None], "PickUp_Keep_important"))

                    return self.planner.actions.done
                
        if self.action is None:
            self.action = self.planner.move_to_target(self.target_pos)

        if self.action == "BLOCKED":
            # print("BLOCKED")
            # time.sleep(5)
            if self.planner.carrying:
                empty_cell = self.planner.find_closest_empty_cell(self.planner.pos)

                if self.planner.carrying_target in self.planner.important_objects:
                    # print("IMPORTANT OBJECTS:", self.planner.important_objects)
                    self.planner.save_path = self.planner.path
                    self.planner.sub_goals.insert(0, GoNextToSubgoal(self.planner, self.planner.carrying_target, "PickUp_Keep_important"))
                    self.planner.sub_goals.insert(0, GoNextToSubgoal(self.planner, self.planner.target_in_cell(self.planner.path[0], self.target), "PickUp_NoKeep_Move", self.planner.cell_in_front()))
                    self.planner.sub_goals.insert(0, GoNextToSubgoal(self.planner, self.planner.carrying_target, "Drop_important", empty_cell))

                else:
                    self.planner.sub_goals.insert(0, GoNextToSubgoal(self.planner, self.target, "Drop", empty_cell))

            else:
                self.planner.sub_goals.insert(0, PickupSubgoal(self.planner, self.planner.target_in_cell(self.planner.path[0], self.target)))
                print(self.planner.target_in_cell(self.planner.path[0], self.target))
            return self.planner.actions.done
        
        if self.action == "BLOCKED_SIDE":
            # print("BLOCKED SIDE")
            # time.sleep(3)
            empty_cell = self.planner.find_closest_empty_cell(self.planner.pos)
            # print("TARGET:", self.target)
            if self.planner.carrying_target in self.planner.important_objects:
                # print("IMPORTANT OBJECTS:", self.planner.important_objects)
                self.planner.save_path = self.planner.path
                self.planner.sub_goals.insert(0, GoNextToSubgoal(self.planner, self.planner.carrying_target, "PickUp_Keep_important"))
                self.planner.sub_goals.insert(0, GoNextToSubgoal(self.planner, self.planner.target_in_cell(self.planner.path[0], self.target), "PickUp_NoKeep_Move", self.planner.path[0]))
                self.planner.sub_goals.insert(0, GoNextToSubgoal(self.planner, self.planner.carrying_target, "Drop_important", empty_cell))

            else:
                self.planner.sub_goals.insert(0, GoNextToSubgoal(self.planner, self.target, "Drop", empty_cell))

            return self.planner.actions.done 

        if self.action == "OPEN DOOR":
            self.planner.sub_goals.insert(0, OpenSubgoal(self.planner))

            return self.planner.actions.done
        
        if self.action == self.planner.actions.done:
            self.planner.sub_goals.pop(0)

            if self.reason == "PickUp_Keep":
                self.planner.sub_goals.insert(0, PickupSubgoal(self.planner, self.target))

            elif self.reason == "PickUp_NoKeep":
                self.planner.sub_goals.insert(0, DropSubgoal(self.planner))
                self.planner.sub_goals.insert(0, PickupSubgoal(self.planner, self.target))

            elif self.reason == "PickUp_NoKeep_Move":
                empty_cell = self.planner.find_closest_empty_cell_avoiding_previous_path(self.planner.cell_in_front())
                # print("EMPTY CELL:", empty_cell)
                self.planner.sub_goals.insert(0, GoNextToSubgoal(self.planner, self.target, "Drop", empty_cell))
                self.planner.sub_goals.insert(0, PickupSubgoal(self.planner, self.target))

            elif self.reason == "PickUp_Keep_important":
                self.planner.sub_goals.insert(0, PickupSubgoal(self.planner, self.target))
                self.planner.important_objects.append(self.target)
                # print("IMPORTANT OBJECTS:", self.planner.important_objects)

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
    def __init__(self, planner, target):
        super().__init__(planner)
        self.target = target

    def __call__(self):
        if self.planner.carrying:

            self.planner.sub_goals.pop(0)
            
            empty_cell = self.planner.find_closest_empty_cell(self.planner.pos)

            if empty_cell is None:
                return self.planner.actions.left
            
            self.planner.sub_goals.insert(0, GoNextToSubgoal(self.planner, self.target, "PickUp_Keep"))
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
        self.target_pos = self.planner.look_for_goal(self.target[0], self.target[1], self.target[2])

        if self.target_pos is None:
            #time.sleep(1)
            self.frontier = self.planner.find_frontiers()
            if self.frontier == self.planner.prev_frontier:
                self.frontier = self.planner.find_new_frontiers(self.frontier)

            # print("FRONTIERA:", self.frontier)
            # time.sleep(1)
            #print("FRONTIERA:", self.frontier)
            neighbors = self.planner.neighbors(self.frontier)
            if self.planner.vis_obs[self.frontier][2] == 2:

                target = self.frontier
                self.planner.sub_goals.pop(0)
                self.planner.prev_frontier = self.frontier
                # print("TARGET:", target)
                self.planner.sub_goals.insert(0, GoNextToSubgoal(self.planner, self.planner.door_in_cell(target), "Open", target))

            
            elif any(self.planner.vis_obs[n[0], n[1]][2] == 2 for n in neighbors):
                for n in neighbors:
                    if self.planner.vis_obs[n[0], n[1]][2] == 2:
                        target = n
                self.planner.sub_goals.pop(0)
                self.planner.prev_frontier = self.frontier
                # print("TARGET:", target)
                self.planner.sub_goals.insert(0, GoNextToSubgoal(self.planner, self.planner.door_in_cell(target), "Open", target))
            
            else:
                self.planner.sub_goals.pop(0)
                self.planner.prev_frontier = self.frontier
                self.planner.sub_goals.insert(0, GoNextToSubgoal(self.planner, self.target, "Explore", self.frontier))

            return self.planner.actions.done
        
        else:
            self.planner.sub_goals.pop(0)
            if self.reason == "PutNext":
                self.target_pos = self.planner.find_closest_drop_cell(self.target_pos)
                print("DROP CELL:", self.target_pos)
                self.planner.drop_pos = self.target_pos
                self.planner.sub_goals[0].target_pos = self.target_pos
            else:
                self.planner.sub_goals[0].target_pos = self.target_pos

            return self.planner.actions.done