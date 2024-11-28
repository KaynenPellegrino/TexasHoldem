import torch
import torch.nn as nn


class PokerAIModel(nn.Module):
    def __init__(self, input_size, action_size):
        super(PokerAIModel, self).__init__()
        self.fc = nn.Sequential(
            nn.Linear(input_size, 128),
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, action_size)
        )

    def forward(self, x):
        return self.fc(x)

    def predict(self, state):
        """
        Predicts action probabilities based on the current state.
        :param state: Game state as a tensor.
        :return: Action probabilities.
        """
        return self.forward(torch.tensor(state, dtype=torch.float))

    def update(self, state, action, reward, next_state, optimizer, discount_factor=0.99):
        """
        Updates the model using the Q-learning algorithm.
        """
        state = torch.tensor(state, dtype=torch.float)
        next_state = torch.tensor(next_state, dtype=torch.float)
        q_values = self(state)
        max_next_q = self(next_state).max().item()
        target = q_values.clone()
        target[action] = reward + discount_factor * max_next_q

        loss_fn = nn.MSELoss()
        optimizer.zero_grad()
        loss = loss_fn(q_values, target)
        loss.backward()
        optimizer.step()
