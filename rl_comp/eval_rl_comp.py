import gymnasium as gym
from gymnasium import spaces
import numpy as np
from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env
from train_rl_comp import SpaceOptimisationEnv

if __name__ == "__main__":
    # Define the environment dimensions and component width
    width = 400
    height = 200
    
    # Not used for this 1D problem, but can be expanded
    component_width = 50
    
    def create_env():
        return SpaceOptimisationEnv(width, height, component_width)

    # Create vectorized environment
    env = make_vec_env(create_env, n_envs=1)
    
    # Load and evaluate the model
    model = PPO.load("space_optimiser", device="cpu")
    obs = env.reset()
    for _ in range(20):
        action, _ = model.predict(obs)
        obs, reward, terminated, truncated = env.step(action)
        if any(terminated) or any(truncated):
            break

    # Optimal number of standard-sized components
    optimal_components = (width - obs[0][0]) // component_width
    print(f"Optimal number of standard components: {optimal_components}")
    print(f"Remaining non-standard space: {obs[0][0]}")