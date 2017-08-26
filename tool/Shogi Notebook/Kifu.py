import numpy as np
from collections import Counter
from collections import OrderedDict
import Board
from Board import Move_Detail
from PieceDistribution import PieceDistribution

kifu_option_test = {
    "title": "",
    "black_name": "",
    "white_name": "",
    "teai": "",
    "comment": "",
    "debug": ""
}


def calc_center(list_: object) -> (float, float):
    """2変数タプルのリスト列で表現されたデータから重心を求める(ただの平均値)"""
    x_  = 0.0
    y_  = 0.0
    count = float(len(list_))
    for (x, y) in list_:
        x_ += x
        y_ += y
    return (x_ / count, y_ / count)


class PieceDistributionData:
    def __init__(self):
        self.black_piece_value = []
        self.white_piece_value = []
        self.diff_piece_value = []
        self.black_piece_point = []
        self.white_piece_point = []
        self.black_nyugoku_point = []
        self.white_nyugoku_point = []

    def add(self, p_d: PieceDistribution):
        self.black_piece_value.append(p_d.get_black_piece_value())
        self.white_piece_value.append(p_d.get_white_piece_value())
        self.diff_piece_value.append(p_d.get_diff_piece_value())
        self.black_piece_point.append(p_d.get_black_piece_point())
        self.white_piece_point.append(p_d.get_white_piece_point())
        self.black_nyugoku_point.append(p_d.get_black_nyugoku_point())
        self.white_nyugoku_point.append(p_d.get_white_nyugoku_point())


