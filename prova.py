from __future__ import annotations

import gymnasium as gym
import threading
import time
from minigrid.utils.baby_ai_bot import BabyAIBot

broken_bonus_envs = {
    "BabyAI-PutNextS5N2Carrying-v0",
    "BabyAI-PutNextS6N3Carrying-v0",
    "BabyAI-PutNextS7N4Carrying-v0",
    "BabyAI-KeyInBox-v0",
}

# Get all BabyAI environments (except the broken ones)
babyai_envs = [
    k_i for k_i in gym.envs.registry.keys()
    if k_i.split("-")[0] == "BabyAI" and k_i not in broken_bonus_envs
]


seed_results = {}
num_step = []
num_completed_missions = []

def test_bot(env_id):
    """
    The BabyAI Bot should be able to solve all BabyAI environments,
    allowing us therefore to generate demonstrations.
    """
    # Use the parameter env_id to make the environment
    env = gym.make(env_id)
    env = gym.make("BabyAI-UnlockToUnlock-v0", render_mode = "human")
    #env = gym.make("BabyAI-Unlock-v0", render_mode = "human")
    #env = gym.make("BabyAI-GoToImpUnlock-v0", render_mode = "human")
    # env = gym.make("BabyAI-BossLevelNoUnlock-v0", render_mode="human") # for visual debugging
    # env = gym.make("BabyAI-SynthS5R2-v0", render_mode = "human")

    # reset env
    curr_seed = 0

    num_steps = 500
    steps = 0
    terminated = False

    seed_results = {}

    while not terminated:
        env.reset(seed=15)
        #print (env.observation_space)

        # Create expert bot
        expert = BabyAIBot(env)

        last_action = None

        for _step in range(num_steps):
            action = expert.replan(last_action)
            obs, reward, terminated, truncated, info = env.step(action)
            steps += 1
            last_action = action
            env.render()

            if terminated:
                # print(f"PROVA NUM_STEPS: {steps}")
                # result = (env_id, steps)
                num_step.append(_step)
                num_completed_missions.append(env_id)
                break

            if _step == num_steps - 1:
                num_step.append(_step)
                # print("MAX STEPS TAKEN")
                return

    env.close()

if __name__ == "__main__":
    # Run a specific environment for debugging
    for seed in range (1, 3, 1):

        for j, env_id in enumerate(babyai_envs):  # Loop through all environments
            print(f"Testing environment: {env_id}")
            print(f"-----------------{seed}-{j}--------------------------------")
            test_bot(env_id)  # Call the test function
        
        total_num_step = sum(num_step)
        completed_missions = len(num_completed_missions)

        seed_results[seed] = {"total_steps": total_num_step, "completed_missions": completed_missions}

with open("results_summary_babyai_bot.txt", "w") as file:
    for seed, results in seed_results.items():
        file.write(f"Seed {seed}: Total Steps = {results['total_steps']}, Completed Missions = {results['completed_missions']}\n")