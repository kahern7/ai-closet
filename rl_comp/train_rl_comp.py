import gymnasium as gym
from gymnasium import spaces
import numpy as np
from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env

class SpaceOptimisationEnv(gym.Env):
    def __init__(self, width, height, component_width):
        super(SpaceOptimisationEnv, self).__init__()
        self.width = width
        self.height = height
        self.component_width = component_width
        
        # Maximum number of standard components that can fit
        self.max_components = self.width // self.component_width

        # Action space: Number of standard components to place
        self.action_space = spaces.Discrete(self.max_components + 1)

        # Observation space: Remaining space after placing components
        self.observation_space = spaces.Box(
            low=0, high=self.width, shape=(1,), dtype=np.int32
        )

        self.remaining_space = None
        
    def reset(self, seed=None, options=None):
        super().reset(seed=seed)

        # Reset remaining space to the full width of the 2D space
        self.remaining_space = self.width
        return np.array([self.remaining_space], dtype=np.int32), {}
    
    def step(self, action):
        # Compute the space used by the selected number of components
        used_space = action * self.component_width

        if used_space > self.width:
            reward = -10  # Penalty for invalid action
            terminated = True
        else:
            # Calculate reward as the space utilisation ratio
            remaining_space = self.width - used_space
            non_standard_component = remaining_space  # Residual space
            reward = (used_space / self.width) * 10  # Scale reward

            self.remaining_space = remaining_space
            terminated = remaining_space == 0  # Done when fully utilised
        
        truncated = False
        return np.array([self.remaining_space], dtype=np.int32), reward, terminated, truncated, {}
    
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

    # Train the model
    model = PPO("MlpPolicy", env, verbose=1, device="cpu")
    model.learn(total_timesteps=100000)

    # Save the trained model
    model.save("space_optimiser")

    # Load and evaluate the model
    model = PPO.load("space_optimiser", device="cpu")
    obs = env.reset()
    for _ in range(10):
        action, _ = model.predict(obs)
        obs, reward, terminated, truncated = env.step(action)
        if any(terminated) or any(truncated):
            break

    # Optimal number of standard-sized components
    optimal_components = (width - obs[0][0]) // component_width
    print(f"Optimal number of standard components: {optimal_components}")
    print(f"Remaining non-standard space: {obs[0][0]}")
