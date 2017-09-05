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
        if not (self.b_update or self.w_update):  # 先手銀、後手銀の両方が更新不要なら全体の更新フラグも落とす
            self.update = False

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


class RightGoldMethod(SenkeiPartsBase):
    """角換わりの右金を規定する"""
    def __init__(self):
        super().__init__()
        self.state = True  # 正常形かどうか
        self.stay = True  # そのままの状態
        self.update = True
        self.b_update = True  # 先手金更新フラグ
        self.b_pos = (4, 9)
        self.w_update = True  # 後手金更新フラグ
        self.w_pos = (6, 1)

    def move(self, m_d: Move_Detail):
        if not self.update:
            return
        if m_d.type == "place":  # 駒を打ったならスルー
            return
        if self.b_update and m_d.move_piece_str == "G":  # 先手の金を動かした
            if m_d.pos == (4, 9):  # 居金解消
                self.stay = False
                self.b_pos = m_d.moved
                if m_d.moved == (4, 8):  # 48金
                    self.b_update = False
                elif m_d.moved == (5, 8):  # 58金
                    self.b_update = False
                else:  # 通常形でない
                    self.b_update = False
                    self.state = False
        elif self.w_update and m_d.move_piece_str == "g":  # 後手の金を動かした
            if m_d.pos == (6, 1):  # 居金解消
                self.stay = False
                self.w_pos = m_d.moved
                if m_d.moved == (6, 2):  # 62金
                    self.w_update = False
                elif m_d.moved == (5, 2):  # 52金
                    self.w_update = False
                else:  # 通常形でない
                    self.w_update = False
                    self.state = False
        if not (self.b_update or self.w_update):  # 先手金、後手金の両方が更新不要なら全体の更新フラグも落とす
            self.update = False

    def stat_str(self) -> List[str]:
        if not self.state:
            return ["右金が通常形でない"]
        result = []
        if self.b_pos == (4, 9):
            result.append("先手は49金")
        elif self.b_pos == (5, 8):
            result.append("先手は58金")
        elif self.b_pos == (4, 8):
            result.append("先手は48金")
        if self.w_pos == (6, 1):
            result.append("後手は61金")
        elif self.w_pos == (5, 2):
            result.append("後手は52金")
        elif self.w_pos == (6, 2):
            result.append("後手は62金")
        return result


