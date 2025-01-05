
from minigrid.core.constants import OBJECT_TO_IDX, COLOR_TO_IDX, STATE_TO_IDX
from minigrid.envs.babyai.core.verifier import *
from subgoals import GoNextToSubgoal, OpenSubgoal, PickupSubgoal, DropSubgoal
import time



def process_desc(desc):
        goal = desc #extract the goal from the mission information
        goal_type = goal.type
        goal_color = goal.color
        goal_location = goal.loc

        goal_type = OBJECT_TO_IDX[goal_type] if goal_type is not None else None
        goal_color = COLOR_TO_IDX[goal_color] if goal_color is not None else None

        print(goal_type, goal_color, goal_location)

        return [goal_type, goal_color, goal_location]


def understand_goal(plan, instr):
    """
    Translate instructions into an internal form the agent can execute
    """
  
    #print(instr)

    if isinstance(instr, GoToInstr):
        plan.sub_goals.append(GoNextToSubgoal(plan,process_desc(instr.desc)))

    elif isinstance(instr, OpenInstr):       
        plan.sub_goals.append(GoNextToSubgoal(plan, process_desc(instr.desc), reason="Open"))
        plan.sub_goals.append(OpenSubgoal(plan))

    elif isinstance(instr, PickupInstr):
        # We pick up and immediately drop so
        # that we may carry other objects 
        plan.sub_goals.append(GoNextToSubgoal(plan, process_desc(instr.desc), reason="PickUp"))
        plan.sub_goals.append(PickupSubgoal(plan, process_desc(instr.desc)))
        plan.sub_goals.append(DropSubgoal(plan))


    elif isinstance(instr, PutNextInstr):     
        plan.sub_goals.append(GoNextToSubgoal(plan, process_desc(instr.desc_move), reason="PickUp"))
        plan.sub_goals.append(PickupSubgoal(plan, process_desc(instr.desc_move)))
        plan.sub_goals.append(GoNextToSubgoal(plan, process_desc(instr.desc_fixed), reason="PutNext"))
        plan.sub_goals.append(DropSubgoal(plan))


    elif isinstance(instr, BeforeInstr):
        (understand_goal(plan,instr.instr_a))
        (understand_goal(plan,instr.instr_b))


    elif isinstance(instr, AfterInstr):
        (understand_goal(plan,instr.instr_b))
        (understand_goal(plan,instr.instr_a))
        
    elif isinstance(instr, AndInstr):
        (understand_goal(plan,instr.instr_a))
        (understand_goal(plan,instr.instr_b))

    else:
        raise ValueError(f"Unknown instruction type: {instr}")

    return 



# # Direction from the agent to the object
#                     v = (i - env.agent_pos[0], j - env.agent_pos[1])
#  # (d1, d2) is an oriented orthonormal basis
#                     d1 = DIR_TO_VEC[env.agent_dir]
#                     d2 = (-d1[1], d1[0])

#                     # Check if object's position matches with location
#                     pos_matches = {
#                         "left": dot_product(v, d2) < 0,
#                         "right": dot_product(v, d2) > 0,
#                         "front": dot_product(v, d1) > 0,
#                         "behind": dot_product(v, d1) < 0,
#                     }
