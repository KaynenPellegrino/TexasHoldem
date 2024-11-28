from game_mechanics import Deck, Player
from ai_logic import AIDecisionMaker
from rl_model import PokerAIModel
from utils import calculate_hand_strength
import torch


def betting_round(players, ai_models, community_cards, pot_size, highest_bet, start_index):
    """
    Handles a betting round where all active players must act until the betting resolves.
    :param players: List of all players.
    :param ai_models: List of AI decision models.
    :param community_cards: Current community cards.
    :param pot_size: Current pot size.
    :param highest_bet: The highest bet placed in this round.
    :param start_index: Index of the player who acts first in this round.
    :return: Updated pot_size, highest_bet, and a boolean indicating if the hand is complete.
    """
    current_index = start_index
    while True:
        changes_made = False
        for _ in range(len(players)):
            player = players[current_index]
            if not player.active:
                current_index = (current_index + 1) % len(players)
                continue

            print(f"\nCurrent Pot: {pot_size}")
            print("Player Purses:")
            for p in players:
                print(f"{p.name}: {p.chips} chips")

            print(f"{player.name}'s turn to act.")

            if "AI" in player.name:
                # AI action
                ai = ai_models[current_index]
                win_prob = ai.calculate_win_probability(player.hand, community_cards)
                pot_odds = (highest_bet - player.current_bet) / max(1, pot_size)

                action = ai.decide_action(player.hand, community_cards, pot_odds)
                if action == "fold":
                    print(f"{player.name} (AI) chose to fold.")
                    player.active = False
                elif action == "call":
                    call_amount = min(highest_bet - player.current_bet, player.chips)
                    player.chips -= call_amount
                    player.current_bet += call_amount
                    pot_size += call_amount
                    print(f"{player.name} (AI) called.")
                elif action == "raise" and player.chips > highest_bet * 2:
                    raise_amount = min(highest_bet * 2, player.chips)
                    call_amount = highest_bet - player.current_bet
                    total_raise = call_amount + raise_amount
                    player.chips -= total_raise
                    player.current_bet += total_raise
                    highest_bet = player.current_bet
                    pot_size += total_raise
                    print(f"{player.name} (AI) raised to {highest_bet} chips.")
                    changes_made = True
            else:
                # Human action
                if player.current_bet < highest_bet:
                    while True:
                        action = input("Choose your action (fold, call, raise): ").strip().lower()
                        if action == "fold":
                            print(f"{player.name} chose to fold.")
                            player.active = False
                            break
                        elif action == "call":
                            call_amount = min(highest_bet - player.current_bet, player.chips)
                            player.chips -= call_amount
                            player.current_bet += call_amount
                            pot_size += call_amount
                            print(f"{player.name} chose to call.")
                            break
                        elif action == "raise" and player.chips > highest_bet * 2:
                            raise_amount = min(highest_bet * 2, player.chips)
                            call_amount = highest_bet - player.current_bet
                            total_raise = call_amount + raise_amount
                            player.chips -= total_raise
                            player.current_bet += total_raise
                            highest_bet = player.current_bet
                            pot_size += total_raise
                            print(f"{player.name} raised to {highest_bet} chips.")
                            changes_made = True
                            break
                        else:
                            print("Invalid action. Choose 'fold', 'call', or 'raise'.")
                else:
                    while True:
                        action = input("Choose your action (check, raise): ").strip().lower()
                        if action == "check":
                            print(f"{player.name} chose to check.")
                            break
                        elif action == "raise" and player.chips > highest_bet * 2:
                            raise_amount = min(highest_bet * 2, player.chips)
                            player.chips -= raise_amount
                            player.current_bet += raise_amount
                            highest_bet = player.current_bet
                            pot_size += raise_amount
                            print(f"{player.name} raised to {highest_bet} chips.")
                            changes_made = True
                            break
                        else:
                            print("Invalid action. Choose 'check' or 'raise'.")

            # Check if only one player remains
            active_players = [p for p in players if p.active]
            if len(active_players) == 1:
                winner = active_players[0]
                print(f"Winner: {winner.name} (last player standing).")
                winner.chips += pot_size
                return pot_size, highest_bet, True

            current_index = (current_index + 1) % len(players)

        # End betting round if no changes and bets are matched
        active_players = [p for p in players if p.active]
        if not changes_made and all(p.current_bet == highest_bet for p in active_players):
            break

    return pot_size, highest_bet, False


