from minigrid.core.constants import OBJECT_TO_IDX, COLOR_TO_IDX, STATE_TO_IDX
from minigrid.envs.babyai.core.verifier import *
from subgoals import GoNextToSubgoal, OpenSubgoal, PickupSubgoal, DropSubgoal



def process_desc(desc):
        goal = desc #extract the goal from the mission information
        goal_type = goal.type
        goal_color = goal.color
        goal_lock = goal.loc

        print(goal_type, goal_color, goal_lock)
        if (goal_lock is None):
            goal_lock = "open"

        if (goal_color is None):
            goal_color = "red"

        goal_type = OBJECT_TO_IDX[goal_type]
        goal_color = COLOR_TO_IDX[goal_color]
        goal_lock = STATE_TO_IDX[goal_lock]

        return [goal_type, goal_color, goal_lock]


def understand_goal(plan, instr):
    """
    Translate instructions into an internal form the agent can execute
    """
  
    print(instr)

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
        plan.sub_oals.append(GoNextToSubgoal(plan, process_desc(instr.desc_move), reason="PickUp"))
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
