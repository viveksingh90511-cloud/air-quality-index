"""
Air Quality Platform - Reinforcement Learning Smart Alert System
Q-Learning agent that adaptively optimizes alert thresholds over time.
"""

import numpy as np
import random
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class AQIEnvironment:
    """
    RL environment representing the air quality alerting task.
    States: discretized AQI buckets × trend direction
    Actions: [no_alert, advisory, warning, critical, emergency]
    Rewards: balanced between sensitivity (catch real events) and precision (avoid false alarms)
    """

    AQI_BUCKETS = [0, 50, 100, 150, 200, 300, 500]
    ACTIONS = ["no_alert", "advisory", "warning", "critical", "emergency"]
    N_STATES = (len(AQI_BUCKETS) - 1) * 3   # 6 AQI bands × 3 trend directions
    N_ACTIONS = len(ACTIONS)

    def __init__(self):
        self.current_aqi = 80.0
        self.trend = 0            # -1 decreasing, 0 stable, 1 increasing
        self.step_count = 0

    def _aqi_band(self, aqi: float) -> int:
        for i, threshold in enumerate(self.AQI_BUCKETS[1:]):
            if aqi <= threshold:
                return i
        return len(self.AQI_BUCKETS) - 2

    def state(self) -> int:
        band = self._aqi_band(self.current_aqi)
        trend_idx = self.trend + 1  # 0, 1, 2
        return band * 3 + trend_idx

    def _ideal_action(self) -> int:
        """Ground truth ideal action for reward shaping."""
        aqi = self.current_aqi
        if aqi <= 50:   return 0  # no_alert
        if aqi <= 100:  return 1  # advisory
        if aqi <= 150:  return 2  # warning
        if aqi <= 300:  return 3  # critical
        return 4                  # emergency

    def step(self, action: int):
        ideal = self._ideal_action()
        diff = abs(action - ideal)

        # Reward structure
        if diff == 0:
            reward = 10.0
        elif diff == 1:
            reward = 3.0 if action > ideal else -1.0   # over-alert slightly better than under
        elif diff == 2:
            reward = -5.0
        else:
            reward = -15.0  # severely wrong

        # Simulate next AQI
        prev_aqi = self.current_aqi
        noise = random.gauss(0, 8)
        hour = (self.step_count % 24)
        diurnal = 15 * np.sin(2 * np.pi * (hour - 8) / 24)
        self.current_aqi = max(5, min(500, self.current_aqi + noise + diurnal * 0.1))
        self.step_count += 1

        # Update trend
        delta = self.current_aqi - prev_aqi
        self.trend = 1 if delta > 5 else (-1 if delta < -5 else 0)

        done = self.step_count >= 168  # 1 week episode
        return self.state(), reward, done

    def reset(self) -> int:
        self.current_aqi = random.uniform(30, 200)
        self.trend = random.choice([-1, 0, 1])
        self.step_count = 0
        return self.state()


class QLearningAgent:
    """
    Tabular Q-Learning agent for adaptive alert threshold optimization.
    Learns from simulated AQI episodes to optimize alerting policy.
    """

    def __init__(self, n_states: int, n_actions: int):
        self.n_states = n_states
        self.n_actions = n_actions
        self.q_table = np.zeros((n_states, n_actions))

        # Hyperparameters
        self.learning_rate = 0.1
        self.discount_factor = 0.95
        self.epsilon = 1.0          # Exploration rate
        self.epsilon_min = 0.05
        self.epsilon_decay = 0.995
        self.episodes_trained = 0

    def choose_action(self, state: int, explore: bool = True) -> int:
        if explore and random.random() < self.epsilon:
            return random.randint(0, self.n_actions - 1)
        return int(np.argmax(self.q_table[state]))

    def learn(self, state: int, action: int, reward: float, next_state: int, done: bool):
        current_q = self.q_table[state, action]
        if done:
            target_q = reward
        else:
            target_q = reward + self.discount_factor * np.max(self.q_table[next_state])

        self.q_table[state, action] += self.learning_rate * (target_q - current_q)

    def decay_epsilon(self):
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

    def get_policy(self) -> dict:
        """Return learned policy as a readable dict."""
        env = AQIEnvironment()
        policy = {}
        aqi_bands = ["0-50", "51-100", "101-150", "151-200", "201-300", "301-500"]
        trends = ["decreasing", "stable", "increasing"]
        for band in range(6):
            for trend_idx, trend in enumerate(trends):
                state = band * 3 + trend_idx
                best_action = int(np.argmax(self.q_table[state]))
                key = f"AQI {aqi_bands[band]}, {trend}"
                policy[key] = {
                    "action": AQIEnvironment.ACTIONS[best_action],
                    "confidence": round(float(np.max(self.q_table[state])), 2),
                    "q_values": {a: round(float(self.q_table[state, i]), 2) for i, a in enumerate(AQIEnvironment.ACTIONS)},
                }
        return policy


