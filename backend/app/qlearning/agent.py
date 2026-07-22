
"""
Q-Learning Agent for Adaptive Inventory Management
State  = (inventory_bucket, demand_bucket, season_idx, disease_idx)
Action = reorder quantity (discrete levels)
"""
import numpy as np
import random
from typing import List, Tuple, Dict

class InventoryEnv:
    """Simulates the supply-chain environment for one medicine category in one district."""

    ACTIONS = [0, 50, 100, 150, 200, 300, 400, 500]   # reorder quantities

    def __init__(self, demand: List[float], forecast: List[float],
                 season_idx: List[int], disease_idx: List[int], opts: Dict):
        self.demand      = demand
        self.forecast    = forecast
        self.season_idx  = season_idx
        self.disease_idx = disease_idx
        self.n           = len(demand)

        self.max_demand    = max(demand) if demand else 500
        self.max_inventory = int(self.max_demand * 1.5 / 50) * 50 + 50

        self.inv_bucket_size  = max(25, self.max_inventory // 10)
        self.dem_bucket_size  = max(25, int(self.max_demand) // 10)
        self.n_inv_buckets    = self.max_inventory // self.inv_bucket_size + 1
        self.n_dem_buckets    = int(self.max_demand) // self.dem_bucket_size + 1
        self.n_seasons        = 6   # Winter Spring Summer Monsoon Post-Monsoon Autumn
        self.n_diseases       = 18

        self.holding_cost  = opts.get("holding", 2.0)
        self.shortage_cost = opts.get("shortage", 15.0)
        self.order_cost    = opts.get("order", 0.5)
        self.setup_cost    = opts.get("setup", 50.0)

        self.init_inventory = int(self.max_demand * 0.6 / 50) * 50
        self.reset()

    def _inv_bucket(self, inv):
        return min(self.n_inv_buckets - 1, int(max(0, inv) / self.inv_bucket_size))

    def _dem_bucket(self, dem):
        return min(self.n_dem_buckets - 1, int(max(0, dem) / self.dem_bucket_size))

    def _state(self):
        ib = self._inv_bucket(self.inventory)
        db = self._dem_bucket(self.forecast[self.t])
        si = self.season_idx[self.t]
        di = self.disease_idx[self.t]
        return (ib, db, si, di)

    def state_size(self):
        return (self.n_inv_buckets, self.n_dem_buckets, self.n_seasons, self.n_diseases)

    def reset(self):
        self.t         = 0
        self.inventory = self.init_inventory
        return self._state()

    def step(self, action_idx: int):
        order    = self.ACTIONS[min(action_idx, len(self.ACTIONS) - 1)]
        demand   = self.demand[self.t]
        stock    = min(self.max_inventory, self.inventory + order)
        stockout = max(0, demand - stock)
        leftover = max(0, stock - demand)
        sales    = min(stock, demand)

        hold_cost    = leftover * self.holding_cost
        short_cost   = stockout * self.shortage_cost
        order_cost   = order * self.order_cost + (self.setup_cost if order > 0 else 0)
        reward       = -(hold_cost + short_cost + order_cost)

        self.inventory = leftover
        self.t        += 1
        done           = self.t >= self.n - 1

        return {
            "next_state": None if done else self._state(),
            "reward": reward, "done": done,
            "stockout": stockout, "leftover": leftover,
            "order": order, "demand": demand, "sales": sales,
        }


class QLearningAgent:
    """Tabular Q-Learning agent."""

    def __init__(self, state_size: Tuple, n_actions: int,
                 alpha=0.1, gamma=0.95, epsilon=1.0,
                 epsilon_min=0.05, epsilon_decay=0.995):
        self.q_table      = np.zeros((*state_size, n_actions))
        self.n_actions    = n_actions
        self.alpha        = alpha
        self.gamma        = gamma
        self.epsilon      = epsilon
        self.epsilon_min  = epsilon_min
        self.epsilon_decay= epsilon_decay

    def choose_action(self, state: Tuple) -> int:
        if random.random() < self.epsilon:
            return random.randint(0, self.n_actions - 1)
        return int(np.argmax(self.q_table[state]))

    def learn(self, state, action, reward, next_state, done):
        current_q = self.q_table[state][action]
        if done or next_state is None:
            target_q = reward
        else:
            target_q = reward + self.gamma * np.max(self.q_table[next_state])
        self.q_table[state][action] += self.alpha * (target_q - current_q)

    def decay_epsilon(self):
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

    def best_action(self, state: Tuple) -> int:
        return int(np.argmax(self.q_table[state]))

    def get_q_table_dict(self) -> Dict:
        return self.q_table.tolist()

    def load_q_table(self, q_table_list):
        self.q_table = np.array(q_table_list)


def train_agent(demand, forecast, season_idx, disease_idx,
                episodes=500, opts=None, callbacks=None) -> Dict:
    """Train Q-learning agent and return results."""
    if opts is None:
        opts = {}

    env   = InventoryEnv(demand, forecast, season_idx, disease_idx, opts)
    agent = QLearningAgent(
        state_size=env.state_size(),
        n_actions=len(InventoryEnv.ACTIONS),
        alpha=opts.get("alpha", 0.1),
        gamma=opts.get("gamma", 0.95),
        epsilon=1.0,
        epsilon_min=0.05,
        epsilon_decay=0.995,
    )

    rewards_per_episode = []
    for ep in range(episodes):
        state      = env.reset()
        total_rew  = 0.0
        done       = False
        while not done:
            action = agent.choose_action(state)
            result = env.step(action)
            agent.learn(state, action, result["reward"], result["next_state"], result["done"])
            state     = result["next_state"] if not result["done"] else state
            total_rew += result["reward"]
            done       = result["done"]
        agent.decay_epsilon()
        rewards_per_episode.append(total_rew)

    # Evaluation run (no exploration)
    agent.epsilon = 0.0
    state    = env.reset()
    done     = False
    orders, stockouts, leftover_hist, sales_hist = [], [], [], []
    while not done:
        action = agent.best_action(state)
        result = env.step(action)
        orders.append(result["order"])
        stockouts.append(result["stockout"])
        leftover_hist.append(result["leftover"])
        sales_hist.append(result["sales"])
        state = result["next_state"] if not result["done"] else state
        done  = result["done"]

    return {
        "q_table":          agent.get_q_table_dict(),
        "rewards_per_episode": rewards_per_episode,
        "eval_orders":      orders,
        "eval_stockouts":   stockouts,
        "eval_leftover":    leftover_hist,
        "eval_sales":       sales_hist,
        "total_reward":     sum(rewards_per_episode),
        "service_level":    1 - (sum(s > 0 for s in stockouts) / max(len(stockouts), 1)),
        "avg_order":        sum(orders) / max(len(orders), 1),
    }