class Kifu:
    """sfen形式の棋譜を扱うクラス"""
    # コンストラクタ
    def __init__(self, sfen="sfen lnsgkgsnl/1r5b1/ppppppppp/9/9/9/PPPPPPPPP/1B5R1/LNSGKGSNL b - 1", stat_flag=True, kifu_option=None):
        """初期局面を与える。stat_flagは詰将棋など特殊局面で棋譜統計を切りたい時にFalseにする"""
        self.startBoard = Board.Board(sfen) # 初期局面(固定)
        self.nowBoard = Board.Board(sfen) # 現局面
        self.position_ = "position " + sfen + " moves " # position用のsfen
        self.movelist = [] # 棋譜
        self.stat_flag = stat_flag
        if stat_flag:
            self.__init_stat()
        if kifu_option:
            self.kifu_option = kifu_option

    def __init_stat(self):
        """棋譜統計情報の初期化を行います"""
        self.pass_of_K = [self.nowBoard.get_x_pos1("K")] # 先手玉の位置
        self.pass_of_k = [self.nowBoard.get_x_pos1("k")] # 後手玉の位置
        self.pass_of_R = [self.nowBoard.get_x_pos1("R")] # 先手飛の位置 (開始時にはある前提)
        self.pass_of_r = [self.nowBoard.get_x_pos1("r")] # 後手飛の位置 (開始時にはある前提)
        self.pass_of_R_flag = True # このフラグがTrueの間飛車の位置を記録する
        self.pass_of_r_flag = True # このフラグがTrueの間飛車の位置を記録する
        self.stat_move = OrderedDict() # 動かした駒種の統計
        od_list = (('K', 0),('R', 0),('B', 0),('G', 0),('S', 0),('N', 0),('L', 0),('P', 0),
                   ('+R', 0),('+B', 0),('+S', 0),('+N', 0),('+L', 0),('+P', 0),('*_b', 0),
                  ('k', 0),('r', 0),('b', 0),('g', 0),('s', 0),('n', 0),('l', 0),('p', 0),
                   ('+r', 0),('+b', 0),('+s', 0),('+n', 0),('+l', 0),('+p', 0),('*_w', 0))
        self.stat_move.update(OrderedDict(od_list))
        self.stat_promote_b = 0 # 先手の成りの数
        self.stat_promote_w = 0 # 後手の成りの数
        self.stat_score_val = [] # 評価値
        self.stat_progress = [] # 進行度
        self.piece_distribution = PieceDistribution(self.nowBoard) # 駒割計算用
        self.stat_piece_distribution = PieceDistributionData() # 駒割

    def set_option(self, option):
        """棋譜のオプションをセットする"""
        self.title = option["title"]
        self.black_name = option["black_name"]
        self.white_name = option["white_name"]
        self.teai = option["teai"]
        self.comment = option["comment"]
        self.debug = option["debug"]

    def get_tesuu(self) -> int:
        """手数を返す"""
        return len(self.movelist)

    def get_sfen(self) -> str:
        return self.position_ + ' '.join(self.movelist)

    def move(self, m: str, info=None, progress=None):
        move_detail = self.nowBoard.move(m) # 現局面を動かす
        self.movelist.append(m) # 棋譜に追加
        if self.stat_flag:
            self.__move_stat(move_detail, info, progress) # 統計情報用の分析を行います

    def gameover(self, black_result: str): # 投了、千日手など対局を終了させる
        self.result = black_result # 先手の勝敗結果を与える

    def __move_stat(self, m_d: Move_Detail, info, progress):
        if m_d.type == "move": # 盤上の駒が移動する場合
            self.stat_move[m_d.move_piece_str] += 1 # 動かした駒種の統計を更新
            self.piece_distribution.move_ban(m_d.pos, m_d.moved, m_d.move_piece_str, m_d.is_promote) # 駒の移動による駒割変更


            if m_d.move_piece_str == "K": # 先手玉移動
                self.pass_of_K.append(m_d.moved) # 移動したので移動先の座標を追加する
            else:
                self.pass_of_K.append(self.pass_of_K[-1]) # 移動していないので末尾をそのまま追加する
            if m_d.move_piece_str == "k": # 後手玉移動
                self.pass_of_k.append(m_d.moved) # 移動したので移動先の座標を追加する
            else:
                self.pass_of_k.append(self.pass_of_k[-1]) # 移動していないので末尾をそのまま追加する

            if self.pass_of_R_flag: # 先手飛の移動記録中
                if m_d.move_piece_str == "R": # 先手飛移動
                    self.pass_of_R.append(m_d.moved) # 移動したので移動先の座標を追加する
                    if m_d.is_promote: # 成りが入ると記録を中止する
                        self.pass_of_R_flag = False
                else:
                    self.pass_of_R.append(self.pass_of_R[-1]) # 移動していないので末尾をそのまま追加する
            if self.pass_of_r_flag: # 後手飛の移動記録中
                if m_d.move_piece_str == "r": # 後手飛移動
                    self.pass_of_r.append(m_d.moved) # 移動したので移動先の座標を追加する
                    if m_d.is_promote: # 成りが入ると記録を中止する
                        self.pass_of_r_flag = False
                else:
                    self.pass_of_r.append(self.pass_of_r[-1]) # 移動していないので末尾をそのまま追加する

            if m_d.get_piece_str == "r": # 後手が飛を得た=先手の駒であった飛が盤上から消えたということ
                self.pass_of_R_flag = False
            if m_d.get_piece_str == "R": # 先手が飛を得た=後手の駒であった飛が盤上から消えたということ
                self.pass_of_r_flag = False

            if m_d.get_piece_str: # 駒を捕捉した場合の駒割更新
                self.piece_distribution.move_get_piece(m_d.pos, m_d.get_piece_origin_str, m_d.get_piece_str, m_d.get_piece_promoted)

            if m_d.is_promote: # 指し手が成りの場合
                if self.nowBoard.get_teban() == "w": # 現局面が後手なら直前の指し手は先手のもの
                    self.stat_promote_b += 1 # 先手の成りの数を1増やす
                else: # 後手の指し手
                    self.stat_promote_w += 1 # 後手の成りの数を1増やす

        elif m_d.type == "place": # 駒を打つ場合
            if self.nowBoard.get_teban() == "w": # 現局面が後手なら直前の指し手は先手のもの
                self.stat_move['*_b'] += 1 # 動かした駒種の統計を更新
                self.piece_distribution.move_place(m_d.moved, m_d.move_piece_str.upper())
            else: # 後手の指し手
                self.stat_move['*_w'] += 1 # 動かした駒種の統計を更新
                self.piece_distribution.move_place(m_d.moved, m_d.move_piece_str.lower())

        if info: # infoは送られるなら常に送られることが前提
            self.stat_score_val.append(info.get_score_val()) # 評価値を追加する
        else: # infoが無かった場合は前の評価値を流用することで代用
            if len(self.stat_score_val) <= 2:
                self.stat_score_val.append(0)
            else:
                self.stat_score_val.append(self.stat_score_val[-2])

        if progress:
            self.stat_progress.append(progress) # 進行度を追加する

        self.stat_piece_distribution.add(self.piece_distribution) # 駒割の統計更新

    def print_kifu_option(self):
        if self.kifu_option:
            b = self.kifu_option["black_name"]
            w = self.kifu_option["white_name"]
            teai = self.kifu_option["teai"]
            print(f"☗{b} VS ☖{w}")
            print(f"手合い： {teai}")

    # 統計情報
    def __stat_result(self): # 勝敗を表示
        if self.result == "win":
            print("先手の勝ちです")
        elif self.result == "lose":
            print("後手の勝ちです")
        elif self.result == "draw":
            print("引き分けです")
        else:
            print("無勝負です")
    def __stat_center_of_K(self): # 先手玉の重心
        return calc_center(self.pass_of_K)
    def __stat_center_of_k(self): # 後手玉の重心
        return calc_center(self.pass_of_k)
    def __stat_mode_of_K(self): # 先手玉の最頻値
        return Counter(self.pass_of_K).most_common(1)[0][0]
    def __stat_mode_of_k(self): # 後手玉の最頻値
        return Counter(self.pass_of_k).most_common(1)[0][0]
    def __stat_center_of_R(self): # 先手飛の重心
        return calc_center(self.pass_of_R)
    def __stat_center_of_r(self): # 後手飛の重心
        return calc_center(self.pass_of_r)
    def __stat_mode_of_R(self): # 先手飛の最頻値
        return Counter(self.pass_of_R).most_common(1)[0][0]
    def __stat_mode_of_r(self): # 後手飛の最頻値
        return Counter(self.pass_of_r).most_common(1)[0][0]
    def calc_score_val(self):
        normal_score_val = self.stat_score_val # 通常の評価値リスト
        reverse_score_val = [x if i%2 == 0 else -x for (i, x) in enumerate(normal_score_val)] # 後手の評価値を反転して先手から見たものに
        black_score_val = normal_score_val[0::2] # 先手の評価値だけを切り出したもの
        white_score_val = normal_score_val[1::2] # 後手の評価値だけを切り出したもの
        # 先後のエンジンの評価値の差
        if len(black_score_val) == len(white_score_val):
            diff_score_val = np.array(black_score_val) + np.array(white_score_val)
        else:
            diff_score_val = np.array(black_score_val[:-1]) + np.array(white_score_val)
        self.normal_score_val = normal_score_val
        self.reverse_score_val = reverse_score_val
        self.black_score_val = black_score_val
        self.white_score_val = white_score_val
        self.diff_score_val = diff_score_val

    def __stat_score_val(self): # 評価値の統計情報表示
        if len(self.stat_score_val) <= 2: # 評価値情報がない
            return False
        self.calc_score_val()
        if self.result == "win": # 先手勝ちの場合
            win_min_val = min(self.black_score_val)
            lose_max_val = max(self.white_score_val)
        elif self.result == "lose": # 後手勝ちの場合
            win_min_val = min(self.white_score_val)
            lose_max_val = max(self.black_score_val)
        else:
            return True # calc_score_val()は実行した
        print(f"勝った方の最小の評価値は{win_min_val}")
        print(f"負けた方の最大の評価値は{lose_max_val}")
        return True

    def stat(self):
        self.__stat_result()
        self.__stat_score_val()
        print(f"手数は{self.get_tesuu()}")
        print(f"先手玉の重心は{self.__stat_center_of_K()}")
        print(f"先手玉の最頻値は{self.__stat_mode_of_K()}")
        print(f"後手玉の重心は{self.__stat_center_of_k()}")
        print(f"後手玉の最頻値は{self.__stat_mode_of_k()}")
        print(f"先手飛の重心は{self.__stat_center_of_R()}")
        print(f"先手飛の最頻値は{self.__stat_mode_of_R()}")
        print(f"後手飛の重心は{self.__stat_center_of_r()}")
        print(f"後手飛の最頻値は{self.__stat_mode_of_r()}")
        print(f"先手の成りの回数は{self.stat_promote_b}")
        print(f"後手の成りの回数は{self.stat_promote_w}")


