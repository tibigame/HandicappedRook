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

    def __set_Board(self, board, clear=False): # Boardクラスから駒位置の情報をセットします
        if clear: # フラグを与えることでここでも初期化できるようにしておく
            self.__clear()
        for i, p in enumerate(["K", "R", "B", "G", "S", "N", "L", "P", "+R", "+B", "+S", "+N", "+L", "+P",
                  "k", "r", "b", "g", "s", "n", "l", "p", "+r", "+b", "+s", "+n", "+l", "+p"]):
            self.__set_koma_pos(i, p, board.get_x_pos2(p))
        self.__set_koma_dict(board.koma)

    def __set_koma_pos(self, i, p, pos_list): # ループインデックス、駒種、駒位置リストから盤面駒位置の情報をセットします
        is_black = i < 14 # Trueなら先手の駒
        ndarray_pos = i % 14 # 14での剰余やndarray配列での代入位置になる
        if not pos_list: # 何もないときは空リストはではなく0が渡される
            return
        for (pos_x, pos_y) in pos_list: # y座標のみが代入する変数に影響する
            if pos_y <= 3: # white_area
                if is_black:
                    self.b_white_area[ndarray_pos] += 1
                else:
                    self.w_white_area[ndarray_pos] += 1
            elif pos_y <= 6: # middle_area
                if is_black:
                    self.b_middle_area[ndarray_pos] += 1
                else:
                    self.w_middle_area[ndarray_pos] += 1
            else: # black_area
                if is_black:
                    self.b_black_area[ndarray_pos] += 1
                else:
                    self.w_black_area[ndarray_pos] += 1

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
