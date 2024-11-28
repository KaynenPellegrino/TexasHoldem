import random


class Card:
    SUITS = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
    RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King', 'Ace']

    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit

    def __repr__(self):
        return f"{self.rank} of {self.suit}"


class Deck:
    def __init__(self):
        """
        Initializes a shuffled deck of 52 cards.
        """
        self.cards = [Card(rank, suit) for suit in Card.SUITS for rank in Card.RANKS]
        random.shuffle(self.cards)

    def deal(self, num):
        """
        Deals `num` cards from the deck.
        :param num: Number of cards to deal.
        :return: List of Card objects.
        """
        if num > len(self.cards):
            raise ValueError("Not enough cards left in the deck to deal.")
        return [self.cards.pop() for _ in range(num)]

    def reshuffle(self):
        """
        Reshuffles the deck, restoring it to its full 52 cards.
        """
        self.__init__()

    def __repr__(self):
        return f"Deck with {len(self.cards)} cards remaining."


class Player:
    def __init__(self, name, chips=1000):
        self.name = name
        self.chips = chips
        self.hand = []
        self.current_bet = 0
        self.active = True  # New attribute to track active status

    def fold(self):
        """
        Marks the player as folded and removes them from further actions in the hand.
        """
        self.active = False


    def bet(self, amount):
        """
        Places a bet, deducting chips from the player's total.
        :param amount: Amount to bet.
        :return: The bet amount.
        """
        if amount > self.chips:
            raise ValueError(f"{self.name} does not have enough chips to bet {amount}.")
        self.chips -= amount
        self.current_bet += amount
        return amount

    def reset_bet(self):
        """
        Resets the current bet to 0 at the end of a betting round.
        """
        self.current_bet = 0

    def receive_cards(self, cards):
        """
        Adds cards to the player's hand.
        :param cards: List of Card objects to add to the hand.
        """
        self.hand.extend(cards)

    def show_hand(self):
        """
        Returns a string representation of the player's hand.
        """
        return ", ".join(str(card) for card in self.hand)

    def clear_hand(self):
        """
        Clears the player's hand at the end of a round.
        """
        self.hand = []

    def __repr__(self):
        return f"Player {self.name} with {self.chips} chips, current bet: {self.current_bet}, and hand: {self.show_hand()}"