class BishopExchange(SenkeiPartsBase):
    """角交換を規定する"""
    def __init__(self):
        super().__init__()
        self.state = True  # 正常形かどうか
        self.update = True
        self.is_exchange = False  # 角交換したか
        self.b_captured = False  # 先手が角を捕獲した
        self.w_captured = False  # 後手が角を捕獲した
        self.b_tezon = 0
        self.w_tezon = 0
        self.comment = []

    def move(self, m_d: Move_Detail):
        if not self.update:
            return
        if m_d.type == "place":  # 駒を打ったならスルー
            return
        if self.update:
            if self.w_captured:  # 先手が後手の角を取り返しに行く
                print("先手が後手の角を取り返しに行く")
                self.update = False
                if m_d.move_piece_str == "R":  # 先手が飛を動かした
                    self.is_exchange = True
                    self.comment.append("先手向かい飛車")
                elif m_d.move_piece_str == "G":  # 先手が金を動かした
                    print("先手が金を動かした")
                    self.b_tezon += 1
                    self.is_exchange = True
                    if m_d.moved == (8, 8):  # 78に戻るために手損することになる
                        self.comment.append("先手一手損角換わり")
                    elif m_d.moved == (7, 7):  # 77金型(阪田流)
                        self.comment.append("先手77金型")
                    else:
                        self.state = False
                elif m_d.move_piece_str == "S":  # 先手が銀を動かした
                    print("先手が銀を動かした")
                    self.update = False
                    self.is_exchange = True
                    if m_d.moved == (8, 8):  # 後手一手損
                        self.comment.append("一手損角換わり")
                    elif m_d.moved == (7, 7):  # 角換わり
                        self.comment.append("角換わり")
                    else:
                        self.state = False
                elif m_d.move_piece_str == "N":  # 先手が桂を動かした
                    self.update = False
                    self.is_exchange = True
                    self.comment.append("77桂")
                elif m_d.move_piece_str == "K":  # 先手が玉を動かした
                    self.update = False
                    self.is_exchange = True
                    self.comment.append("後手角交換振り飛車")
                else:  # 正常形でない
                    print("先手の動かす駒：正常形でない")
                    self.update = False
                    self.state = False

            elif self.b_captured:  # 後手が先手の角を取り返しに行く
                print("後手が先手の角を取り返しに行く")
                self.update = False
                if m_d.move_piece_str == "r":  # 後手が飛を動かした
                    self.is_exchange = True
                    self.comment.append("後手向かい飛車")
                elif m_d.move_piece_str == "g":  # 後手が金を動かした
                    print("後手が金を動かした")
                    self.w_tezon += 1
                    self.is_exchange = True
                    if m_d.moved == (2, 2):  # 32に戻るために手損することになる
                        self.comment.append("角換わり")
                    elif m_d.moved == (3, 3):  # 33金型(阪田流)
                        self.comment.append("後手33金型")
                    else:
                        self.state = False
                elif m_d.move_piece_str == "s":  # 後手が銀を動かした
                    print("後手が銀を動かした")
                    self.update = False
                    self.is_exchange = True
                    if m_d.moved == (2, 2):  # 先手一手損
                        self.comment.append("先手一手損角換わり")
                    elif m_d.moved == (3, 3):  # 角換わり
                        self.comment.append("角換わり")
                    else:
                        self.state = False
                elif m_d.move_piece_str == "n":  # 後手が桂を動かした
                    self.update = False
                    self.is_exchange = True
                    self.comment.append("33桂")
                elif m_d.move_piece_str == "k":  # 後手が玉を動かした
                    self.update = False
                    self.is_exchange = True
                    self.comment.append("先手角交換振り飛車")
                else:  # 正常形でない
                    print("後手の動かす駒：正常形でない")
                    self.update = False
                    self.state = False
            elif m_d.move_piece_str == "B":  # 先手の角を動かした
                print("先手の角を動かした")
                if not (m_d.moved == (7, 7) or m_d.moved == (3, 3) or m_d.moved == (2, 2)):  # 77、33、22以外に動くと通常形でない
                    print("77、33、22以外に動くと通常形でない")
                    self.state = False
                    self.update = False
                else:
                    self.b_tezon += 1
                    if m_d.get_piece_origin_str == "b":  # 後手の角を捕獲した
                        print("後手の角を捕獲した")
                        self.b_captured = True
            elif m_d.move_piece_str == "b":  # 後手の角を動かした
                print("後手の角を動かした")
                if not (m_d.moved == (3, 3) or m_d.moved == (7, 7) or m_d.moved == (8, 8)):  # 33、77、88以外に動くと通常形でない
                    print("33、77、88以外に動くと通常形でない")
                    self.state = False
                    self.update = False
                else:
                    self.w_tezon += 1
                    if m_d.get_piece_origin_str == "B":  # 先手の角を捕獲した
                        print("先手の角を捕獲した")
                        self.w_captured = True

    def stat_str(self) -> List[str]:
        if not self.state:
            return ["角交換の通常形でない"]
        tezon = self.b_tezon - self.w_tezon
        print(f"先手の手損は{tezon}")
        return self.comment


class Senkei:
    def __init__(self):
        self.edge_p36 = EdgeP36()
        self.right_silver_method = RightSilverMethod()
        self.right_gold_method = RightGoldMethod()
        self.bishop_exchange = BishopExchange()

    def move(self, m_d: Move_Detail):
        self.edge_p36.move(m_d)
        self.right_silver_method.move(m_d)
        self.right_gold_method.move(m_d)
        self.bishop_exchange.move(m_d)

    def print(self):
        for text in self.edge_p36.stat_str():
            print(text)
        for text in self.right_silver_method.stat_str():
            print(text)
        for text in self.right_gold_method.stat_str():
            print(text)
        for text in self.bishop_exchange.stat_str():
            print(text)
