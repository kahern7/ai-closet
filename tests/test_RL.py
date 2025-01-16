import numpy as np
import matplotlib.pyplot as plt
from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env
from gymnasium import Env
from gymnasium.spaces import Discrete, Box

class ClosetEnv(Env):
    def __init__(self, config):
        super(ClosetEnv, self).__init__()
        self.config = config
        self.columns = config["columns"]
        self.max_height = config["height"]
        self.components = config["components"]
        self.min_heights = config["min_heights"]
        self.preferences = config["preferences"]
        self.state = np.zeros(self.columns)
        self.done = False
        
        self.action_space = Discrete(self.columns)  # Select a column to add an item
        self.observation_space = Box(0, self.max_height, shape=(self.columns,), dtype=np.float32)

    def step(self, action):
        if not self.done:
            # Add an item to the selected column
            self.state[action] += 1

            # Check constraints
            if any(self.state > self.max_height):
                self.done = True  # End the episode if a column overflows

            # Calculate reward
            reward = self.calculate_reward(self.state, action, self.done)

            # Check if target configuration is met
            terminated = self.state_meets_target_configuration(self.state)
            truncated = self.done and not terminated

            return self.state, reward, terminated, truncated, {}

        return self.state, 0, True, False, {}

    def reset(self):
        self.state = np.zeros(self.columns)
        self.done = False
        return self.state

    def calculate_reward(self, state, action, done):
        reward = 0

        # Reward for utilising space efficiently
        used_space = sum(state)  # Total height allocated to components
        total_space = self.columns * self.max_height
        utilisation_ratio = used_space / total_space
        reward += utilisation_ratio * 10  # Scale up to emphasise this reward

        # Penalty for unused space
        reward -= (1 - utilisation_ratio) * 5

        # Penalty for exceeding constraints
        if any(h > self.max_height for h in state):
            reward -= 20

        # Additional rewards for specific objectives (customise based on goals)
        if done and self.state_meets_target_configuration(state):
            reward += 50  # Bonus for completing with the optimal layout

        return reward

    def state_meets_target_configuration(self, state):
        return sum(state) > (0.8 * self.columns * self.max_height)  # Example: at least 80% utilisation

# Debugging Enhancements
if __name__ == "__main__":
    
    # Configuration for the closet
    config = {
        "width": 4000,
        "height": 2176,
        "preferences": {"drawers": 50, "shelves": 50},
        "columns": 4,
        "components": ["drawers", "shelves"],
        "min_heights": {"drawers": (7*32), "shelves": 32},
    }
    
    env = ClosetEnv(config)
    rewards = []

    for episode in range(10):  # Simulate 10 episodes for debugging
        state = env.reset()
        total_reward = 0
        done = False
        while not done:
            action = env.action_space.sample()  # Replace with model's action if integrated
            next_state, reward, terminated, truncated, info = env.step(action)

            # Log reward
            print(f"State: {state}, Action: {action}, Reward: {reward}")

            total_reward += reward
            state = next_state
            done = terminated or truncated

        rewards.append(total_reward)
        print(f"Episode {episode + 1}: Total Reward = {total_reward}")

    # Plot reward progression
    plt.plot(rewards)
    plt.xlabel("Episode")
    plt.ylabel("Total Reward")
    plt.title("Reward Progression Over Episodes")
    plt.show()

    # Training using PPO
    model = PPO("MlpPolicy", env, verbose=1, device="cpu")
    model.learn(total_timesteps=10000)

    # Save model
    model.save("closet_ppo_model")