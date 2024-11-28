import itertools
import logging
from collections import Counter
from game_mechanics import Card

# Hand rankings based on Texas Hold'em rules
HAND_RANKS = {
    "High Card": 1,
    "One Pair": 2,
    "Two Pair": 3,
    "Three of a Kind": 4,
    "Straight": 5,
    "Flush": 6,
    "Full House": 7,
    "Four of a Kind": 8,
    "Straight Flush": 9,
    "Royal Flush": 10
}


def calculate_hand_strength(hand, community_cards):
    """
    Calculates the strength of a player's hand by combining their hole cards with the community cards.
    :param hand: List of 2 Card objects (player's hole cards)
    :param community_cards: List of up to 5 Card objects (community cards)
    :return: A tuple (rank_value, best_hand), where rank_value is the rank of the hand,
             and best_hand is the list of cards representing the strongest hand.
    """
    all_cards = hand + community_cards
    if len(all_cards) < 5:
        raise ValueError("Insufficient cards to evaluate hand strength.")

    best_rank = ("High Card", [])
    for combo in itertools.combinations(all_cards, 5):
        rank = evaluate_hand(combo)
        if HAND_RANKS[rank[0]] > HAND_RANKS[best_rank[0]]:
            best_rank = rank
    return HAND_RANKS[best_rank[0]], best_rank[1]


def evaluate_hand(cards):
    """
    Evaluates a single hand (5 cards) to determine its rank.
    Handles tie-breaking by returning the sorted hand for comparison.
    :param cards: List of 5 Card objects
    :return: A tuple (rank_name, sorted_hand, rank_value), where rank_name is the hand rank,
             sorted_hand is the best card sequence, and rank_value is a tuple for tie-breaking.
    """
    suits = [card.suit for card in cards]
    ranks = [card.rank for card in cards]
    rank_counts = Counter(ranks)
    sorted_cards = sorted(cards, key=lambda x: Card.RANKS.index(x.rank), reverse=True)

    # Check for flush
    is_flush = len(set(suits)) == 1

    # Check for straight
    rank_indices = [Card.RANKS.index(rank) for rank in ranks]
    rank_indices.sort()
    is_straight = all(rank_indices[i] - rank_indices[i - 1] == 1 for i in range(1, len(rank_indices)))

    # Check combinations and determine rank value
    if is_flush and is_straight and sorted_cards[0].rank == "Ace":
        return "Royal Flush", sorted_cards, (10,)
    elif is_flush and is_straight:
        return "Straight Flush", sorted_cards, (9, max(rank_indices))
    elif 4 in rank_counts.values():
        four_of_a_kind = [rank for rank, count in rank_counts.items() if count == 4][0]
        kicker = [rank for rank in ranks if rank != four_of_a_kind][0]
        return "Four of a Kind", sorted_cards, (8, Card.RANKS.index(four_of_a_kind), Card.RANKS.index(kicker))
    elif 3 in rank_counts.values() and 2 in rank_counts.values():
        three_of_a_kind = [rank for rank, count in rank_counts.items() if count == 3][0]
        pair = [rank for rank, count in rank_counts.items() if count == 2][0]
        return "Full House", sorted_cards, (7, Card.RANKS.index(three_of_a_kind), Card.RANKS.index(pair))
    elif is_flush:
        return "Flush", sorted_cards, tuple(Card.RANKS.index(card.rank) for card in sorted_cards)
    elif is_straight:
        return "Straight", sorted_cards, (5, max(rank_indices))
    elif 3 in rank_counts.values():
        three_of_a_kind = [rank for rank, count in rank_counts.items() if count == 3][0]
        kickers = [rank for rank in ranks if rank != three_of_a_kind]
        kickers.sort(key=lambda x: Card.RANKS.index(x), reverse=True)
        return "Three of a Kind", sorted_cards, (4, Card.RANKS.index(three_of_a_kind)) + tuple(
            Card.RANKS.index(k) for k in kickers)
    elif list(rank_counts.values()).count(2) == 2:
        pairs = [rank for rank, count in rank_counts.items() if count == 2]
        pairs.sort(key=lambda x: Card.RANKS.index(x), reverse=True)
        kicker = [rank for rank in ranks if rank not in pairs][0]
        return "Two Pair", sorted_cards, (3,) + tuple(Card.RANKS.index(p) for p in pairs) + (Card.RANKS.index(kicker),)
    elif 2 in rank_counts.values():
        pair = [rank for rank, count in rank_counts.items() if count == 2][0]
        kickers = [rank for rank in ranks if rank != pair]
        kickers.sort(key=lambda x: Card.RANKS.index(x), reverse=True)
        return "One Pair", sorted_cards, (2, Card.RANKS.index(pair)) + tuple(Card.RANKS.index(k) for k in kickers)
    else:
        return "High Card", sorted_cards, tuple(Card.RANKS.index(card.rank) for card in sorted_cards)


def log_game_state(state, filename="game_log.txt"):
    """
    Logs the current state of the game to a file.
    :param state: Dictionary containing game state information (e.g., player chips, pot size, community cards).
    :param filename: The file to log the state to.
    """
    logging.basicConfig(filename=filename, level=logging.INFO, format='%(asctime)s - %(message)s')
    logging.info(f"Game State: {state}")


def calculate_pot_odds(player_bet, pot_size, call_amount):
    """
    Calculates the pot odds for a player.
    :param player_bet: Current bet placed by the player.
    :param pot_size: Total pot size.
    :param call_amount: Amount required to call the current bet.
    :return: Pot odds as a float (e.g., 0.25 for 25%).
    """
    total_investment = player_bet + call_amount
    return total_investment / (pot_size + total_investment)


def generate_deck_visual(deck):
    """
    Generates a visual representation of the current deck (for debugging purposes).
    :param deck: List of Card objects.
    :return: A string representation of the deck.
    """
    return ", ".join(str(card) for card in deck)
