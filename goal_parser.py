from minigrid.core.constants import OBJECT_TO_IDX, COLOR_TO_IDX, STATE_TO_IDX
from minigrid.envs.babyai.core.verifier import *
from subgoals import GoNextToSubgoal, OpenSubgoal, PickupSubgoal, DropSubgoal



def process_desc(desc):
        goal = desc #extract the goal from the mission information
        goal_type = goal.type
        goal_color = goal.color
        goal_lock = goal.loc
        if (goal_lock is None):
            goal_lock = "open"

        goal_type = OBJECT_TO_IDX[goal_type]
        goal_color = COLOR_TO_IDX[goal_color]
        goal_lock = STATE_TO_IDX[goal_lock]

        return [goal_type, goal_color, goal_lock]


def understand_goal(plan, instr):
    """
    Translate instructions into an internal form the agent can execute
    """
    subgoals = []

    if isinstance(instr, GoToInstr):
        subgoals.append(GoNextToSubgoal(plan,process_desc(instr.desc)))

    elif isinstance(instr, OpenInstr):       
        subgoals.append(GoNextToSubgoal(plan, process_desc(instr.desc), reason="Open"))
        subgoals.append(OpenSubgoal(plan))

    elif isinstance(instr, PickupInstr):
        # We pick up and immediately drop so
        # that we may carry other objects 
        subgoals.append(GoNextToSubgoal(plan, process_desc(instr.desc)))
        subgoals.append(PickupSubgoal(plan))
        subgoals.append(DropSubgoal(plan))


    elif isinstance(instr, PutNextInstr):     
        subgoals.append(GoNextToSubgoal(plan, process_desc(instr.desc_move)))
        subgoals.append(PickupSubgoal(plan, process_desc(instr.desc_move)))
        subgoals.append(GoNextToSubgoal(plan, process_desc(instr.desc_fixed), reason="PutNext"))
        subgoals.append(DropSubgoal(plan, process_desc(instr.desc_fixed)))


    elif isinstance(instr, BeforeInstr) or isinstance(instr, AndInstr):
        understand_goal(instr.instr_b)
        understand_goal(instr.instr_a)


    elif isinstance(instr, AfterInstr):
        understand_goal(instr.instr_a)
        understand_goal(instr.instr_b)

    else:
        raise ValueError(f"Unknown instruction type: {instr}")

    return subgoals
