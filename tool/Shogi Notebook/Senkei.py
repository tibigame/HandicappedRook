from typing import List
from abc import ABCMeta, abstractmethod
from Board import Move_Detail


class SenkeiPartsBase(metaclass=ABCMeta):  # 戦型用の部分判定を行うクラスの基底クラス
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def move(self, m_d: Move_Detail):
        pass

    @abstractmethod
    def stat_str(self) -> List[str]:
        return [""]


class EdgeP36(SenkeiPartsBase):
    """端歩36景を表すクラス"""
    def __init__(self):
        super().__init__()
        self.update = True  # 更新フラグ
        self.one_update = True  # 1筋更新フラグ
        self.nine_update = True  # 9筋更新フラグ
        self.b_1 = 7
        self.b_9 = 7
        self.w_1 = 3
        self.w_9 = 3

    def move(self, m_d: Move_Detail):
        if not self.update:
            return
        if m_d.type == "place":  # 駒を打ったならスルー
            return
        if self.one_update:  # 1筋のチェック
            if m_d.move_piece_str == "P":  # 先手の歩を動かした
                if m_d.pos == (1, 7):  # 16歩と突いた
                    self.b_1 = 6
                    if self.w_1 == 4:  # 14歩なら更新停止
                        self.one_update = False
                elif m_d.pos == (1, 6):  # 15歩と突いた
                    self.b_1 = 5
                    self.one_update = False
            elif m_d.move_piece_str == "p":  # 後手の歩を動かした
                if m_d.pos == (1, 3):  # 14歩と突いた
                    self.w_1 = 4
                    if self.b_1 == 6:  # 16歩なら更新停止
                        self.one_update = False
                elif m_d.pos == (1, 4):  # 15歩と突いた
                    self.w_1 = 5
                    self.one_update = False
        if self.nine_update:  # 9筋のチェック
            if m_d.move_piece_str == "P":  # 先手の歩を動かした
                if m_d.pos == (9, 7):  # 96歩と突いた
                    self.b_9 = 6
                    if self.w_9 == 4:  # 94歩なら更新停止
                        self.nine_update = False
                elif m_d.pos == (9, 6):  # 95歩と突いた
                    self.b_9 = 5
                    self.nine_update = False
            elif m_d.move_piece_str == "p":  # 後手の歩を動かした
                if m_d.pos == (9, 3):  # 94歩と突いた
                    self.w_9 = 4
                    if self.b_9 == 6:  # 96歩なら更新停止
                        self.nine_update = False
                elif m_d.pos == (9, 4):  # 95歩と突いた
                    self.w_9 = 5
                    self.nine_update = False
        if not (self.one_update or self.nine_update):  # 1筋9筋の両方が更新不要なら全体の更新フラグも落とす
            self.update = False

    def tezon(self) -> int:
        """先手から見て端に何手多く費やしているか"""
        b_tesuu = 14 - self.b_1 - self.b_9
        w_tesuu = -6 + self.w_1 + self.w_9
        return b_tesuu - w_tesuu

    def stat_str(self) -> List[str]:
        """端歩の状況の文字列を返す"""
        result = []
        if self.b_1 == 7 and self.w_1 == 3:
            result.append("1筋不突き")
        elif self.b_1 == 6 and self.w_1 == 3:
            result.append("1筋先手突き")
        elif self.b_1 == 7 and self.w_1 == 4:
            result.append("1筋後手突き")
        elif self.b_1 == 6 and self.w_1 == 4:
            result.append("1筋突き合い")
        elif self.b_1 == 5 and self.w_1 == 3:
            result.append("1筋先手突き越し")
        elif self.b_1 == 7 and self.w_1 == 5:
            result.append("1筋後手突き越し")
        if self.b_9 == 7 and self.w_9 == 3:
            result.append("9筋不突き")
        elif self.b_9 == 6 and self.w_9 == 3:
            result.append("9筋先手突き")
        elif self.b_9 == 7 and self.w_9 == 4:
            result.append("9筋後手突き")
        elif self.b_9 == 6 and self.w_9 == 4:
            result.append("9筋突き合い")
        elif self.b_9 == 5 and self.w_9 == 3:
            result.append("9筋先手突き越し")
        elif self.b_9 == 7 and self.w_9 == 5:
            result.append("9筋後手突き越し")
        return result


