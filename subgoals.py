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

        if self.target_pos is None:
            self.planner.sub_goals.insert(0, ExploreSubgoal(self.planner, self.target, self.reason))
            return self.planner.actions.done

        # if self.reason == "PutNext":
        #     target_cell = self.planner.find_closest_empty_cell(self.target_pos)
        #     self.action = self.planner.move_to_target(target_cell, "PutNext")

        # elif self.reason == "Drop":

        #     self.action = self.planner.move_to_target(self.target_pos, "Drop")

        # elif self.reason == "Open":
        #     self.action = self.planner.move_to_target(self.target_pos, "Open")

        # elif self.reason == "PickUp":
        #     self.action = self.planner.move_to_target(self.target_pos)

        # else:

        self.action = self.planner.move_to_target(self.target_pos)

        if self.action == "BLOCKED":
            # if self.planner.carrying:
            #     empty_cell = self.planner.find_closest_empty_cell(self.planner.pos)
            #     self.planner.sub_goals.insert(0, DropSubgoal(self.planner))
            #     self.planner.sub_goals.insert(0, GoNextToSubgoal(self.planner, self.target, "Drop", empty_cell))
            # else:
            self.planner.sub_goals.insert(0, PickupSubgoal(self.planner, self.target))

            return self.planner.actions.done
        
        if self.action == "BLOCKED_SIDE":
            self.planner.sub_goals.insert(0, PickupSubgoal(self.planner, self.target))

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
                
            
            elif self.reason == "PutNext":
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
        print(f"TARGET: {self.target}")
        if self.planner.carrying:

            self.planner.sub_goals.pop(0)
            
            empty_cell = self.planner.find_closest_empty_cell(self.planner.pos)

            if empty_cell is None:
                return self.planner.actions.left

            self.planner.sub_goals.insert(0, DropSubgoal(self.planner))
            self.planner.sub_goals.insert(0, GoNextToSubgoal(self.planner, None, "Drop", empty_cell))
            return self.planner.actions.done
        
        action = self.planner.actions.pickup
        self.planner.carrying = True
        self.planner.sub_goals.pop(0)

        return action

class DropSubgoal(Subgoal):
    def __init__(self, planner):
        super().__init__(planner)

    def __call__(self):

        action = self.planner.actions.drop
        self.planner.sub_goals.pop(0)

        self.planner.carrying = False

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
        #print("EXPLORING")
        #print(self.target)
        self.target_pos = self.planner.look_for_goal(self.target[0], self.target[1], self.target[2])
        print(self.target_pos)

        if self.target_pos is None:
            self.frontier = self.planner.find_frontiers()

            if self.frontier is None:
                return self.planner.actions.done
            else:
                                   
                self.action = self.planner.move_to_target(self.frontier)

                if self.action == "BLOCKED":
                    self.planner.sub_goals.insert(0, PickupSubgoal(self.planner, self.target))

                    return self.planner.actions.done
                
                if self.action == "BLOCKED_SIDE":
                    self.planner.sub_goals.insert(0, PickupSubgoal(self.planner, self.target))

                    return self.planner.actions.done

                if self.action == "OPEN DOOR":
                    self.planner.sub_goals.insert(0, OpenSubgoal(self.planner))
                    return self.planner.actions.done

                return self.action

        
        else:
            print(self.target_pos)
            if self.planner.vis_obs[self.target_pos][2] == 2:
                    color=self.planner.vis_obs[self.target_pos][1]
                    self.planner.sub_goals.insert(0, ExploreSubgoal(self.planner, [5,color,0]))
                    
            #self.planner.sub_goals.pop(0)

            if self.reason == "PutNext":
                self.target_pos = self.planner.find_closest_empty_cell(self.target_pos)
                self.planner.sub_goals[0].target_pos = self.target_pos
            else:
                self.planner.sub_goals[0].target_pos = self.target_pos
            return self.planner.actions.done