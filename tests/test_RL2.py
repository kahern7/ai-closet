import gymnasium as gym
from gymnasium import spaces
import numpy as np
from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.callbacks import BaseCallback
import matplotlib.pyplot as plt

class ClosetEnv(gym.Env):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.columns = config["columns"]
        self.components = config["components"]
        self.height = config["height"]
        self.min_heights = config["min_heights"]
        self.preferences = config["preferences"]
        self.state = None

        # Action space: (column, component, action type)
        self.action_space = spaces.MultiDiscrete([
            self.columns, len(self.components), 2  # 2 actions: increase, decrease
        ])

        # Observation space: closet state as a vector
        self.observation_space = spaces.Box(
            low=0,
            high=self.height,
            shape=(self.columns * len(self.components),),
            dtype=np.int32,
        )

    def reset(self, seed=None, options=None):
        # Seed the environment if seed is provided
        super().reset(seed=seed)

        # Initial state: empty closet
        self.state = np.zeros(self.columns * len(self.components), dtype=np.int32)
        return self.state, {}

    def step(self, action):
        column, component, action_type = action
        index = column * len(self.components) + component

        # Apply action
        if action_type == 0:  # increase
            self.state[index] += self.min_heights[self.components[component]]
        elif action_type == 1:  # decrease
            self.state[index] = max(0, self.state[index] - self.min_heights[self.components[component]])

        # Compute reward
        reward = self.compute_penalty(self.state)

        # Check if done (e.g., after fixed steps or valid solution)
        terminated = reward >= 0  # TODO: Adjust termination condition as needed
        truncated = False  # No explicit truncation condition in this implementation

        return self.state, reward, terminated, truncated, {}

    def compute_penalty(self, state):
        reward = 0
        
        # Reward for utilising space efficiently
        used_space = sum(state)  # Total height allocated to components
        total_space = self.columns * self.height
        utilisation_ratio = used_space / total_space
        if utilisation_ratio > 1:
            reward -= 50
            # reward += utilisation_ratio * 20  # Scale up to emphasise this reward

        # Penalty for unused space
        reward -= (1 - utilisation_ratio) * 5

        # Penalty for exceeding constraints
        if any(h > self.height for h in state):
            reward -= 20

        return reward

    def con_comp_percent_diff(self, state):
        penalty = 0
        component_allocation = {
            component: sum(state[i::len(self.components)])
            for i, component in enumerate(self.components)
        }

        for component, target_percentage in self.preferences.items():
            allocated_percentage = (component_allocation[component] / (self.columns * self.height)) * 100
            penalty += abs(allocated_percentage - target_percentage)

        return penalty

    def con_exceed_total_space(self, state):
        total_space_used = sum(state)
        unused_space = (self.height * self.columns) - total_space_used
        if unused_space < 0: # if exceeds total space available
            return 100
        return (unused_space * 100) / (self.height * self.columns)

    def con_drawers(self, state):
        if "drawers" not in self.components:
            return 0

        penalty = 0
        drawer_heights = [state[i] for i in range(self.components.index("drawers"), len(state), len(self.components))]

        # Ensure drawers are centred
        total_drawer_height = sum(drawer_heights)
        max_drawer_height_per_column = self.height // self.min_heights["drawers"] * self.min_heights["drawers"]
        if total_drawer_height > self.columns * max_drawer_height_per_column:
            penalty += 100 + (total_drawer_height - self.columns * max_drawer_height_per_column)

        # Centre drawers in ideal columns
        drawer_columns = [i for i, height in enumerate(drawer_heights) if height > 0]
        if len(drawer_columns) > 0:
            mid = self.columns // 2
            ideal_positions = range(mid - len(drawer_columns) // 2, mid + (len(drawer_columns) + 1) // 2)
            for actual, ideal in zip(sorted(drawer_columns), ideal_positions):
                penalty += abs(actual - ideal) * 10

        return penalty

class RewardTrackingCallback(BaseCallback):
    def __init__(self, verbose=0):
        super().__init__(verbose)
        self.rewards = []
        self.step_counts = []

    def _on_step(self) -> bool:
        if len(self.locals["infos"]) > 0 and "episode" in self.locals["infos"][0]:
            # Log the reward at each step
            reward = self.locals["rewards"][0]  # Assuming a single environment
            self.rewards.append(reward)
            self.step_counts.append(len(self.rewards))  # Track the iteration count
        return True

    def _on_training_end(self) -> None:
        # Visualise rewards per iteration
        plt.figure(figsize=(10, 5))
        plt.plot(self.step_counts, self.rewards, label="Step Reward", alpha=0.7)
        plt.xlabel("Iteration")
        plt.ylabel("Reward")
        plt.title("Reward Progression During Training (Per Step)")
        plt.legend()
        plt.grid()
        plt.show()

if __name__ == "__main__":
    config = {
        "width": 4000,
        "height": 2176,
        "preferences": {"drawers": 50, "shelves": 50},
        "columns": 4,
        "components": ["drawers", "shelves"],
        "min_heights": {"drawers": (7 * 32), "shelves": 32},
    }

    def create_env():
        return ClosetEnv(config)

    env = make_vec_env(create_env, n_envs=1)

    reward_tracking_callback = RewardTrackingCallback()

    model = PPO("MlpPolicy", env, learning_rate=0.0003, verbose=1, device="cpu")
    model.learn(total_timesteps=100000, callback=reward_tracking_callback)

    model.save("closet_optimizer")

    model = PPO.load("closet_optimizer", device="cpu")
    obs = env.reset()
    for _ in range(1000):  # Allow enough steps for full optimisation
        action, _ = model.predict(obs)
        obs, reward, terminated, truncated = env.step(action)
        if any(terminated) or any(truncated):
            break
    print("Optimised Closet Configuration:\n", obs)
