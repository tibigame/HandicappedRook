from Board import Board
import numpy as np

# 順に玉飛角金銀桂香歩龍馬…の駒の価値(Ponanza参考値)を表す
piece_value = np.array(
    [0, 1087, 951, 567, 528, 416, 322, 93,
     1550, 1101, 582, 569, 567, 598]
)

# 順に玉飛角金銀桂香歩龍馬…の駒の点数を表す
piece_point = np.array(
    [0, 5, 5, 1, 1, 1, 1, 1, 5, 5, 1, 1, 1, 1]
)

nd_index = {
    "K": 0, "R": 1, "B": 2, "G": 3, "S": 4, "N": 5, "L": 6, "P": 7, "+R": 8, "+B": 9, "+S": 10, "+N": 11, "+L": 12, "+P": 13,
    "k": 0, "r": 1, "b": 2, "g": 3, "s": 4, "n": 5, "l": 6, "p": 7, "+r": 8, "+b": 9, "+s": 10, "+n": 11, "+l": 12, "+p": 13
}


class PieceDistribution:
    """駒割りを扱うクラス"""
    def __init__(self, board=None): # boardクラスを与えてここで全ての初期設定を行う
        self.__clear()
        if board:
            self.__set_Board(board)

    def __clear(self): # 0での初期化を行います
        self.b_black_area = np.zeros(14, dtype=int)
        self.b_middle_area = np.zeros(14, dtype=int)
        self.b_white_area = np.zeros(14, dtype=int)
        self.b_komadai_area = np.zeros(14, dtype=int)
        self.w_black_area = np.zeros(14, dtype=int)
        self.w_middle_area = np.zeros(14, dtype=int)
        self.w_white_area = np.zeros(14, dtype=int)
        self.w_komadai_area = np.zeros(14, dtype=int)

    def __inc_val(self, pos, is_black=True, val=1, p=None, ndarray_index=-1):
        pos_y = pos[1] # y座標のみが代入する変数に影響する
        n_index = ndarray_index if ndarray_index >= 0 else nd_index[p] # ndarray_indexがあればそれを、なければ駒種から計算する
        if pos_y <= 3:  # white_area
            if is_black:
                self.b_white_area[n_index] += val
            else:
                self.w_white_area[n_index] += val
        elif pos_y <= 6:  # middle_area
            if is_black:
                self.b_middle_area[n_index] += val
            else:
                self.w_middle_area[n_index] += val
        else:  # black_area
            if is_black:
                self.b_black_area[n_index] += val
            else:
                self.w_black_area[n_index] += val

    def __set_Board(self, board, clear=False): # Boardクラスから駒位置の情報をセットします
        if clear: # フラグを与えることでここでも初期化できるようにしておく
            self.__clear()
        for i, p in enumerate(["K", "R", "B", "G", "S", "N", "L", "P", "+R", "+B", "+S", "+N", "+L", "+P",
                  "k", "r", "b", "g", "s", "n", "l", "p", "+r", "+b", "+s", "+n", "+l", "+p"]):
            self.__set_koma_pos(i, p, board.get_x_pos2(p))
        self.__set_koma_dict(board.koma)

    def __set_koma_pos(self, i, p, pos_list): # ループインデックス、駒種、駒位置リストから盤面駒位置の情報をセットします
        if not pos_list: # 何もないときは空リストはではなく0が渡される
            return
        for pos in pos_list:
            self.__inc_val(pos, is_black=i < 14, val=1, p=p, ndarray_index=i % 14)

    def __set_koma_dict(self, koma_dict): # 駒台の辞書からクラス変数に値をセットします
        self.b_komadai_area[1] = koma_dict["R"]
        self.b_komadai_area[2] = koma_dict["B"]
        self.b_komadai_area[3] = koma_dict["G"]
        self.b_komadai_area[4] = koma_dict["S"]
        self.b_komadai_area[5] = koma_dict["N"]
        self.b_komadai_area[6] = koma_dict["L"]
        self.b_komadai_area[7] = koma_dict["P"]
        self.w_komadai_area[1] = koma_dict["r"]
        self.w_komadai_area[2] = koma_dict["b"]
        self.w_komadai_area[3] = koma_dict["g"]
        self.w_komadai_area[4] = koma_dict["s"]
        self.w_komadai_area[5] = koma_dict["n"]
        self.w_komadai_area[6] = koma_dict["l"]
        self.w_komadai_area[7] = koma_dict["p"]

    def move_ban(self, pos, moved, move_piece_str, is_promote): # 盤上から盤上へ動く
        self.__inc_val(pos, is_black=move_piece_str[-1].isupper(), val=-1, p=move_piece_str)
        moved_p = "+" + move_piece_str if is_promote else move_piece_str
        self.__inc_val(moved, is_black=move_piece_str[-1].isupper(), val=1, p=moved_p)

    def move_get_piece(self, pos, captured_piece_str, get_piece_str, is_promoted): # 捕獲されて盤上から駒が消え、駒台の駒を増やす
        p = "+" + captured_piece_str if is_promoted else captured_piece_str
        self.__inc_val(pos, is_black=captured_piece_str[-1].isupper(), val=-1, p=p)
        if get_piece_str.isupper():
            self.b_komadai_area[nd_index[get_piece_str]] += 1
        else:
            self.w_komadai_area[nd_index[get_piece_str]] += 1

    def move_place(self, moved, move_piece_str): # 駒台の駒を減らして、駒台から盤上へ置く
        if move_piece_str.isupper():
            self.b_komadai_area[nd_index[move_piece_str]] -= 1
        else:
            self.w_komadai_area[nd_index[move_piece_str]] -= 1
        self.__inc_val(moved, is_black=move_piece_str.isupper(), val=1, p=move_piece_str)

    def get_black_piece_value(self): # 先手の駒価値を返す
        return np.sum((self.b_black_area + self.b_middle_area + self.b_white_area + self.b_komadai_area) * piece_value)

    def get_white_piece_value(self): # 後手の駒価値を返す
        return np.sum((self.w_black_area + self.w_middle_area + self.w_white_area + self.w_komadai_area) * piece_value)

    def get_diff_piece_value(self): # 先手の駒価値が後手の駒価値よりどれだけ大きいかを返す
        return self.get_black_piece_value() - self.get_white_piece_value()

    def get_black_piece_point(self): # 大駒5点、小駒1点とした先手の駒点数を返す
        return np.sum((self.b_black_area + self.b_middle_area + self.b_white_area + self.b_komadai_area) * piece_point)

    def get_white_piece_point(self): # 大駒5点、小駒1点とした後手の駒点数を返す
        return np.sum((self.w_black_area + self.w_middle_area + self.w_white_area + self.w_komadai_area) * piece_point)

    def get_black_nyugoku_point(self): # 大駒5点、小駒1点とした先手の駒点数(敵陣と駒台のみ)を返す
        return np.sum((self.b_white_area + self.b_komadai_area) * piece_point)

    def get_white_nyugoku_point(self): # 大駒5点、小駒1点とした後手の駒点数(敵陣と駒台のみ)を返す
        return np.sum((self.w_black_area + self.w_komadai_area) * piece_point)