class RightSilverMethod(SenkeiPartsBase):
    """相居飛車の右銀を規定する"""
    def __init__(self):
        super().__init__()
        self.state = True  # 正常形かどうか
        self.stay = True  # そのままの状態
        self.update = True
        self.b_update = True  # 先手銀更新フラグ
        self.b_pos = (3, 9)
        self.w_update = True  # 後手銀更新フラグ
        self.w_pos = (7, 1)

    def move(self, m_d: Move_Detail):
        if not self.update:
            return
        if m_d.type == "place":  # 駒を打ったならスルー
            return
        if self.b_update and m_d.move_piece_str == "S":  # 先手の銀を動かした
            if m_d.pos == (3, 9):  # 居銀解消
                self.stay = False
                self.b_pos = m_d.moved
            elif m_d.pos == (4, 8) or m_d.pos == (3, 8) or m_d.pos == (2, 8):  # 銀を2段目から移動
                self.b_pos = m_d.moved
                if m_d.moved == (5, 7):  # 57銀確定
                    self.b_update = False
                elif m_d.moved == (4, 7):  # 腰掛銀 or 鎖鎌銀
                    pass
                elif m_d.moved == (3, 7):  # 早繰り銀 or 棒銀
                    pass
                elif m_d.moved == (2, 7):  # 棒銀確定
                    self.b_update = False
                else:  # 通常形でない
                    self.b_update = False
                    self.state = False
            elif m_d.pos == (4, 7) or m_d.pos == (3, 7):  # 銀を3段目から移動
                self.b_pos = m_d.moved
                if m_d.moved == (5, 6):  # 腰掛銀確定
                    self.b_update = False
                elif m_d.moved == (4, 6):  # 早繰り銀
                    self.b_update = False
                elif m_d.moved == (3, 6):  # 鎖鎌銀
                    self.b_update = False
                elif m_d.moved == (2, 6):  # 棒銀
                    self.b_update = False
                else:  # 通常形でない
                    self.b_update = False
                    self.state = False
        if not (self.b_update or self.w_update):  # 先手銀、後手銀の両方が更新不要なら全体の更新フラグも落とす
            self.update = False

        elif self.w_update and m_d.move_piece_str == "s":  # 後手の銀を動かした
            if m_d.pos == (7, 1):  # 居銀解消
                self.stay = False
                self.w_pos = m_d.moved
            elif m_d.pos == (6, 2) or m_d.pos == (7, 2) or m_d.pos == (8, 2):  # 銀を2段目から移動
                self.w_pos = m_d.moved
                if m_d.moved == (5, 3):  # 53銀確定
                    self.w_update = False
                elif m_d.moved == (6, 3):  # 腰掛銀 or 鎖鎌銀
                    pass
                elif m_d.moved == (7, 3):  # 早繰り銀 or 棒銀
                    pass
                elif m_d.moved == (8, 3):  # 棒銀確定
                    self.w_update = False
                else:  # 通常形でない
                    self.w_update = False
                    self.state = False
            elif m_d.pos == (6, 3) or m_d.pos == (7, 3):  # 銀を3段目から移動
                self.w_pos = m_d.moved
                if m_d.moved == (5, 4):  # 腰掛銀確定
                    self.w_update = False
                elif m_d.moved == (6, 4):  # 早繰り銀
                    self.w_update = False
                elif m_d.moved == (7, 4):  # 鎖鎌銀
                    self.w_update = False
                elif m_d.moved == (8, 4):  # 棒銀
                    self.w_update = False
                else:  # 通常形でない
                    self.w_update = False
                    self.state = False

    def stat_str(self) -> List[str]:
        if not self.state:
            return ["右銀が通常形でない"]

        result = []
        if self.b_pos == (3, 9):
            result.append("先手は39銀")
        elif self.b_pos == (2, 6) or self.b_pos == (2, 7):
            result.append("先手は棒銀")
        elif self.b_pos == (4, 6):
            result.append("先手は早繰り銀")
        elif self.b_pos == (3, 6):
            result.append("先手は鎖鎌銀")
        elif self.b_pos == (5, 6) or self.b_pos == (4, 7):
            result.append("先手は腰掛銀")
        elif self.b_pos == (5, 7):
            result.append("先手は57銀")
        elif self.b_pos == (2, 8):
            result.append("先手は28銀")
        elif self.b_pos == (3, 8):
            result.append("先手は38銀")
        elif self.b_pos == (4, 8):
            result.append("先手は48銀")
        if self.w_pos == (7, 1):
            result.append("後手は71銀")
        elif self.w_pos == (8, 4) or self.w_pos == (8, 3):
            result.append("後手は棒銀")
        elif self.w_pos == (6, 4):
            result.append("後手は早繰り銀")
        elif self.w_pos == (7, 4):
            result.append("後手は鎖鎌銀")
        elif self.w_pos == (5, 4) or self.w_pos == (6, 3):
            result.append("後手は腰掛銀")
        elif self.w_pos == (5, 3):
            result.append("後手は53銀")
        elif self.w_pos == (8, 2):
            result.append("後手は82銀")
        elif self.w_pos == (7, 2):
            result.append("後手は72銀")
        elif self.w_pos == (6, 2):
            result.append("後手は62銀")

        return result


class Senkei:
    def __init__(self):
        self.edge_p36 = EdgeP36()
        self.right_silver_method = RightSilverMethod()

    def move(self, m_d: Move_Detail):
        self.edge_p36.move(m_d)
        self.right_silver_method.move(m_d)

    def print(self):
        r1 = self.edge_p36.stat_str()
        r2 = self.right_silver_method.stat_str()
        for text in r1:
            print(text)
        for text in r2:
            print(text)
