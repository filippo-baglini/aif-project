import gymnasium as gym
from minigrid.utils.baby_ai_bot import BabyAIBot
import bot 
import utils
import time
from minigrid.core.constants import OBJECT_TO_IDX, COLOR_TO_IDX

def get_babyai_envs():
    broken_bonus_envs = {
        "BabyAI-PutNextS5N2Carrying-v0",
        "BabyAI-PutNextS6N3Carrying-v0",
        "BabyAI-PutNextS7N4Carrying-v0",
        "BabyAI-KeyInBox-v0",
    }
    return [
        key for key in gym.envs.registry.keys()
        if key.startswith("BabyAI") and key not in broken_bonus_envs
    ]

def run_environment_tests(env_id, max_steps=100):
    try:
        env = gym.make(env_id, render_mode="human")
        env.reset()
        bot_instance = bot.Bot(env)
        mission = bot_instance.mission
        goal_type, goal_color = utils.parse_mission(mission)
        goal_type = OBJECT_TO_IDX[goal_type]
        goal_color = COLOR_TO_IDX[goal_color]

        for step in range(max_steps):
            action = bot_instance.take_action(env)
            obs, _, terminated, truncated, _ = env.step(action)
            if terminated or truncated:
                break
            # Process observation here

    except Exception as e:
        print(f"Error in environment {env_id}: {e}")
    finally:
        env.close()

if __name__ == "__main__":
    babyai_envs = get_babyai_envs()
    for env_id in babyai_envs:
        print(f"Testing environment: {env_id}")
        run_environment_tests(env_id)
