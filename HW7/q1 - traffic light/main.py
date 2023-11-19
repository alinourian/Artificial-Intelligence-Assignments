import gym
import gym_cityflow
import numpy as np
import matplotlib.pyplot as plt


EPISODES = 200

actions = [
    [],
    [1, 5],
    [3, 7],
    [0, 3],
    [2, 6],
    [0, 1],
    [5, 4],
    [3, 2],
    [6, 7]
]

cars_per_turn = 1
def f(i, obs, action):
    return -max(0, obs[i] - (i in actions[action]) * cars_per_turn)


if __name__ == "__main__":
    env = gym.make('gym_cityflow:CityFlow-1x1-LowTraffic-v0')

    epsilon = .5  # Exploration rate.
    alpha = 0.2

    action_size = 9
    w = np.zeros(8)
    rewards = []

    for _ in range(EPISODES):
        epsilon = max(.1, epsilon * .95)
        obs = env.reset()
        done = False
        total_reward = 0
        turns = 0
        while not done:
            if np.random.uniform() < epsilon:
                action = np.random.randint(0, action_size)
            else:
                m = -100000
                action = 0
                for ac in range(0, action_size):
                    q = 0
                    for i in range(8):
                        q += w[i] * f(i, obs, ac)
                    if q > m:
                        m = q
                        action = ac

            last_f = [f(i, obs, action) for i in range(8)]
            pred_q = [w[i] * f(i, obs, action) for i in range(8)]
            obs, reward, done, info = env.step(action)
            diff = sum(pred_q) - reward
            for i in range(8):
                w[i] -= alpha * diff * last_f[i] / (abs(sum(pred_q)) or 1)

            total_reward += reward
            turns += 1
        rewards.append(total_reward)



