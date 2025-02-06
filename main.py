import random
import time

class MCTSNode:
    def __init__(self, state, parent=None):
        if state is None:
            print("Error: state is None")
        self.state = state  # オセロの盤面状態
        self.parent = parent  # 親ノード
        self.children = []  # 子ノードリスト
        self.visits = 0  # 訪問回数 N
        self.wins = 0  # 勝ち数 W
        self.untried_moves = state.get_valid_moves()  # 未探索の手
        self.exploration_weight = 1.4  # 探索の重み（UCB1の係数）

    def is_fully_expanded(self):
        """ すべての手が展開されたか """
        return len(self.untried_moves) == 0

    def best_child(self, exploration_weight=1.4):
        """ UCB1 に基づいて最良の子を選択 """
        if not self.children:
            print("Warning: No children available to select best child.")
            return None  # あるいは適切なデフォルトノードを返す

        return max(self.children, key=lambda child: child.get_value(exploration_weight))

    def expand(self):
        """ 未探索の手からランダムに1つ選び、新しいノードを作る """
        if not self.untried_moves:
            return self  # すでに全ての手を試した場合
        move = self.untried_moves.pop()
        new_state = self.state.clone()  # 盤面をコピー
        new_state.apply_move(move)  # 手を適用
        
        child_node = MCTSNode(new_state, parent=self)
        self.children.append(child_node)  # 子ノードを追加

        return child_node

    def backpropagate(self, result):
        """ シミュレーション結果を親ノードへ反映 """
        self.visits += 1
        self.wins += result
        if self.parent:
            self.parent.backpropagate(-result)  # 相手の視点で評価
    
    def get_value(self, exploration_weight):
        """UCB1値を計算"""
        if self.visits == 0:
            return float('inf')  # 未訪問ノードには無限大の価値を与える
        exploitation = self.wins / self.visits  # 実際の成果（勝率）
        exploration = exploration_weight * (self.parent.visits ** 0.5) / (1 + self.visits)  # 探索重み
        return exploitation + exploration

class MCTS:
    def __init__(self, iteration_limit=10000, time_limit=None, exploration_weight=1.4):
        self.iteration_limit = iteration_limit  # シミュレーション回数
        self.time_limit = time_limit  # 時間制限
        self.exploration_weight = exploration_weight  # UCB1の探索パラメータ

    def search(self, root_state):
        """ MCTSで最良の手を探索 """
        root_node = MCTSNode(root_state)
        start_time = time.time()

        for _ in range(self.iteration_limit):
            if self.time_limit and (time.time() - start_time) > self.time_limit:
                break
            
            node = self.select_node(root_node)  # 1. 選択
            if not node.state.is_game_over():
                node = node.expand()  # 2. 展開
            result = self.simulate(node.state)  # 3. シミュレーション
            node.backpropagate(result)  # 4. 逆伝播

        return root_node.best_child(exploration_weight=0).state.last_move  # 最良の手を返す

    def select_node(self, node):
        """ UCB1 を使ってノードを選択 """
        while not node.state.is_game_over() and node.is_fully_expanded():
            node = node.best_child(self.exploration_weight)
        # if node.children == []:
        #     print("No children found during selection.")
        return node

    def simulate(self, state):
        """ ランダムにプレイアウトして勝敗を返す """
        current_state = state.clone()
        while not current_state.is_game_over():
            moves = current_state.get_valid_moves()
            if moves:
                move = random.choice(moves)
                current_state.apply_move(move)
        return current_state.get_winner()  # 勝者を返す
    
class MCTSPlayer:
    def __init__(self, iteration_limit=100000, time_limit=None):
        self.mcts = MCTS(iteration_limit, time_limit)
        self.total_time = 0  # AIが考えた合計時間を保持

    def get_move(self, game_state):
        """ MCTSで最良の手を決定 """
        if not game_state.get_valid_moves():
            return None  # パス
        start_time = time.time()
        move = self.mcts.search(game_state)
        end_time = time.time()
        self.total_time += (end_time - start_time)  # 合計時間を更新
        return move