class RLAlertSystem:
    """
    RL-powered adaptive alert threshold system.
    Trains a Q-learning agent and uses it to classify alert levels.
    """

    def __init__(self):
        self.env = AQIEnvironment()
        self.agent = QLearningAgent(AQIEnvironment.N_STATES, AQIEnvironment.N_ACTIONS)
        self.is_trained = False
        self.training_history = []

    def train(self, episodes: int = 500):
        """Train the Q-learning agent."""
        logger.info(f"Training RL alert agent for {episodes} episodes...")
        rewards_per_episode = []

        for ep in range(episodes):
            state = self.env.reset()
            total_reward = 0.0
            done = False

            while not done:
                action = self.agent.choose_action(state, explore=True)
                next_state, reward, done = self.env.step(action)
                self.agent.learn(state, action, reward, next_state, done)
                state = next_state
                total_reward += reward

            self.agent.decay_epsilon()
            rewards_per_episode.append(total_reward)

            if (ep + 1) % 100 == 0:
                avg = np.mean(rewards_per_episode[-100:])
                logger.info(f"  Episode {ep+1}/{episodes} | Avg Reward: {avg:.1f} | ε: {self.agent.epsilon:.3f}")

        self.agent.episodes_trained = episodes
        self.training_history = rewards_per_episode
        self.is_trained = True
        logger.info("RL agent training complete!")

    def classify_alert(self, aqi: float, trend: str = "stable") -> dict:
        """Classify alert level using learned RL policy."""
        trend_map = {"decreasing": -1, "stable": 0, "increasing": 1}
        self.env.current_aqi = aqi
        self.env.trend = trend_map.get(trend, 0)
        state = self.env.state()

        if self.is_trained:
            action = self.agent.choose_action(state, explore=False)
        else:
            # Rule-based fallback (pre-training)
            action = self._rule_based(aqi, trend)

        alert_level = AQIEnvironment.ACTIONS[action]
        q_values = {a: round(float(self.agent.q_table[state, i]), 2) for i, a in enumerate(AQIEnvironment.ACTIONS)}

        return {
            "aqi": aqi,
            "trend": trend,
            "alert_level": alert_level,
            "action_id": action,
            "q_values": q_values,
            "confidence": round(float(np.max(self.agent.q_table[state])), 2),
            "model": "rl_q_learning" if self.is_trained else "rule_based_fallback",
            "episodes_trained": self.agent.episodes_trained,
            "recommended_actions": self._get_recommended_actions(alert_level),
            "timestamp": datetime.now().isoformat(),
        }

    def _rule_based(self, aqi: float, trend: str) -> int:
        """Fallback rule-based policy."""
        if aqi <= 50:   return 0
        if aqi <= 100:  return 1
        if aqi <= 150:  return 2
        if aqi <= 300:  return 3
        return 4

    def _get_recommended_actions(self, alert_level: str) -> list:
        actions = {
            "no_alert": ["Continue normal operations", "Maintain monitoring"],
            "advisory": ["Issue public health advisory", "Alert sensitive groups"],
            "warning": ["Issue public warning", "Close schools/outdoor events", "Activate emergency response"],
            "critical": ["Evacuate high-risk populations", "Activate emergency response", "Notify hospitals"],
            "emergency": ["Issue emergency shutdown", "Activate disaster response", "Notify government authorities"],
        }
        return actions.get(alert_level, [])

    def get_policy_summary(self) -> dict:
        """Get the learned alerting policy."""
        return {
            "policy": self.agent.get_policy(),
            "training_summary": {
                "episodes": self.agent.episodes_trained,
                "final_epsilon": round(self.agent.epsilon, 4),
                "avg_reward_last_100": round(float(np.mean(self.training_history[-100:])), 2) if len(self.training_history) >= 100 else 0,
            },
            "is_trained": self.is_trained,
        }

    def quick_train(self):
        """Fast training for demo purposes (100 episodes)."""
        self.train(episodes=100)


# Singleton
rl_alert_system = RLAlertSystem()
# Quick-train in background on first import
try:
    rl_alert_system.quick_train()
except Exception as e:
    logger.warning(f"RL quick-train failed: {e}")
