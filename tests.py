import unittest

from game_mechanics import Card, Deck, Player
from utils import evaluate_hand, compare_hands, calculate_pot_odds


class TestGameMechanics(unittest.TestCase):
    def test_card_representation(self):
        card = Card('Ace', 'Spades')
        self.assertEqual(str(card), "Ace of Spades")

    def test_deck_initialization(self):
        deck = Deck()
        self.assertEqual(len(deck.cards), 52)
        self.assertNotEqual(deck.cards, sorted(deck.cards, key=lambda x: (x.rank, x.suit)))  # Deck is shuffled

    def test_deck_deal(self):
        deck = Deck()
        dealt_cards = deck.deal(5)
        self.assertEqual(len(dealt_cards), 5)
        self.assertEqual(len(deck.cards), 47)

    def test_player_bet(self):
        player = Player("TestPlayer", chips=1000)
        bet_amount = player.bet(100)
        self.assertEqual(bet_amount, 100)
        self.assertEqual(player.chips, 900)
        self.assertEqual(player.current_bet, 100)


class TestUtils(unittest.TestCase):
    def test_calculate_pot_odds(self):
        pot_odds = calculate_pot_odds(player_bet=50, pot_size=200, call_amount=50)
        self.assertAlmostEqual(pot_odds, 0.2)  # 50 / (200 + 50)

    def test_evaluate_hand_high_card(self):
        hand = [Card('2', 'Hearts'), Card('4', 'Diamonds')]
        community_cards = [Card('6', 'Clubs'), Card('8', 'Spades'), Card('Jack', 'Hearts'), Card('3', 'Diamonds'), Card('9', 'Hearts')]
        rank, sorted_hand, rank_value = evaluate_hand(hand + community_cards)
        self.assertEqual(rank, "High Card")
        self.assertEqual(rank_value[0], Card.RANKS.index('Jack'))  # Jack is the highest card

    def test_evaluate_hand_pair(self):
        hand = [Card('Ace', 'Hearts'), Card('Ace', 'Diamonds')]
        community_cards = [Card('2', 'Clubs'), Card('4', 'Spades'), Card('6', 'Hearts'), Card('8', 'Diamonds'), Card('9', 'Spades')]
        rank, sorted_hand, rank_value = evaluate_hand(hand + community_cards)
        self.assertEqual(rank, "One Pair")
        self.assertEqual(rank_value[0], Card.RANKS.index('Ace'))  # Pair of Aces

    def test_compare_hands(self):
        hand1 = ("One Pair", [], (2, 13, 12, 11))  # Pair of 2s with kickers K, Q, J
        hand2 = ("One Pair", [], (2, 14, 12, 11))  # Pair of 2s with kickers A, Q, J
        result = compare_hands(hand1, hand2)
        self.assertEqual(result, -1)  # Hand2 wins with a higher kicker

    def test_compare_hands_tie(self):
        hand1 = ("One Pair", [], (2, 13, 12, 11))  # Pair of 2s with kickers K, Q, J
        hand2 = ("One Pair", [], (2, 13, 12, 11))  # Identical hand
        result = compare_hands(hand1, hand2)
        self.assertEqual(result, 0)  # It's a tie

    def test_ai_does_not_use_human_hand(self):
        from game_mechanics import Card
        from ai_logic import AIDecisionMaker

        ai = AIDecisionMaker()
        ai_hand = [Card("Ace", "Spades"), Card("King", "Hearts")]
        community_cards = [Card("2", "Clubs"), Card("7", "Diamonds"), Card("10", "Hearts")]
        pot_odds = 0.3

        # Simulate AI decision
        decision = ai.decide_action(ai_hand, community_cards, pot_odds)

        # Verify no unexpected behavior
        assert decision in ["fold", "call", "raise"], "Invalid AI action."


if __name__ == '__main__':
    unittest.main()
