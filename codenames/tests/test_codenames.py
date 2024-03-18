import unittest

from codenames.codenames_engine import Card, Board, Codenames


def create_test_board() -> Board:
    return Board(words=['OCTOPUS', 'WAR', 'MICROSCOPE', 'TEACHER', 'SATURN', 'LEPRECHAUN', 'ANTARCTICA', 'SKYSCRAPER',
                        'LINK', 'NET', 'POLICE', 'SHOE', 'DOG', 'PLOT', 'LASER', 'CHAIR', 'TORCH', 'BEAT', 'PLAY',
                        'CHICK', 'GENIUS', 'DRILL', 'LAWYER', 'PLATYPUS', 'WALL'])


class TestCard(unittest.TestCase):
    def test_reveal(self):
        card = Card("HELLO", "RED")
        assert (card.word, card.color, card.revealed) == ("HELLO", "RED", None)
        assert card.public_view() == ("HELLO", None)
        card.reveal()
        assert (card.word, card.color, card.revealed) == ("HELLO", "RED", "RED")
        assert card.public_view() == ("HELLO", "RED")


class TestBoard(unittest.TestCase):

    def test_create(self):
        board = create_test_board()
        assert len(board.words) == 25
        assert len(board.red) == 9
        assert len(board.blue) == 8
        assert len(board.grey) == 7
        assert len(board.black) == 1

    def test_public_cards(self):
        board = create_test_board()
        cards = board.public_cards()
        for (word, revealed) in cards:
            assert revealed is None

    def test_hidden_cards(self):
        board = create_test_board()
        cards = board.hidden_cards()
        for (word, color, revealed) in cards:
            assert color == board.get_word_color(word)
            assert revealed is None

    def test_reveal(self):
        board = create_test_board()

        for i in range(len(board.cards)):
            assert board.cards[i].revealed is None
            board.reveal(board.cards[i].word)
            assert board.cards[i].revealed == board.cards[i].color


class TestCodenames(unittest.TestCase):
    def test_create(self):
        board = create_test_board()
        game = Codenames(board)
        assert game.board is board
        assert game.turn == "RED"
        assert game.remaining.get("RED") == 9
        assert game.remaining.get("BLUE") == 8
        assert game.assassinated is None

    def test_public_words(self):
        board = create_test_board()
        game = Codenames(board)
        words: list[str] = game.public_words()
        assert len(words) == 25
        for word in words:
            assert word in board.words

    def test_winner(self):
        pass

    def test_end_turn(self):
        board = create_test_board()
        game = Codenames(board)
        start_turn = game.turn
        assert game.end_turn() == Codenames.opposite_team(start_turn)
        assert game.turn == Codenames.opposite_team(start_turn)

    def test_guess(self):
        pass

    def test_opposite_team(self):
        assert Codenames.opposite_team("RED") == "BLUE"
        assert Codenames.opposite_team("BLUE") == "RED"


if __name__ == '__main__':
    unittest.main()