def main():
    # Initialize game components
    deck = Deck()
    players = [Player(f"AI{i + 1}") for i in range(5)] + [Player("Human")]
    dealer_index = 0  # Start with the first player as the dealer

    # Create individual AI models for each AI player
    ai_models = [AIDecisionMaker(PokerAIModel(input_size=10, action_size=3)) for _ in range(5)]

    # Load the pre-trained AI model into each AI
    for i, model in enumerate(ai_models):
        try:
            model.model.load_state_dict(torch.load(f"trained_model_{i + 1}.pth", weights_only=True))
        except FileNotFoundError:
            print(f"Trained model for AI{i + 1} not found. Ensure 'trained_model_{i + 1}.pth' is available.")
            return
        except Exception as e:
            print(f"Error loading model for AI{i + 1}: {e}")
            return

    # Main game flow
    while len(players) > 1:  # Ensure at least two players are in the game
        deck.reshuffle()
        community_cards = []
        pot_size = 0

        # Reset player states and deal cards
        for player in players:
            player.clear_hand()
            player.receive_cards(deck.deal(2))
            player.active = True
            player.current_bet = 0

        print("New Hand Begins!")
        for player in players:
            print(f"{player.name}'s Hand: {'[Hidden]' if 'AI' in player.name else player.show_hand()}")

        # Assign blinds
        small_blind_index = (dealer_index + 1) % len(players)
        big_blind_index = (dealer_index + 2) % len(players)
        small_blind, big_blind = players[small_blind_index], players[big_blind_index]

        small_blind_bet = 50
        big_blind_bet = 100
        small_blind.chips -= small_blind_bet
        big_blind.chips -= big_blind_bet
        small_blind.current_bet = small_blind_bet
        big_blind.current_bet = big_blind_bet
        pot_size = small_blind_bet + big_blind_bet

        print(f"{small_blind.name} posts the small blind: {small_blind_bet}")
        print(f"{big_blind.name} posts the big blind: {big_blind_bet}")

        highest_bet = big_blind_bet

        # Progress through the game phases
        for phase in ["Pre-Flop", "Flop", "Turn", "River"]:
            if phase == "Flop":
                community_cards.extend(deck.deal(3))
            elif phase in ["Turn", "River"]:
                community_cards.extend(deck.deal(1))

            print(f"\n--- {phase} Phase ---")
            print(f"Community Cards: {', '.join(str(card) for card in community_cards) if community_cards else 'None'}")
            print(f"Current Pot: {pot_size}")
            print("Player Purses:")
            for p in players:
                print(f"{p.name}: {p.chips} chips")

            # Run betting round
            start_index = (big_blind_index + 1) % len(players)
            pot_size, highest_bet, hand_complete = betting_round(
                players, ai_models, community_cards, pot_size, highest_bet, start_index
            )

            if hand_complete:
                break

        # Determine winner
        active_players = [p for p in players if p.active]
        if len(active_players) == 1:
            winner = active_players[0]
            print(f"Winner: {winner.name} (last player standing).")
            winner.chips += pot_size
        else:
            hand_strengths = [
                calculate_hand_strength(player.hand, community_cards) for player in active_players
            ]
            winner_index = max(range(len(hand_strengths)), key=lambda i: hand_strengths[i][0])
            winner = active_players[winner_index]
            print(f"Winner: {winner.name} (best hand).")
            winner.chips += pot_size

        # Remove players with no chips
        players = [p for p in players if p.chips > 0]

        # Rotate dealer
        dealer_index = (dealer_index + 1) % len(players)

        # Prompt to continue
        start_new = input("Start a new hand? (y/n): ").strip().lower()
        if start_new != 'y':
            print("Thanks for playing!")
            break


if __name__ == "__main__":
    main()
