import random
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import List, Union, Tuple


@dataclass
class Card:
    group: str
    rank: str

    GROUPS = ['A', 'B', 'C', 'D', 'E']
    RANKS = ['0', '1', '2', '3']

    _holder: 'Player' = None
    _not_holders: List['Player'] = field(default_factory=list)

    def __str__(self):
        return f"{self.group}-{self.rank}"

    def __eq__(self, other):
        return self.group == other.group and self.rank == other.rank

    @property
    def holder(self):
        return self._holder

    @holder.setter
    def holder(self, player: 'Player'):
        self._holder = player
        self._not_holders = []  # all other players are not holder

    @property
    def not_holders(self) -> List['Player']:
        return self._not_holders

    @not_holders.setter
    def not_holders(self, player: 'Player'):
        if self.holder is player:
            self.holder = None
        self._not_holders.append(player)


@dataclass
class Player:
    name: str = ''
    num_quartet: int = 0
    cards: List[Card] = field(default_factory=list)

    def __str__(self):
        return f"{self.name}: [{','.join([str(i) for i in self.cards])}]"

    @property
    def has_cards(self):
        return True if len(self.cards) != 0 else False

    def cards_player_can_ask_for(self, card_deck: List[Card]) -> List[Card]:
        grouped_cards = defaultdict(list)
        for card in self.cards:
            grouped_cards[card.group].append(card.rank)

        card_indices = []
        for group, ranks in grouped_cards.items():
            missing_ranks = [r for r in Card.RANKS if r not in ranks]
            for r in missing_ranks:
                card_indices.append(card_deck.index(Card(group, r)))

        return [card_deck[i] for i in card_indices]

    def get_quartet_in_hand(self) -> Union[None, List[Card]]:
        """
        Check if there is a quartet in self.cards, if so, return the card group, otherwise, return None
        """
        count_in_group = Counter()
        for card in self.cards:
            count_in_group[card.group] += 1
            if count_in_group[card.group] == 4:
                return [Card(card.group, rank) for rank in Card.RANKS]

    @property
    def has_quartet_in_hand(self) -> bool:
        return self.get_quartet_in_hand() is not None

    def request_for_card(
        self, players: List, card_deck: List[Card]
    ) -> Union[None, Tuple]:
        """
        Determine which card self can ask and who to ask for. Also mark self as not-a-holder of the card
        """
        cards = self.cards_player_can_ask_for(card_deck)
        print(f"There are {len(cards)} cards {self.name} can ask for.")
        if not cards:
            return

        for card in cards:
            if card.holder:
                return card, card.holder
            if card.not_holders:
                other_players = [
                    p
                    for p in players
                    if p != self and p.has_cards and p not in card.not_holders
                ]
                if other_players:
                    card.not_holders = self
                    return card, other_players[0]
            else:
                card.not_holders = self
                return card, Game.get_next_player(self, players)

    def answer_card_request(self, card: Card) -> Union[None, Card]:
        """
        Other player ask if self has a certain card. Answering with the card, or return None
        """
        if card in self.cards:
            self.cards.remove(card)
            if card.holder:
                card.holder = None
            return card

        else:
            card.not_holders = self
            return None

    def receive_card(self, card: Card) -> None:
        self.cards.append(card)
        card.holder = self


@dataclass
class Game:
    card_deck: List[Card] = field(default_factory=list)
    players: List[Player] = field(default_factory=list)

    def __init__(self, card_deck: List[Card] = None, players: List[Player] = None):
        self.card_deck = card_deck if card_deck else self.initialize_cards()
        self.players = players if players else self.initialize_players()
        self._validate()

    def _validate(self):
        """
        check constraints before the game start
        """
        assert len(self.card_deck) % len(self.players) == 0
        assert len(self.card_deck) % 4 == 0

    @staticmethod
    def initialize_cards() -> List[Card]:
        card_deck: List[Card] = list(
            Card(group, rank) for group in Card.GROUPS for rank in Card.RANKS
        )
        return card_deck

    @staticmethod
    def initialize_players() -> List[Player]:
        players: List[Player] = [
            Player('Amelia'),
            Player('Ben'),
            Player('Carl'),
            Player('Diane'),
        ]
        return players

    @classmethod
    def get_next_player(
        cls, turn_player: Player, players: List[Player]
    ) -> Union[None, Player]:
        if not any(player.has_cards for player in players):
            return None

        turn_inx = players.index(turn_player)
        next_player = players[(turn_inx + 1) % len(players)]

        while not next_player.has_cards:
            turn_inx += 1
            next_player = players[turn_inx % len(players)]

        return next_player

    def shuffle_cards_to_players(self) -> None:
        cards = self.card_deck
        players = self.players
        num_player = len(players)
        assert len(cards) % num_player == 0

        random.shuffle(cards)

        for i in range(len(cards)):
            players[i % num_player].cards.append(cards[i])

    def player_puts_down_quartet(self, player: Player) -> None:
        """
        Remove the quartet cards from self.cards, add up a num_quartet, remove those cards from card_deck
        """
        quartet = player.get_quartet_in_hand()
        if not quartet:
            return

        for card in quartet:
            player.cards.remove(card)
            self.card_deck.remove(card)

        player.num_quartet += 1

    def run(self):
        turn_player: Player = self.players[0]
        while len(self.card_deck) != 0:
            print(f'')
            for player in self.players:
                print(f"{player}")
            while turn_player and turn_player.has_quartet_in_hand:
                print(f"{turn_player.name} has a quartet!")
                quartet = turn_player.get_quartet_in_hand()
                print(
                    f"{turn_player.name} is putting down [{','.join([str(card) for card in quartet])}]"
                )
                self.player_puts_down_quartet(turn_player)
                if not turn_player.has_cards:
                    print(f"{turn_player.name} is out of cards")
                    turn_player = Game.get_next_player(turn_player, self.players)

            if not turn_player:
                break
            print(f"It is {turn_player.name}'s turn.")

            card, other_player = turn_player.request_for_card(
                self.players, self.card_deck
            )
            if other_player is None:
                turn_player = Game.get_next_player(turn_player, self.players)

            print(f"{turn_player.name} is asking {other_player.name} for {card}")
            requested_card = other_player.answer_card_request(card)
            if requested_card:
                print(
                    f"{turn_player.name} gets {requested_card} from {other_player.name}."
                )
                turn_player.receive_card(card)
            else:
                print(f"{other_player.name} does not have {card}")
                turn_player = other_player


def run_game():
    game = Game()
    game.shuffle_cards_to_players()
    game.run()

    print(f"-----------")
    print(f"All players out of cards - game is over!")
    for player in game.players:
        print(f"{player.name} has {player.num_quartet} quartets")


if __name__ == '__main__':
    run_game()