# usinewgame済のエンジンを与えると棋譜の現局面から対局を実行する。
# 対局終了後はisready状態に戻る。
def battle(black_engine, white_engine, kifu, progress_engine):
    think_time = 100
    while kifu.get_tesuu() <= 256:
        pos = kifu.get_sfen()
        progress = progress_engine.progress(pos)
        if kifu.nowBoard.get_teban() == "b":
            go_result = black_engine.go_think(pos, think_time)[1]
        else:
            go_result = white_engine.go_think(pos, think_time)[1]
        bestmove = go_result[0]
        if bestmove == "resign": # 投了
            black_engine.gameover()
            white_engine.gameover()
            if kifu.nowBoard.get_teban() == "b": # 先手番(ここはまだ指し手が進んでいない)で投了なので先手負け
                kifu.gameover("lose")
            else: # 後手番で投了なので先手勝ち
                kifu.gameover("win")
            return kifu
        if bestmove == "win": # 宣言勝ち
            black_engine.gameover()
            white_engine.gameover()
            if kifu.nowBoard.get_teban() == "b": # 先手番(ここはまだ指し手が進んでいない)で宣言勝ちなので先手勝ち
                kifu.gameover("win")
            else: # 後手番で宣言勝ちなので先手負け
                kifu.gameover("lose")
            return kifu
        info_list = go_result[1]
        info = info_list[-1] if len(info_list) >= 1 else None # 最新のinfoだけを抽出(あれば)
        kifu.move(bestmove, info, progress)

    # 256手超えで引き分け
    black_engine.gameover()
    white_engine.gameover()
    kifu.gameover("draw")
    return kifu
