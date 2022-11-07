"""
    Module that contains the alpha-beta-pruning algorithm for the AI
"""
import math
from tqdm import tqdm
import pieces
import multiprocessing as m


class AI:
    """Handles the behavior of the AI"""

    def __init__(self, model, view, color, enemy):
        self.model = model
        self.view = view
        self.color = color
        self.enemy = enemy  # Enemy Color
        self.Pawn_table = [
            [0, 0, 0, 0, 0, 0, 0, 0],
            [5, 10, 10, -20, -20, 10, 10, 5],
            [5, -5, -10, 0, 0, -10, -5, 5],
            [0, 0, 0, 20, 20, 0, 0, 0],
            [5, 5, 10, 25, 25, 10, 5, 5],
            [10, 10, 20, 30, 30, 20, 10, 10],
            [50, 50, 50, 50, 50, 50, 50, 50],
            [0, 0, 0, 0, 0, 0, 0, 0]
        ]
        self.Queen_table = [
            [-20, -10, -10, -5, -5, -10, -10, -20],
            [-10, 0, 5, 0, 0, 0, 0, -10],
            [-10, 5, 5, 5, 5, 5, 0, -10],
            [0, 0, 5, 5, 5, 5, 0, -5],
            [-5, 0, 5, 5, 5, 5, 0, -5],
            [-10, 0, 5, 5, 5, 5, 0, -10],
            [-10, 0, 0, 0, 0, 0, 0, -10],
            [-20, -10, -10, -5, -5, -10, -10, -20]
        ]
        self.Bishop_table = [
            [-20, -10, -10, -10, -10, -10, -10, -20],
            [-10, 5, 0, 0, 0, 0, 5, -10],
            [-10, 10, 10, 10, 10, 10, 10, -10],
            [-10, 0, 10, 10, 10, 10, 0, -10],
            [-10, 5, 5, 10, 10, 5, 5, -10],
            [-10, 0, 5, 10, 10, 5, 0, -10],
            [-10, 0, 0, 0, 0, 0, 0, -10],
            [-20, -10, -10, -10, -10, -10, -10, -20]
        ]
        self.Horse_table = [
            [-50, -40, -30, -30, -30, -30, -40, -50],
            [-40, -20, 0, 5, 5, 0, -20, -40],
            [-30, 5, 10, 15, 15, 10, 5, -30],
            [-30, 0, 15, 20, 20, 15, 0, -30],
            [-30, 5, 15, 20, 20, 15, 0, -30],
            [-30, 0, 10, 15, 15, 10, 0, -30],
            [-40, -20, 0, 0, 0, 0, -20, -40],
            [-50, -40, -30, -30, -30, -30, -40, -50]
        ]
        self.Rook_table = [
            [0, 0, 0, 5, 5, 0, 0, 0],
            [-5, 0, 0, 0, 0, 0, 0, -5],
            [-5, 0, 0, 0, 0, 0, 0, -5],
            [-5, 0, 0, 0, 0, 0, 0, -5],
            [-5, 0, 0, 0, 0, 0, 0, -5],
            [-5, 0, 0, 0, 0, 0, 0, -5],
            [5, 10, 10, 10, 10, 10, 10, 5],
            [0, 0, 0, 0, 0, 0, 0, 0]
        ]

    def alpha_beta_pruning(self, state, depth, alpha, beta, ai_playing):
        """Returns the score of the current board"""

        # calcs the score of the current board
        if depth == 0 or not self.model.check_for_king():
            return self.calculate_board_value(state)

        if ai_playing:
            ai_value = -math.inf
            self.model.currently_playing = "White"
            # calcs the score of every possible move
            for next_move in self.get_possible_moves(self.enemy, state):

                x_move, y_move = next_move

                temp = self.model.get_copy_board_state(state)

                change_position = None

                try:

                    change_position = temp[x_move].position
                    temp[x_move].position = y_move
                    temp[y_move] = temp[x_move]
                    temp[x_move] = None
                except AttributeError:
                    pass

                # calcs the score of the current board
                value = self.alpha_beta_pruning(temp, depth - 1, alpha, beta, False)

                if change_position is not None:
                    temp[y_move].position = change_position

                self.model.currently_playing = "Black"

                # White want the score as high as possible
                ai_value = max(ai_value, value)

                alpha = max(alpha, value)
                if beta <= alpha:
                    break
            return ai_value

        player_value = math.inf
        self.model.currently_playing = "Black"
        for next_move in self.get_possible_moves(self.color, state):

            x_move, y_move = next_move

            temp = self.model.get_copy_board_state(state)

            change_position = None

            try:

                change_position = temp[x_move].position
                temp[x_move].position = y_move
                temp[y_move] = temp[x_move]
                temp[x_move] = None
            except AttributeError:
                pass

            value = self.alpha_beta_pruning(temp, depth - 1, alpha, beta, True)

            if change_position is not None:
                temp[y_move].position = change_position

            # Black wants the score as low as possible
            player_value = min(player_value, value)
            beta = min(beta, value)
            if beta <= alpha:
                break
        return player_value

    @staticmethod
    def get_score_pieces(current_game_state):

        """
        Returns the score of the current pieces
        """

        black = 0
        white = 0

        for i in current_game_state:

            if type(i) is pieces.Rook:

                if i.colour == "White":
                    white += 500
                else:
                    black += 500

            if type(i) is pieces.Pawn:
                if i.colour == "White":
                    white += 100
                else:
                    black += 100

            if type(i) is pieces.Horse:
                if i.colour == "White":
                    white += 320
                else:
                    black += 320

            if type(i) is pieces.Bishop:
                if i.colour == "White":
                    white += 330
                else:
                    black += 330

            if type(i) is pieces.King:
                if i.colour == "White":
                    white += 20000
                else:
                    black += 20000

            if type(i) is pieces.Queen:
                if i.colour == "White":
                    white += 900
                else:
                    black += 900

        return white - black

    # @staticmethod
    def score_position(self, pieces_type, table, piece_val, current_game_state):
        """Evaluates the current position of a pieces"""
        white = 0
        black = 0
        count = 0

        for i in current_game_state:
            if type(i) is pieces_type:
                if i.colour == "White":
                    white += piece_val
                else:
                    y = math.floor(count/8)
                    x = count - (y * 7) - y
                    black += table[7-x][y]
            count += 1
        return white-black

    # @staticmethod
    def calculate_board_value(self, current_game_state):
        """Evaluate the current Board"""

        piece = self.get_score_pieces(current_game_state)

        pawn = self.score_position(pieces.Pawn, self.Pawn_table, 100, current_game_state)
        horse = self.score_position(pieces.Horse, self.Horse_table, 320, current_game_state)
        bishop = self.score_position(pieces.Bishop, self.Bishop_table, 330, current_game_state)
        rook = self.score_position(pieces.Rook, self.Rook_table, 500, current_game_state)
        queen = self.score_position(pieces.Queen, self.Queen_table, 900, current_game_state)

        return piece + pawn + rook + horse + bishop + queen

    @staticmethod
    def get_possible_moves(color, state):
        """Get all possible moves of the color"""

        move = []

        for i in state:
            try:
                if i.colour == color:
                    possible_move = i.check_legal_move(i.position, state, True)
                    if len(possible_move) > 0:
                        for moves in possible_move:
                            if 0 < moves < 64:
                                move.append([i.position, moves])

            except AttributeError:
                continue

        return move

    def calc_move(self, moves, queue, state):

        best_score = math.inf
        final_move = None

        # Calcs every possible move of the AI
        for next_move in moves:

            temp = self.model.get_copy_board_state(state)

            x_move, y_move = next_move
            change_position = None

            try:

                # if a pieces got the attribute position, it has to be saved and changed
                change_position = temp[x_move].position
                temp[x_move].position = y_move
                temp[y_move] = temp[x_move]
                temp[x_move] = None
            except AttributeError:
                pass

            # calcs the score of the current move
            current_score = self.alpha_beta_pruning(temp, 3, -math.inf, math.inf, True)

            if change_position is not None:
                temp[y_move].position = change_position

            if current_score < best_score:
                best_score = current_score
                final_move = next_move

        queue.put([final_move, best_score])

    def move(self):
        """
        Main function
        Calcs the best move for the AI moves
        """

        print("AI thinks...")

        # The current board self.model.board_state shouldn't be overwritten
        # Therefore state is a copy of the Value and not a copy of the Instance
        state = self.model.get_copy_board_state()
        possible_moves = self.get_possible_moves(self.color, state)
        result = []

        # Splits the list possible_moves in as many chunks as the PC has cores
        k, a = divmod(len(possible_moves), m.cpu_count())
        process_moves = list(possible_moves[i * k + min(i, a):
                                            (i + 1) * k + min(i + 1, a)] for i in range(m.cpu_count()))

        output = tqdm(total=m.cpu_count())

        processes = []
        queue = m.Queue()

        for i in process_moves:
            processes.append(m.Process(target=self.calc_move, args=(i, queue, state,)))
            processes[len(processes) - 1].start()

        for i in processes:
            i.join()
            output.update()

        for _ in range(queue.qsize()):
            result.append(queue.get())

        result = sorted(result, key=lambda x: x[1])
        same_score = []
        lower_score = result[0][1]

        for i in result:
            if i[1] == lower_score:
                same_score.append(i)

        same_score.sort()

        x_move, y_move = same_score[0][0]

        output.close()

        self.model.move_piece(x_move, y_move)
