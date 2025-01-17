import sys
import os
# Get the absolute path of the parent directory of the project
script_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.abspath(os.path.join(script_dir, "../"))

# Append the project directory to sys.path
sys.path.append(project_dir)

import gymnasium as gym
from src.bot import Bot
from src.goal_parser import *

# Define the list of environments to test
broken_bonus_envs = {
    "BabyAI-PutNextS5N2Carrying-v0",
    "BabyAI-PutNextS6N3Carrying-v0",
    "BabyAI-PutNextS7N4Carrying-v0",
    "BabyAI-KeyInBox-v0",
}

# Get all BabyAI environments (excluding the broken ones)
babyai_envs = [
    k_i for k_i in gym.envs.registry.keys()
    if k_i.split("-")[0] == "BabyAI" and k_i not in broken_bonus_envs
]

# Define the number of seeds to test
num_first_seed = 0
num_last_seed = 101

# Results dictionary to store data for each seed
seed_results = {}

if __name__ == "__main__":
    print(f"Number of BabyAI environments: {len(babyai_envs)}")

    for seed in range(num_first_seed, num_last_seed, 1):  # Iterate through seeds
        print(f"Testing seed: {seed}")
        total_steps = 0
        completed_missions = 0

        for j, env_id in enumerate(babyai_envs):  # Loop through all environments
            print(f"Testing environment: {env_id}")

            # Create environment
            env = gym.make(env_id)
            env.reset(seed=seed)

            # Print the mission description
            print(env.unwrapped.mission)

            bot = Bot(env)
            max_steps = 500
            num_steps = 0

            for i in range(max_steps):
                action = bot.take_action(env)  # Call the test function
                if action == "FAILURE":
                    print(f"Level failed at seed {seed}: {env_id}")
                    break

                obs, reward, terminated, truncated, info = env.step(action)
                num_steps += 1

                if terminated:
                    total_steps += num_steps
                    completed_missions += 1
                    break

                if i == (max_steps - 1):
                    print("Max steps taken")
            print(f"-----------------------{seed}---{j}----------------------")
            env.close()

        # Save results for this seed
        seed_results[seed] = {"total_steps": total_steps, "completed_missions": completed_missions}

    # Print the results for all seeds
    print("Results per seed:")
    for seed, results in seed_results.items():
        print(f"Seed {seed}: Total Steps = {results['total_steps']}, Completed Missions = {results['completed_missions']}")

    # Save results to a file
    with open("../results/OurBot_results.txt", "w") as file:
        for seed, results in seed_results.items():
            file.write(f"Seed {seed}: Total Steps = {results['total_steps']}, Completed Missions = {results['completed_missions']}\n")

