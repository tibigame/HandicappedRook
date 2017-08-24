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
    def __init__(self):
        self.b_black_area = np.zeros(14, dtype=int)
        self.b_middle_area = np.zeros(14, dtype=int)
        self.b_white_area = np.zeros(14, dtype=int)
        self.b_komadai_area = np.zeros(14, dtype=int)
        self.w_black_area = np.zeros(14, dtype=int)
        self.w_middle_area = np.zeros(14, dtype=int)
        self.w_white_area = np.zeros(14, dtype=int)
        self.w_komadai_area = np.zeros(14, dtype=int)

    def get_black_piece_value(self): # 先手の駒価値を返す
        return np.sum((self.b_black_area + self.b_middle_area + self.b_white_area + self.b_komadai_area) * piece_value)

    def get_white_piece_value(self): # 後手の駒価値を返す
        return np.sum((self.w_black_area + self.w_middle_area + self.w_white_area + self.w_komadai_area) * piece_value)

    def get_black_piece_point(self): # 大駒5点、小駒1点とした先手の駒点数を返す
        return np.sum((self.b_black_area + self.b_middle_area + self.b_white_area + self.b_komadai_area) * piece_point)

    def get_white_piece_point(self): # 大駒5点、小駒1点とした後手の駒点数を返す
        return np.sum((self.w_black_area + self.w_middle_area + self.w_white_area + self.w_komadai_area) * piece_point)

    def get_black_nyugoku_point(self): # 大駒5点、小駒1点とした先手の駒点数(敵陣と駒台のみ)を返す
        return np.sum((self.b_white_area + self.b_komadai_area) * piece_point)

    def get_white_nyugoku_point(self): # 大駒5点、小駒1点とした後手の駒点数(敵陣と駒台のみ)を返す
        return np.sum((self.w_black_area + self.w_komadai_area) * piece_point)
