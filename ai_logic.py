import random

import numpy as np
import torch


class AIDecisionMaker:
    def __init__(self, model=None):
        """
        Initialize the AI decision-maker.
        :param model: A trained reinforcement learning model (optional).
        """
        self.model = model

    def calculate_win_probability(self, hole_cards, community_cards):
        """
        Simulates the AI's win probability based on hole and community cards.
        """
        # Placeholder: Replace with a more advanced calculation or simulation
        return random.uniform(0, 1)

    def decide_action(self, hole_cards, community_cards, pot_odds, current_state=None):
        """
        Makes a decision (fold, call, raise) using the RL model or simple heuristics.
        :param hole_cards: The AI's hole cards.
        :param community_cards: The community cards on the table.
        :param pot_odds: The current pot odds.
        :param current_state: Encoded state representation for the RL model (optional).
        :return: The chosen action ('fold', 'call', 'raise').
        """
        # If the RL model is available and a state is provided
        if self.model and current_state is not None:
            action_probs = self.model.predict(current_state)
            action = torch.argmax(action_probs).item()  # Choose the action with the highest probability
            return ["fold", "call", "raise"][action]

        # Fall back to heuristic-based decision-making
        win_prob = self.calculate_win_probability(hole_cards, community_cards)
        if win_prob > 0.8:
            return "raise"
        elif win_prob > pot_odds:
            return "call"
        else:
            return "fold"

    def learn_from_game(self, experience, reward, optimizer):
        """
        Updates the model based on game results.
        :param experience: State, action, and next state from the game.
        :param reward: Reward signal from the outcome of the game.
        :param optimizer: Optimizer for updating the model.
        """
        if self.model is None:
            raise ValueError("No model available for learning.")

        # Example: Simple Q-Learning update
        state, action, next_state = experience
        current_q_values = self.model(state)
        max_next_q = np.max(self.model(next_state))
        target = current_q_values.clone()
        target[action] = reward + 0.99 * max_next_q

        # Backpropagate the loss
        loss_fn = torch.nn.MSELoss()
        loss = loss_fn(current_q_values, target)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
