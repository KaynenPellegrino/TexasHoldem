import torch
from rl_model import PokerAIModel

# Generate models for AI1 to AI5
for i in range(5):
    model = PokerAIModel(input_size=10, action_size=3)  # Adjust input_size and action_size as needed
    torch.save(model.state_dict(), f"trained_model_{i+1}.pth")
print("Placeholder models generated successfully.")
