import sys
import os

# Get the absolute path of the parent directory of the project
script_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.abspath(os.path.join(script_dir, "../"))

# Append the project directory to sys.path
sys.path.append(project_dir)


import gymnasium as gym
from PIL import Image  # For GIF creation
from src.bot import Bot
from src.goal_parser import *
from minigrid.envs.babyai.core.verifier import *

# Setup project path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.abspath(os.path.join(script_dir, "../"))
sys.path.append(project_dir)

# Specify the environment
SPECIFIC_ENV = "BabyAI-SynthS5R2-v0"

# Initialize variables
frames = []  # To store rendered frames
reward_list = []

if __name__ == "__main__":
    print(f"Testing specific environment: {SPECIFIC_ENV}")

    try:
        # Create the environment
        env = gym.make(SPECIFIC_ENV, render_mode="rgb_array")  # Use rgb_array for frame capture
        env.reset(seed=3)
    except gym.error.Error:
        print(f"Environment {SPECIFIC_ENV} is not available.")
        sys.exit(1)

    # Print the mission
    print(f"Mission: {env.unwrapped.mission}")

    # Initialize bot
    bot = Bot(env)
    max_steps = 500
    num_steps = 0

    # Run the environment
    for step in range(max_steps):
        # Capture the frame
        frame = env.render()  # Capture the RGB frame
        frames.append(Image.fromarray(frame))  # Convert to PIL Image and store

        # Bot takes action
        action = bot.take_action(env)
        if action == "FAILURE":
            print(f"Mission failed in environment: {SPECIFIC_ENV}")
            break

        obs, reward, terminated, truncated, info = env.step(action)
        num_steps += 1

        if terminated:
            print(f"Mission completed in {num_steps} steps")
            reward_list.append((SPECIFIC_ENV, num_steps))
            break

        if step == (max_steps - 1):
            print("Reached maximum steps without completion")

    # Close the environment
    env.close()

    # Save GIF from captured frames
    gif_path = f"{SPECIFIC_ENV}_simulation.gif"
    frames[0].save(
        gif_path,
        save_all=True,
        append_images=frames[1:],  # Add the remaining frames
        duration=100,  # Duration per frame in milliseconds
        loop=0,  # Infinite loop
    )
    print(f"GIF saved as {gif_path}")

    # Print results
    if reward_list:
        total_steps = sum([steps for _, steps in reward_list])
        print(f"Environment: {SPECIFIC_ENV}, Steps Taken: {total_steps}")
        print(f"Mission Completed Successfully: {len(reward_list)} times")
    else:
        print(f"No missions completed in environment: {SPECIFIC_ENV}")
