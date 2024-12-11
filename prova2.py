from __future__ import annotations
import gymnasium as gym
from minigrid.manual_control import ManualControl
import numpy as np
import pygame


def main():
    # Create the environment with rgb_array render mode
    env = gym.make("BabyAI-GoToImpUnlock-v0", render_mode="rgb_array")

    # Set a clean video directory
    video_folder = "/home/filippo/aif-project/videos"
    env = gym.wrappers.RecordVideo(
        env,
        video_folder,
        episode_trigger=lambda e: True,  # Record all episodes
    )

    # Initialize pygame properly
    pygame.init()

    # Enable manual control for testing
    manual_control = ManualControl(env, seed=np.random.randint(1, 100))

    try:
        manual_control.start()  # Start the manual control
    except Exception as e:
        print(f"Error during manual control: {e}")
    finally:
        env.close()  # Ensure the environment is properly closed
        pygame.quit()  # Quit pygame cleanly

    
if __name__ == "__main__":
    main()
