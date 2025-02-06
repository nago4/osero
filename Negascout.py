import time
import random

class NegascoutNode:
    def __init__(self, state, parent=None):
        self.state = state
        self.parent = parent
        self.children = []
        self.best_move = None

    def add_child(self, child):
        self.children.append(child)

class Negascout:
    def __init__(self, depth_limit=5):
        self.depth_limit = depth_limit

    def search(self, root_state):
        root_node = NegascoutNode(root_state)
        score = self.negascout(root_node, self.depth_limit, -float('inf'), float('inf'), 1)
        return root_node.best_move

    def negascout(self, node, depth, alpha, beta, color):
        if depth == 0 or node.state.is_game_over():
            return color * self.evaluate(node.state)

        moves = node.state.get_valid_moves()
        if not moves:
            return -self.negascout(node, depth-1, -beta, -alpha, -color)

        score = -float('inf')
        for i, move in enumerate(moves):
            new_state = node.state.clone()
            new_state.apply_move(move)
            child_node = NegascoutNode(new_state, parent=node)
            node.add_child(child_node)

            if i == 0:
                current_score = -self.negascout(child_node, depth-1, -beta, -alpha, -color)
            else:
                current_score = -self.negascout(child_node, depth-1, -alpha-1, -alpha, -color)
                if alpha < current_score < beta:
                    current_score = -self.negascout(child_node, depth-1, -beta, -current_score, -color)

            if current_score > score:
                score = current_score
                node.best_move = move

            alpha = max(alpha, score)
            if alpha >= beta:
                break

        return score

    def evaluate(self, state):
        # 簡単な評価関数（自分の駒の数 - 相手の駒の数）
        return sum(state.board)

class NegascoutPlayer:
    def __init__(self, depth_limit=5):
        self.negascout = Negascout(depth_limit)
        self.total_time = 0  # AIが考えた合計時間を保持

    def get_move(self, game_state):
        if not game_state.get_valid_moves():
            return None
        start_time = time.time()
        move = self.negascout.search(game_state)
        end_time = time.time()
        self.total_time += (end_time - start_time)  # 合計時間を更新
        return move

class OthelloGame:
    def __init__(self):
        self.board = self.initialize_board()
        self.current_player = 1
        self.last_move = None
        self.turns_passed = 0

    def initialize_board(self):
        board = [0] * 64
        board[27], board[36] = -1, -1  # 白
        board[28], board[35] = 1, 1  # 黒
        return board

    def get_valid_moves(self):
        moves = []
        for i in range(64):
            if self.is_valid_move(i):
                moves.append(i)
        return moves

    def is_valid_move(self, index):
        if self.board[index] != 0:
            return False
        x, y = index // 8, index % 8
        directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        for dx, dy in directions:
            if self.can_flip(x, y, dx, dy):
                return True
        return False

    def can_flip(self, x, y, dx, dy):
        opponent = -self.current_player
        flipped = False
        nx, ny = x + dx, y + dy
        while 0 <= nx < 8 and 0 <= ny < 8:
            ni = nx * 8 + ny
            if self.board[ni] == opponent:
                flipped = True
            elif self.board[ni] == self.current_player:
                return flipped
            else:
                return False
            nx += dx
            ny += dy
        return False

    def flip_discs(self, move, player):
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
        flips = []
        for direction in directions:
            flipped = []
            x, y = divmod(move, 8)
            dx, dy = direction
            nx, ny = x + dx, y + dy
            while 0 <= nx < 8 and 0 <= ny < 8:
                index = nx * 8 + ny
                if self.board[index] == 0:
                    break
                if self.board[index] == player:
                    flips.extend(flipped)
                    break
                flipped.append(index)
                nx += dx
                ny += dy
        return flips

    def pass_turn(self):
        self.turns_passed += 1
        self.current_player = -self.current_player
        print(f"Player {self.current_player} has passed their turn.")

    def apply_move(self, move):
        if move is not None and self.is_valid_move(move):
            self.board[move] = self.current_player
            self.last_move = move
            flips = self.flip_discs(move, self.current_player)
            for flip in flips:
                self.board[flip] = self.current_player
            self.current_player *= -1
            self.turns_passed = 0
        else:
            print(f"Invalid move detected: {move}")

    def clone(self):
        new_game = OthelloGame()
        new_game.board = self.board[:]
        new_game.current_player = self.current_player
        return new_game

    def is_game_over(self):
        if all(cell != 0 for cell in self.board):
            return not self.get_valid_moves()
        if self.turns_passed >= 2:
            return False
        return not self.get_valid_moves()

    def get_winner(self):
        score = sum(self.board)
        return 1 if score > 0 else -1 if score < 0 else 0

    def print_board(self):
        edge = 8
        print("\n  0 1 2 3 4 5 6 7")
        for i in range(edge):
            temp = []
            temp.append(str(int(i)))
            for el in self.board[edge * i:edge * (i + 1)]:
                if el == -1:
                    temp.append("○")
                elif el == 1:
                    temp.append("●")
                else:
                    temp.append("+")
            print(" ".join(temp))

def main():
    game = OthelloGame()
    ai_player = NegascoutPlayer(depth_limit=5)

    while not game.is_game_over():
        game.print_board()
        while True:
            if game.turns_passed >= 2:
                break
            moves = game.get_valid_moves()
            if len(moves) == 0:
                print("Pass")
                game.pass_turn()
                continue
            if game.current_player == 1:  # ランダムプレイヤー（黒）
                move = random.choice(moves)
            else:  # AIプレイヤー（白）
                print("AIが思考中...")
                move = ai_player.get_move(game)
                if move is None:
                    print("AIはパスします")
                    game.pass_turn()
                    continue
            if move in moves:
                game.apply_move(move)
                game.print_board()
            else:
                print("そこにはおけません")

    winner = game.get_winner()
    if winner == 1:
        print("ランダムプレイヤーの勝ち!")
    elif winner == -1:
        print("AIの勝ち!")
    else:
        print("引き分け!")

    # AIが考えた合計時間を表示
    print(f"AIが考えた合計時間: {ai_player.total_time:.2f}秒")

if __name__ == "__main__":
    main()