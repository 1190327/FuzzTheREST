import random
import time

import numpy as np
from matplotlib import pyplot as plt
import matplotlib.patches as mpatches
from FuzzAlgorithm.environment import APIFuzzyTestingEnvironment


class QLearningAgent:
    def __init__(self, env: APIFuzzyTestingEnvironment, mutation_methods, max_steps_per_episode, learning_rate=0.1,
                 discount_factor=0.9, temperature=1.0, min_temperature=0.1, temperature_decay=0.99):
        self.env = env
        self.int_q_table = np.zeros([env.observation_space.n, len(mutation_methods[0])])
        self.float_q_table = np.zeros([env.observation_space.n, len(mutation_methods[1])])
        self.bool_q_table = np.zeros([env.observation_space.n, len(mutation_methods[2])])
        self.byte_q_table = np.zeros([env.observation_space.n, len(mutation_methods[3])])
        self.string_q_table = np.zeros([env.observation_space.n, len(mutation_methods[4])])
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.temperature = temperature
        self.min_temperature = min_temperature
        self.temperature_decay = temperature_decay
        self.max_steps_per_episode = max_steps_per_episode
        self.episode_durations = []  # To store the duration of each episode
        self.episode_rewards = []  # To store the rewards obtained in each episode
        self.rewards_all_episodes = []
        self.mutation_methods = mutation_methods
        self.mutation_counts = {i: {method: 0 for method in mutation_methods[i]} for i in range(env.observation_space.n)}
        self.mutation_rewards = {i: {method: [] for method in mutation_methods[i]} for i in range(env.observation_space.n)}
        self.state_visits = np.zeros(env.observation_space.n)
        self.q_value_convergence = {}
        self.num_episodes = 30

    def choose_action(self, state):
        q_values = [
            self.int_q_table[state, :],
            self.float_q_table[state, :],
            self.bool_q_table[state, :],
            self.byte_q_table[state, :],
            self.string_q_table[state, :]
        ]
        action = []
        for q_table in q_values:
            exp_q = np.exp(q_table / self.temperature)
            probabilities = exp_q / np.sum(exp_q)
            action.append(np.random.choice(len(q_table), p=probabilities))
        return action

    def update_q_table(self, state, action, reward, new_state, q_table):
        q_table[state, action] = q_table[state, action] * (1 - self.learning_rate) + \
                                 self.learning_rate * (reward + self.discount_factor * np.max(q_table[new_state, :]))

    def train(self, num_episodes, request_logs, crashes, hangs):
        self.q_value_convergence = {
            'int': [],
            'float': [],
            'bool': [],
            'byte': [],
            'string': []
        }

        self.num_episodes = num_episodes

        for episode in range(num_episodes):
            done = False
            state = self.env.reset()
            rewards_current_episode = 0
            start_time = time.time()

            print(episode)

            for step in range(self.max_steps_per_episode):
                action = self.choose_action(state)
                new_state, reward, done = self.env.step(action, request_logs, crashes, hangs)

                self.update_q_table(state, action[0], reward, new_state, self.int_q_table)
                self.update_q_table(state, action[1], reward, new_state, self.float_q_table)
                self.update_q_table(state, action[2], reward, new_state, self.bool_q_table)
                self.update_q_table(state, action[3], reward, new_state, self.byte_q_table)
                self.update_q_table(state, action[4], reward, new_state, self.string_q_table)

                for i in range(len(self.mutation_counts)):
                    chosen_method = self.mutation_methods[i][action[i]]
                    self.mutation_counts[i][chosen_method] += 1
                    self.mutation_rewards[i][chosen_method].append(reward)

                state = new_state
                rewards_current_episode += reward
                self.episode_rewards.append(reward)
                self.state_visits[state] += 1

                if done is True:
                    break

            end_time = time.time()
            self.episode_durations.append(end_time - start_time)
            # Temperature decay
            self.temperature = max(self.min_temperature, self.temperature * self.temperature_decay)

            self.rewards_all_episodes.append(rewards_current_episode)

            self.q_value_convergence['int'].append(np.copy(self.int_q_table))
            self.q_value_convergence['float'].append(np.copy(self.float_q_table))
            self.q_value_convergence['bool'].append(np.copy(self.bool_q_table))
            self.q_value_convergence['byte'].append(np.copy(self.byte_q_table))
            self.q_value_convergence['string'].append(np.copy(self.string_q_table))

        # Calculate and print the average reward per hundred episodes
        rewards_per_number_episodes = np.split(np.array(self.rewards_all_episodes), num_episodes / num_episodes)
        count = num_episodes
        print("********Average reward per number of episodes********\n")
        for r in rewards_per_number_episodes:
            print(count, ": ", str(sum(r / num_episodes)))
            count += num_episodes

    def plot_q_value_convergence(self, base_path):
        x = np.arange(0, self.num_episodes)
        data_types = ['int', 'float', 'bool', 'byte', 'string']
        for data_type in data_types:
            q_values = np.array(self.q_value_convergence[data_type])
            avg_q_values = np.mean(q_values, axis=(1, 2))  # Average over states and actions
            plt.plot(x, avg_q_values, label=data_type)

        plt.xlabel('Episodes')
        plt.ylabel('Average Q-value')
        plt.legend()
        plt.title('Q-value Convergence')
        plt.savefig(base_path + "q_value_convergence.png")
        plt.close()

    def plot_learning_curve(self, num_episodes):
        # Calculate the average reward over a fixed number of episodes (e.g., last 100 episodes) and plot the learning curve
        window_size = 10
        average_rewards = [np.mean(self.episode_rewards[i:i + window_size]) for i in
                           range(len(self.episode_rewards) - window_size + 1)]
        plt.plot(range(window_size, num_episodes + 1), average_rewards)
        plt.xlabel('Episodes')
        plt.ylabel('Average Reward')
        plt.title('Learning Curve')
        plt.show()

    def plot_cumulative_rewards(self, base_path):
        # Plot cumulative rewards for all episodes
        plt.plot(range(1, len(self.rewards_all_episodes) + 1), self.rewards_all_episodes, label='Cumulative Reward')

        # Calculate and display the average cumulative reward
        avg_cumulative_reward = np.mean(self.rewards_all_episodes)
        plt.axhline(y=avg_cumulative_reward, color='r', linestyle='--', label=f'Average Reward: {avg_cumulative_reward:.2f}')

        plt.xlabel('Episodes')
        plt.ylabel('Cumulative Reward')
        plt.title('Cumulative Reward per Episode')
        plt.legend()
        plt.savefig(base_path + "cumulative_rewards.png")
        plt.close()

    def plot_action_distribution(self, base_path):
        data_types = ['int', 'float', 'bool', 'byte', 'string']
        for i in range(len(self.mutation_counts)):
            mutation_methods = list(self.mutation_counts[i].keys())
            method_counts = list(self.mutation_counts[i].values())

            indices = np.arange(len(mutation_methods))

            # Define a list of colors for the columns
            colors = plt.cm.viridis(np.linspace(0, 1, len(mutation_methods)))

            # Use the 'colors' list to set different colors for each column
            bars = plt.bar(indices, method_counts, color=colors)

            plt.xticks(indices, indices)
            plt.xlabel('Mutation Method Index')
            plt.ylabel('Action Counts')
            plt.title(f'Action Distribution for {data_types[i]}')

            # Create custom legend handles for each mutation method
            legend_handles = [mpatches.Patch(color=colors[j], label=mutation_method.__name__) for j, mutation_method in
                              enumerate(mutation_methods)]

            # Move the legend outside the plot
            plt.legend(handles=legend_handles, loc='upper left', bbox_to_anchor=(1, 1))

            # Annotate each bar with the exact number on top
            for j, count in enumerate(method_counts):
                plt.text(j, count + 0.1, str(count), ha='center', va='bottom')

            plt.savefig(base_path + "q_action_distribution_" + str(i) + ".png", bbox_inches='tight')
            plt.close()

    def plot_exploration_exploitation_ratio(self, base_path):
        # Calculate exploration and exploitation rates based on temperature
        exploration_rates = [self.temperature * (self.temperature_decay ** episode) for episode in range(self.num_episodes)]
        normalized_exploration_rates = [rate / max(exploration_rates) for rate in exploration_rates]
        exploitation_rates = [1 - rate for rate in normalized_exploration_rates]

        # Plot the exploration and exploitation rates
        plt.plot(range(self.num_episodes), normalized_exploration_rates, label='Exploration Rate', color='blue')
        plt.plot(range(self.num_episodes), exploitation_rates, label='Exploitation Rate', color='orange')

        plt.xlabel('Episodes')
        plt.ylabel('Rate')
        plt.title('Exploration vs. Exploitation Ratio (Boltzmann Algorithm)')
        plt.legend()
        plt.savefig(base_path + "exploration_exploitation_ratio_boltzmann.png")
        plt.close()

    def plot_state_visits(self, base_path):
        states = list(range(len(self.state_visits)))
        visit_counts = list(self.state_visits)

        # Define legend labels for HTTP status code ranges
        legend_labels = ['1XX', '2XX', '3XX', '4XX', '5XX']

        # Define colors for each HTTP status code range
        colors = ['lightblue', 'green', 'yellow', 'orange', 'red']

        plt.bar(states, visit_counts, color=colors)
        plt.xlabel('HTTP Status Code Ranges')
        plt.ylabel('Number of Visits')
        plt.title('Number of Visits to Each HTTP Status Code Range')

        # Set x-axis ticks and labels to the legend labels
        plt.xticks(states, legend_labels)

        # Annotate each bar with the exact number on top
        for state, count in zip(states, visit_counts):
            plt.text(state, count + 0.1, str(count), ha='center', va='bottom')

        plt.savefig(base_path + "state_visits.png", bbox_inches='tight')
        plt.close()

    def test(self, request_logs, crashes, hangs):
        for episode in range(5):
            state = self.env.reset()
            done = False

            print("*******Episode ", episode + 1, "*******\n\n")
            for step in range(self.max_steps_per_episode):
                # Choose action with highest Q-value for current state
                self.env.render()
                # Take new action
                # time.sleep(0.3)
                action = []
                action.append(np.argmax(self.int_q_table[state, :]))
                action.append(np.argmax(self.float_q_table[state, :]))
                action.append(np.argmax(self.bool_q_table[state, :]))
                action.append(np.argmax(self.byte_q_table[state, :]))
                action.append(np.argmax(self.string_q_table[state, :]))
                new_state, reward, done = self.env.step(action, request_logs, crashes, hangs)

                if done:
                    self.env.render()
                    if reward == 1:
                        # Agent reached the goal and won episode
                        print("****You reached the goal****")
                        # time.sleep(3)
                    break
                else:
                    print("****You lost****")
                    # time.sleep(3)

                state = new_state


