from typing import Optional

from gymnasium import Env

from entity import Entity
from planner import Planner

class Bot:

    def __init__ (self, env):

        #Init plan instance of bot passing only env
        self.plan = Planner(env)
        self.env = env
        self.door_found: Optional[Entity] = None

    def take_action(self, env: Env):

        #First action is update plan instance
        self.plan()

        # Check if the goal is visible
        goal_pos = self.plan.look_for_goal()  # Returns the goal's position if visible, else None
        if goal_pos is None:
            print("Goal not visible, exploring env..")
            carried_item = env.unwrapped.carrying
            keys = self.plan.look_for_keys()
            print("Found keys: {}".format(keys))

            if self.door_found is not None:
                if carried_item is None:
                    if self.door_found.color in keys:
                        print("I already have seen the key")

                        key = keys[self.door_found.color]
                        return self.plan.move_to_target(key.pos)

                else:
                    print("Going to the door")
                    return self.plan.move_to_target(self.door_found.pos)

            door = self.plan.look_for_door()
            if door is not None:
                self.door_found = Entity(pos=door[1], color=door[0])
                print(f"Door found: {self.door_found}")
                if self.door_found.color in keys:
                    print("I already have seen the key")

                    key = keys[self.door_found.color]
                    return self.plan.move_to_target(key.pos)

            return self.plan.find_frontiers() # Rotate left to explore

        else:
            print("Goal Found!")
            return self.plan.move_to_target(goal_pos)