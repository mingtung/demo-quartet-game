import unittest

from quartet import Game, Player, Card, run_game


class TestQuartet(unittest.TestCase):
    def setUp(self) -> None:
        self.player1 = Player('Test1')
        self.player1.cards = [Card('A', '0')]
        self.player2 = Player('Test2')
        self.player2.cards = [Card('A', '1'), Card('A', '2'), Card('A', '3')]

        self.players = [self.player1, self.player2]
        self.card_deck = self.player1.cards + self.player2.cards
        self.game = Game(card_deck=self.card_deck, players=self.players)

    def test_game_init(self):
        game = Game()
        game.shuffle_cards_to_players()
        self.assertEqual(len(game.card_deck), 20)
        self.assertEqual(len(game.players), 4)
        for player in game.players:
            self.assertEqual(len(player.cards), 5)

    def test_cards_player_can_ask_for(self):
        self.assertEqual(
            self.player1.cards_player_can_ask_for(self.card_deck),
            [Card('A', '1'), Card('A', '2'), Card('A', '3')],
        )
        self.assertEqual(
            self.player2.cards_player_can_ask_for(self.card_deck), [Card('A', '0')]
        )

    def test_request_for_card(self):
        card, other_player = self.player1.request_for_card(self.players, self.card_deck)

        self.assertEqual(self.player2, other_player)
        self.assertEqual(Card('A', '1'), card)

    def test_answer_card_request__has_the_card(self):
        card = Card('A', '0')
        requested_card = self.player1.answer_card_request(card)

        self.assertEqual(requested_card, card)
        self.assertEqual(self.player1.cards, [])
        self.assertNotEqual(self.player1, card.holder)

    def test_answer_card_request__doesnt_have_the_card(self):
        card = Card('B', '0')  # neither player1 nor player2 has this card
        requested_card = self.player1.answer_card_request(card)

        self.assertIsNone(requested_card)
        self.assertIn(self.player1, card.not_holders)

        requested_card = self.player2.answer_card_request(card)
        self.assertIsNone(requested_card)
        self.assertIn(self.player2, card.not_holders)

        self.assertEqual(card.not_holders, [self.player1, self.player2])

    def test_receive_card(self):
        card = Card('A', '1')
        self.player1.receive_card(card)

        self.assertIn(card, self.player1.cards)
        self.assertEqual(card.holder, self.player1)

    def test_has_quartet_in_hand(self):
        self.assertFalse(self.player2.has_quartet_in_hand)
        self.player2.cards.append(Card('A', '0'))

        self.assertTrue(self.player2.has_quartet_in_hand)

    def test_put_down_quartet(self):
        self.player2.cards.append(Card('A', '0'))
        self.assertEqual(len(self.player2.cards), 4)

        self.game.player_puts_down_quartet(self.player2)

        card_deck = self.game.card_deck
        self.assertEqual(len(self.player2.cards), 0)
        self.assertEqual(self.player2.num_quartet, 1)
        self.assertNotIn(Card('A', '0'), card_deck)
        self.assertNotIn(Card('A', '1'), card_deck)
        self.assertNotIn(Card('A', '2'), card_deck)
        self.assertNotIn(Card('A', '3'), card_deck)

    def test_run_game(self):
        for i in range(10):
            run_game()


if __name__ == '__main__':
    unittest.main()