def write_agent_report(agent, name):
    q_tables_serializable = {
        "int_q_table": agent.int_q_table.tolist() if isinstance(agent.int_q_table,
                                                                np.ndarray) else agent.int_q_table,
        "float_q_table": agent.float_q_table.tolist() if isinstance(agent.float_q_table,
                                                                    np.ndarray) else agent.float_q_table,
        "bool_q_table": agent.bool_q_table.tolist() if isinstance(agent.bool_q_table,
                                                                  np.ndarray) else agent.bool_q_table,
        "byte_q_table": agent.byte_q_table.tolist() if isinstance(agent.byte_q_table,
                                                                  np.ndarray) else agent.byte_q_table,
        "string_q_table": agent.string_q_table.tolist() if isinstance(agent.string_q_table,
                                                                      np.ndarray) else agent.string_q_table,
    }

    mutation_counts_serializable = {
        str(key): {func.__name__: value for func, value in inner_dict.items()}
        for key, inner_dict in agent.mutation_counts.items()
    }

    mutation_rewards_serializable = {
        str(key): {func.__name__: value for func, value in inner_dict.items()}
        for key, inner_dict in agent.mutation_rewards.items()
    }

    q_value_convergence_serializable = {
        "int": [q.tolist() for q in agent.q_value_convergence['int']],
        "float": [q.tolist() for q in agent.q_value_convergence['float']],
        "bool": [q.tolist() for q in agent.q_value_convergence['bool']],
        "byte": [q.tolist() for q in agent.q_value_convergence['byte']],
        "string": [q.tolist() for q in agent.q_value_convergence['string']],
    }

    exploration_rates = [agent.temperature * (agent.temperature_decay ** episode) for episode in range(agent.num_episodes)]
    normalized_exploration_rates = [rate / max(exploration_rates) for rate in exploration_rates]
    exploitation_rates = [1 - rate for rate in normalized_exploration_rates]

    report = {
        "name": name,
        "q_tables": q_tables_serializable,
        "episode_rewards": agent.episode_rewards,
        "state_visits": agent.state_visits.tolist(),
        "mutation_counts": mutation_counts_serializable,
        "mutation_rewards": mutation_rewards_serializable,
        "q_value_convergence": q_value_convergence_serializable,
        "episode_durations": agent.episode_durations,
        "exploration_rates": exploration_rates,
        "exploitation_rates": exploitation_rates,
        "rewards_all_episodes": agent.rewards_all_episodes
    }

    return report