class OthelloGame:
    def __init__(self):
        self.board = self.initialize_board()  # 1次元リスト
        self.current_player = 1  # 1: 黒, -1: 白
        self.last_move = None  # 最後の手を保持する属性を追加
        self.turns_passed = 0  # パスしたターン数

    def initialize_board(self):
        """ 1次元リストで初期盤面を作成 """
        board = [0] * 64
        board[27], board[36] = -1, -1  # 白
        board[28], board[35] = 1, 1  # 黒
        return board

    def get_valid_moves(self):
        """ 現在のプレイヤーの合法手をリストで返す（インデックス形式）"""
        moves = []
        for i in range(64):
            if self.is_valid_move(i):
                moves.append(i)
        return moves

    def is_valid_move(self, index):
        """ 指定のインデックスの手が合法かを判定（ここにオセロのルールを追加） """
        if self.board[index] != 0:
            return False  # 仮実装（本当は判定ロジックを書く）
        
        x, y=index // 8, index % 8
        directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]  # 8方向
        for dx, dy in directions:
            if self.can_flip(x, y, dx, dy):
                return True  # どこか1方向でも挟めるならOK
        return False  # どの方向にも挟めないなら不正な手
    
    def can_flip(self, x, y, dx, dy):
        """ (x, y) から (dx, dy) 方向に石を挟めるかチェック """
        opponent = -self.current_player  # 相手の色
        flipped = False
        nx, ny = x + dx, y + dy

        while 0 <= nx < 8 and 0 <= ny < 8:
            ni = nx * 8 + ny  # 2次元 → 1次元変換

            if self.board[ni] == opponent:
                flipped = True  # 相手の石を見つけたら継続
            elif self.board[ni] == self.current_player:
                return flipped  # 自分の石が見つかったら、挟めていればOK
            else:
                return False  # 空白ならダメ

            nx += dx
            ny += dy

        return False  # 盤外まで進んだらダメ
    
    def flip_discs(self, move, player):
        """指定した位置で相手の駒をひっくり返す"""
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]  # 8方向
        flips = []  # ひっくり返す駒を保存

        for direction in directions:
            flipped = []  # 1方向におけるひっくり返される駒を一時的に保存
            x, y = divmod(move, 8)  # 1Dインデックスを2D座標に変換

            dx, dy = direction
            nx, ny = x + dx, y + dy

            while 0 <= nx < 8 and 0 <= ny < 8:  # 盤面の範囲内
                index = nx * 8 + ny  # 1Dインデックスに変換
                if self.board[index] == 0:  # 空きスペースの場合、ひっくり返せない
                    break
                if self.board[index] == player:  # 自分の色の駒が来た場合、ひっくり返しリストに追加
                    flips.extend(flipped)
                    break
                flipped.append(index)  # 相手の色の駒を挟んでいく

                # 次の位置に進む
                nx += dx
                ny += dy

        return flips  # ひっくり返す駒のリスト
    
    def pass_turn(self):
        """プレイヤーが手を打てない場合にターンをスキップ"""
        self.turns_passed += 1
        self.current_player = -self.current_player  # プレイヤー交代
        print(f"Player {self.current_player} has passed their turn.")

    def apply_move(self, move):
        """ 指定の手を適用し、盤面を更新する """
        if move is not None and self.is_valid_move(move):
            self.board[move] = self.current_player
            self.last_move = move  # 最後に行われた手を更新
            flips = self.flip_discs(move, self.current_player)
            # ひっくり返す
            for flip in flips:
                self.board[flip] = self.current_player
            self.current_player *= -1  # 手番を交代
            self.turns_passed = 0
        else:
            print(f"Invalid move detected: {move}")  # デバッグ用

    def clone(self):
        """ 盤面のコピーを作成（MCTSのため） """
        new_game = OthelloGame()
        new_game.board = self.board[:]  # 1次元リストのコピー
        new_game.current_player = self.current_player
        return new_game

    def is_game_over(self):
        """ ゲームが終了したかを判定 """
        if all(cell != 0 for cell in self.board):
            return not self.get_valid_moves()
        if self.turns_passed >= 2:return False
        return not self.get_valid_moves()

    def get_winner(self):
        """ 勝者を判定 """
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

def get_move_input():
    while True:
        try:
            x, y = map(int, input("行列指定 >> ").split())
            if 0 <= x < 8 and 0 <= y < 8:  # 入力された位置が盤面内か確認
                return x, y
            else:
                print("入力エラー: 盤面の範囲（0-7）で入力してください。")
        except ValueError:
            print("入力エラー: 2つの整数をスペースで区切って入力してください。")

#メイン関数
def main():
    num_games = 50  # 対戦回数
    ai_wins = 0
    random_wins = 0
    draws = 0
    total_ai_time = 0

    for _ in range(num_games):
        # ゲームのセットアップ
        game = OthelloGame()
        ai_player = MCTSPlayer(iteration_limit=1000)

        # AI vs ランダムプレイヤーの対戦
        while not game.is_game_over():
            while True:
                if game.turns_passed >= 2:
                    break
                moves = game.get_valid_moves()
                if len(moves) == 0:
                    game.pass_turn()
                    continue
                if game.current_player == 1:  # ランダムプレイヤー（黒）
                    move = random.choice(moves)
                else:  # AIプレイヤー（白）
                    move = ai_player.get_move(game)
                    if move is None:
                        game.pass_turn()
                        continue
                if move in moves:
                    game.apply_move(move)
                    break

        # 結果を集計
        winner = game.get_winner()
        if winner == 1:
            random_wins += 1
        elif winner == -1:
            ai_wins += 1
        else:
            draws += 1

        total_ai_time += ai_player.total_time

    # 勝率を表示
    print(f"AIの勝ち: {ai_wins}回 ({ai_wins / num_games * 100:.2f}%)")
    print(f"ランダムプレイヤーの勝ち: {random_wins}回 ({random_wins / num_games * 100:.2f}%)")
    print(f"引き分け: {draws}回 ({draws / num_games * 100:.2f}%)")
    print(f"AIが考えた合計時間の平均: {total_ai_time / num_games:.2f}秒")

if __name__ == "__main__":
    main()