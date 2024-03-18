from codenames.codenames_engine import Card, Board, Codenames


def create_test_board() -> Board:
    return Board(words=['OCTOPUS', 'WAR', 'MICROSCOPE', 'TEACHER', 'SATURN', 'LEPRECHAUN', 'ANTARCTICA', 'SKYSCRAPER',
                        'LINK', 'NET', 'POLICE', 'SHOE', 'DOG', 'PLOT', 'LASER', 'CHAIR', 'TORCH', 'BEAT', 'PLAY',
                        'CHICK', 'GENIUS', 'DRILL', 'LAWYER', 'PLATYPUS', 'WALL'])


class TestCard:
    def test_reveal(self):
        card = Card("HELLO", "RED")
        assert (card.word, card.color, card.revealed) == ("HELLO", "RED", None)
        assert card.public_view() == ("HELLO", None)
        card.reveal()
        assert (card.word, card.color, card.revealed) == ("HELLO", "RED", "RED")
        assert card.public_view() == ("HELLO", "RED")

    def test_format(self):
        card = Card("HELLO", "RED")
        assert card.__repr__() == "HELLO (RED, revealed=None)"
        card.reveal()
        assert card.__repr__() == "HELLO (RED, revealed=RED)"


class TestBoard:

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

    def test_public_words(self):
        board = create_test_board()
        words: list[str] = board.public_unrevealed_words()
        assert len(words) == 25
        for word in words:
            assert word in board.words

    def test_reveal(self):
        board = create_test_board()

        assert len(board.public_unrevealed_words()) == 25
        for i in range(len(board.cards)):
            assert board.cards[i].revealed is None
            assert board.reveal(board.cards[i].word) is not None
            assert board.cards[i].revealed == board.cards[i].color
            assert len(board.public_unrevealed_words()) == 24 - i
        assert len(board.public_unrevealed_words()) == 0
        assert board.reveal(board.cards[0].word) is None

    def test_reveal_missing(self):
        board = create_test_board()
        assert len(board.public_unrevealed_words()) == 25
        board.reveal("NOT_ON_BOARD")
        assert len(board.public_unrevealed_words()) == 25


class TestCodenames:
    def test_create(self):
        board = create_test_board()
        game = Codenames(board)
        assert game.board is board
        assert game.turn == "RED"
        assert game.remaining.get("RED") == 9
        assert game.remaining.get("BLUE") == 8
        assert game.assassinated is None

    def test_winner_red(self):
        board = create_test_board()
        game = Codenames(board)
        assert game.winner() is None
        game.remaining["RED"] = 0
        assert game.winner() == "RED"

    def test_winner_blue(self):
        board = create_test_board()
        game = Codenames(board)
        assert game.winner() is None
        game.remaining["BLUE"] = 0
        assert game.winner() == "BLUE"

    def test_winner_assassinated(self):
        board = create_test_board()
        game = Codenames(board)
        assert game.winner() is None
        game.assassinated = "RED"
        assert game.winner() == "BLUE"

    def test_end_turn(self):
        board = create_test_board()
        game = Codenames(board)
        start_turn = game.turn
        assert game.end_turn() == Codenames.opposite_team(start_turn)
        assert game.turn == Codenames.opposite_team(start_turn)

    def test_guess(self):
        board = create_test_board()
        game = Codenames(board)
        assert len(board.public_unrevealed_words()) == 25
        assert game.remaining.get("RED") == 9
        assert game.remaining.get("BLUE") == 8
        assert game.turn == "RED"
        assert game.winner() is None

        # guess an invalid word
        assert game.guess("NOT_ON_BOARD") is None
        assert len(board.public_unrevealed_words()) == 25
        assert game.remaining.get("RED") == 9
        assert game.remaining.get("BLUE") == 8
        assert game.turn == "RED"
        assert game.winner() is None

        # guess a red word
        assert game.guess(board.red[0].word) == "RED"
        assert len(board.public_unrevealed_words()) == 24
        assert game.remaining.get("RED") == 8
        assert game.remaining.get("BLUE") == 8
        assert game.turn == "RED"
        assert game.winner() is None

        # guess a blue word
        assert game.guess(board.blue[0].word) == "BLUE"
        assert len(board.public_unrevealed_words()) == 23
        assert game.remaining.get("RED") == 8
        assert game.remaining.get("BLUE") == 7
        assert game.turn == "BLUE"
        assert game.winner() is None

        # guess a grey word
        assert game.guess(board.grey[0].word) == "GREY"
        assert len(board.public_unrevealed_words()) == 22
        assert game.remaining.get("RED") == 8
        assert game.remaining.get("BLUE") == 7
        assert game.turn == "RED"
        assert game.winner() is None

        # re-guess a word
        assert game.guess(board.grey[0].word) is None
        assert len(board.public_unrevealed_words()) == 22
        assert game.remaining.get("RED") == 8
        assert game.remaining.get("BLUE") == 7
        assert game.turn == "RED"
        assert game.winner() is None

        # guess the black word
        assert game.guess(board.black[0].word) == "BLACK"
        assert len(board.public_unrevealed_words()) == 21
        assert game.remaining.get("RED") == 8
        assert game.remaining.get("BLUE") == 7
        assert game.turn == "BLUE"
        assert game.winner() is "BLUE"

        # attempt to guess after the game is over
        assert game.guess(board.red[1].word) is None
        assert len(board.public_unrevealed_words()) == 21
        assert game.remaining.get("RED") == 8
        assert game.remaining.get("BLUE") == 7
        assert game.turn == "BLUE"
        assert game.winner() is "BLUE"

    def test_opposite_team(self):
        assert Codenames.opposite_team("RED") == "BLUE"
        assert Codenames.opposite_team("BLUE") == "RED"
