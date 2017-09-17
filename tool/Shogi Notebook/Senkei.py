from typing import List
from typing import Tuple
from typing import Set
from abc import ABCMeta, abstractmethod
from Board import Move_Detail
from util import xor
from util import reverse_bw
from util import d_print


class SenkeiClassify:
    def __init__(self):
        self.kingdom = None  # kingdom 振り飛車とか
        self.phylum = None  # phylum 角換わりとか横歩取り
        self.subphylum = None  # subphylum 一手損角換わりとか
        self.order = None  # order 角換わり先手棒銀後手腰掛け銀とか矢倉▲４六銀△３七桂とか
        self.family = None  # family 宮田新手・Ponanza新手△３七銀とか
        self.forms = None  # forms 横歩取り▲１六歩△１四歩型とか


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

    def print(self):
        for text in self.stat_str():
            print(text)


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


class KingLeftCastle(SenkeiPartsBase):
    """先手の左側への囲いを規定する"""
    def __init__(self, debug=False, is_black=True):
        super().__init__()
        self.update = True
        self.is_black = is_black
        self.left_n = [self.reg_pos((8, 9))]  # 左桂
        self.left_s = [self.reg_pos((7, 9))]  # 左銀
        self.left_g = [self.reg_pos((6, 9))]  # 左金
        self.k = [self.reg_pos((5, 9))]  # 玉
        self.right_g = [self.reg_pos((4, 9))]  # 右金
        self.right_s = [self.reg_pos((3, 9))]  # 右銀
        self.p6 = False  # 6筋の歩
        self.s38_str = "38銀" if self.is_black else "72銀"
        self.castle_set = {  # 指し手を進めるたびに不要なものをセットから消していく方式
            "矢倉", "菊水矢倉", "雁木", "急戦矢倉", "右玉",
            "中原囲い", "中住まい", self.s38_str,
            "早囲い", "片矢倉", "Bonanza囲い",
            "舟囲い", "elmo囲い", "ミレニアム",
            "左美濃", "天守閣美濃", "端玉銀冠", "銀冠", "銀冠穴熊", "穴熊", "松尾流穴熊", "4枚穴熊", "ビッグ4"
        }
        self.debug = debug

    def reg_pos(self, p: Tuple[int, int]):
        return reverse_bw(p, self.is_black)

    # デバッグプリント用
    def __dprint(self, string: str):
        d_print(string, is_debug=self.debug)

    def move(self, m_d: Move_Detail):
        if not self.update:
            return
        if m_d.type == "place":  # 駒を打ったならスルー
            return
        if self.is_black:
            is_move_p = m_d.move_piece_str == "P"
            is_move_n = m_d.move_piece_str == "N"
            is_move_s = m_d.move_piece_str == "S"
            is_move_g = m_d.move_piece_str == "G"
            is_move_k = m_d.move_piece_str == "K"
        else:
            is_move_p = m_d.move_piece_str == "p"
            is_move_n = m_d.move_piece_str == "n"
            is_move_s = m_d.move_piece_str == "s"
            is_move_g = m_d.move_piece_str == "g"
            is_move_k = m_d.move_piece_str == "k"

        if is_move_p and m_d.moved == self.reg_pos((6, 6)):  # 66歩の判定
            self.__dprint("先手66歩")
            self.castle_set -= {"急戦矢倉"}
            self.p6 = True
        elif is_move_n:  # 菊水矢倉かミレニアムの可能性
            if m_d.moved == self.reg_pos((7, 7)):  # 77桂だけを判定すればよい
                self.__dprint("先手77桂")
                self.castle_set -= {"矢倉", "早囲い", "片矢倉", "Bonanza囲い", "舟囲い", "elmo囲い",
                                    "穴熊", "銀冠穴熊", "松尾流穴熊", "4枚穴熊", "ビッグ4"}
                self.left_n.append(m_d.moved)
        elif is_move_s:  # 左銀か右銀かを分離する
            if m_d.pos == self.left_s[-1]:  # 左銀の現在位置は記録してある
                if m_d.moved == self.reg_pos((8, 8)):  # 88銀の場合 (穴熊のハッチを閉める or 矢倉か銀冠の途中)
                    if self.k[-1] == self.reg_pos((9, 9)):
                        self.castle_set &= {"穴熊", "銀冠穴熊", "松尾流穴熊", "4枚穴熊", "ビッグ4"}
                    else:  # 左美濃と雁木が消える
                        self.castle_set -= {"雁木", "左美濃", "天守閣美濃", "舟囲い", "elmo囲い"}
                elif m_d.moved == self.reg_pos((7, 8)):  # 78銀の場合 (左美濃 or 矢倉か銀冠の途中)
                    self.castle_set -= {"穴熊", "松尾流穴熊", "舟囲い", "elmo囲い"}
                elif m_d.moved == self.reg_pos((6, 8)):  # 68銀の場合 (矢倉の途中 or カニ囲い or elmo囲い)
                    self.castle_set &= {"矢倉", "雁木", "急戦矢倉", "早囲い", "片矢倉", "Bonanza囲い", "右玉", "elmo囲い"}
                elif m_d.moved == self.reg_pos((8, 7)):  # 87銀の場合 (銀冠)
                    self.castle_set &= {"端玉銀冠", "銀冠", "銀冠穴熊", "4枚穴熊", "ビッグ4", "右玉"}
                elif m_d.moved == self.reg_pos((7, 7)):  # 77銀の場合 (矢倉)
                    self.castle_set &= {"矢倉", "急戦矢倉", "右玉", "早囲い", "片矢倉", "Bonanza囲い"}
                elif m_d.moved == self.reg_pos((6, 7)):  # 67銀の場合 (雁木)
                    self.castle_set &= {"雁木", "右玉"}
                elif m_d.moved == self.reg_pos((6, 6)):  # 66銀の場合 (急戦矢倉)
                    self.castle_set &= {"急戦矢倉", "右玉"}
                self.left_s.append(m_d.moved)
            else:  # 右銀
                if m_d.moved == self.reg_pos((7, 7)):  # 77銀の場合 (4枚穴熊、ビッグ4、4枚左美濃)
                    self.castle_set &= {"4枚穴熊", "ビッグ4", "左美濃", "天守閣美濃", "端玉銀冠", "銀冠"}
                elif m_d.moved == self.reg_pos((7, 9)):  # 79銀の場合 (松尾流穴熊)
                    self.castle_set &= {"松尾流穴熊"}
                self.right_s.append(m_d.moved)
        elif is_move_g:  # 左金か右金かを分離する
            if m_d.pos == self.left_g[-1]:  # 左金の現在位置は記録してある
                if m_d.moved == self.reg_pos((7, 8)):  # 78金の場合 (通常系：矢倉、雁木、銀冠、穴熊など)
                    self.castle_set -= {"早囲い", "片矢倉", "Bonanza囲い", "舟囲い", "elmo囲い", "左美濃", "天守閣美濃"}
                elif m_d.moved == self.reg_pos((6, 8)):  # 68金の場合 (片矢倉、Bonanza囲い)
                    self.castle_set &= {"急戦矢倉", "右玉", "片矢倉", "Bonanza囲い"}
                elif m_d.moved == self.reg_pos((7, 9)):  # 79金の場合 (穴熊、elmo囲い)
                    self.castle_set &= {"elmo囲い", "銀冠穴熊", "穴熊", "4枚穴熊", "ビッグ4"}
                elif m_d.moved == self.reg_pos((8, 8)):  # 88金の場合 (おそらく銀冠穴熊)
                    self.castle_set &= {"銀冠穴熊", "4枚穴熊", "ビッグ4"}
                elif self.reg_pos(m_d.moved)[0] <= 5:  # 5筋より右なら無視
                    self.castle_set &= set()
                self.left_g.append(m_d.moved)
            else:  # 右金
                if m_d.moved == self.reg_pos((5, 8)):  # 58金の場合 (通常系)
                    self.castle_set -= {"中原囲い", "中住まい", self.s38_str}
                elif m_d.moved == self.reg_pos((5, 9)):  # 59金の場合 (穴熊 or 中原囲い)
                    self.castle_set &= {"中原囲い", "銀冠穴熊", "穴熊", "4枚穴熊", "ビッグ4", "松尾流穴熊"}
                elif m_d.moved == self.reg_pos((4, 8)):  # 48金
                    pass
                elif m_d.moved == self.reg_pos((3, 8)):  # 38金
                    self.castle_set &= {"中住まい"}
                elif self.reg_pos(m_d.moved)[0] <= 4:  # 4筋より右なら無視
                    self.castle_set = set()
                elif m_d.moved == self.reg_pos((6, 7)):  # 67金の場合 (矢倉 or 左美濃系 or 銀冠)
                    self.castle_set -= {"雁木", "急戦矢倉", "右玉", "Bonanza囲い", "舟囲い", "elmo囲い"}
                elif m_d.moved == self.reg_pos((6, 8)):  # 68金の場合 (角交換系が多いが他で判断する)
                    self.castle_set -= {"右玉"}
                elif self.reg_pos(m_d.moved)[0] >= 7:  # 7筋より左ならおそらく穴熊系
                    pass
                self.right_g.append(m_d.moved)
        elif is_move_k:
            if m_d.moved == self.reg_pos((5, 8)):  # 58玉の場合 (中住まい、中原囲い)
                self.castle_set &= {"中原囲い", "中住まい", self.s38_str}
            elif m_d.moved == self.reg_pos((6, 8)):  # 68玉の場合 (矢倉だと早囲いの可能性、舟囲い系)
                self.castle_set -= {"右玉", "中原囲い", "中住まい", self.s38_str}
            elif m_d.moved == self.reg_pos((6, 9)):  # 69玉の場合 (おそらく78金が入っている：矢倉、雁木の通常系、中原囲い)
                self.castle_set -= {"右玉", "中住まい", self.s38_str, "早囲い", "片矢倉", "Bonanza囲い",
                                    "舟囲い", "elmo囲い", "左美濃", "天守閣美濃"}
            elif m_d.moved == self.reg_pos((7, 8)):  # 78玉の場合 (矢倉だと早囲いの可能性、舟囲い系)
                self.castle_set -= {"中原囲い"}
            elif m_d.moved == self.reg_pos((8, 7)):  # 87玉の場合 (天守閣美濃)
                self.castle_set = {"左美濃", "天守閣美濃", "端玉銀冠", "銀冠", "銀冠穴熊", "4枚穴熊", "ビッグ4"}
            elif m_d.moved == self.reg_pos((9, 8)):  # 98玉の場合 (端玉→銀冠かどうかのチェックをする)
                self.castle_set = {"端玉銀冠"}
            elif m_d.moved == self.reg_pos((7, 9)):  # 79玉の場合 (通常系)
                self.castle_set -= {"中原囲い", "早囲い", "片矢倉", "Bonanza囲い",
                                    "舟囲い", "elmo囲い", "天守閣美濃", "端玉銀冠", "穴熊", "松尾流穴熊"}
            elif m_d.moved == self.reg_pos((8, 8)):  # 88玉の場合 (通常系) (88玉のelmo囲いは連盟左美濃)
                self.castle_set -= {"天守閣美濃", "端玉銀冠", "菊水矢倉", "ミレニアム",
                                    "舟囲い", "片矢倉", "Bonanza囲い"}
            elif m_d.moved == self.reg_pos((8, 9)):  # 88玉の場合 (ミレニアムか菊水矢倉)
                self.castle_set = {"菊水矢倉", "ミレニアム"}
            elif m_d.moved == self.reg_pos((9, 9)):  # 99玉の場合 (穴熊)
                self.castle_set = {"銀冠穴熊", "穴熊", "松尾流穴熊", "4枚穴熊", "ビッグ4"}
            elif self.reg_pos(m_d.moved)[0] <= 4:  # 4筋より右なら無視
                self.castle_set &= {"右玉"}
            self.k.append(m_d.moved)

    def deep_check(self, castle_type: str) -> bool:
        valid_flag = True
        if castle_type == "松尾流穴熊":
            if self.k[-1] != self.reg_pos((9, 9)):
                self.__dprint(f"[{castle_type}]: 玉が{self.reg_pos((9, 9))}でない")
                valid_flag = False
            if self.left_s[-1] != self.reg_pos((8, 8)):
                self.__dprint(f"[{castle_type}]: 左銀が{self.reg_pos((8, 8))}でない")
                valid_flag = False
            if self.right_s[-1] != self.reg_pos((7, 9)):
                self.__dprint(f"[{castle_type}]: 右銀が{self.reg_pos((7, 9))}でない")
                valid_flag = False
            if self.left_g[-1] != self.reg_pos((7, 8)):
                self.__dprint(f"[{castle_type}]: 左金が{self.reg_pos((7, 8))}でない")
                valid_flag = False
            if self.left_n[-1] != self.reg_pos((8, 9)):
                self.__dprint(f"[{castle_type}]: 左桂が{self.reg_pos((8, 9))}でない")
                valid_flag = False
            self.__dprint(f"[{castle_type}]: check passed")
        elif castle_type == "ビッグ4":
            if self.k[-1] != self.reg_pos((9, 9)):
                self.__dprint(f"[{castle_type}]: 玉が{self.reg_pos((9, 9))}でない")
                valid_flag = False
            if self.left_s[-1] != self.reg_pos((8, 7)):
                self.__dprint(f"[{castle_type}]: 左銀が{self.reg_pos((8, 7))}でない")
                valid_flag = False
            if self.right_s[-1] != self.reg_pos((7, 7)):
                self.__dprint(f"[{castle_type}]: 右銀が{self.reg_pos((7, 7))}でない")
                valid_flag = False
            if self.left_g[-1] != self.reg_pos((7, 8)) or self.left_g[-1] != self.reg_pos((8, 8)):
                self.__dprint(f"[{castle_type}]: 左金が{self.reg_pos((7, 8))}か{self.reg_pos((8, 8))}でない")
                valid_flag = False
            if self.right_g[-1] != self.reg_pos((7, 8)) or self.right_g[-1] != self.reg_pos((8, 8)):
                self.__dprint(f"[{castle_type}]: 右金が{self.reg_pos((7, 8))}か{self.reg_pos((8, 8))}でない")
                valid_flag = False
            if self.left_n[-1] != self.reg_pos((8, 9)):
                self.__dprint(f"[{castle_type}]: 左桂が{self.reg_pos((8, 9))}でない")
                valid_flag = False
            self.__dprint(f"[{castle_type}]: check passed")
        elif castle_type == "銀冠穴熊":
            if self.k[-1] != self.reg_pos((9, 9)):
                self.__dprint(f"[{castle_type}]: 玉が{self.reg_pos((9, 9))}でない")
                valid_flag = False
            if self.left_s[-1] != self.reg_pos((8, 7)):
                self.__dprint(f"[{castle_type}]: 左銀が{self.reg_pos((8, 7))}でない")
                valid_flag = False
            if self.left_g[-1] != self.reg_pos((7, 8)) or self.left_g[-1] != self.reg_pos((8, 8)):
                self.__dprint(f"[{castle_type}]: 左金が{self.reg_pos((7, 8))}か{self.reg_pos((8, 8))}でない")
                valid_flag = False
            if self.left_n[-1] != self.reg_pos((8, 9)):
                self.__dprint(f"[{castle_type}]: 左桂が{self.reg_pos((8, 9))}でない")
                valid_flag = False
            self.__dprint(f"[{castle_type}]: check passed")
        elif castle_type == "4枚穴熊":
            if self.k[-1] != self.reg_pos((9, 9)):
                self.__dprint(f"[{castle_type}]: 玉が{self.reg_pos((9, 9))}でない")
                valid_flag = False
            if self.reg_pos(self.left_s[-1]) <= 6:
                self.__dprint(f"[{castle_type}]: 左銀が左端から3筋までにない")
                valid_flag = False
            if self.reg_pos(self.right_s[-1]) <= 6:
                self.__dprint(f"[{castle_type}]: 右銀が左端から3筋までにない")
                valid_flag = False
            if self.reg_pos(self.left_g[-1]) <= 6:
                self.__dprint(f"[{castle_type}]: 左金が左端から3筋までにない")
                valid_flag = False
            if self.reg_pos(self.right_g[-1]) <= 6:
                self.__dprint(f"[{castle_type}]: 右金が左端から3筋までにない")
                valid_flag = False
            if self.left_n[-1] != self.reg_pos((8, 9)):
                self.__dprint(f"[{castle_type}]: 左桂が{self.reg_pos((8, 9))}でない")
                valid_flag = False
            self.__dprint(f"[{castle_type}]: check passed")
        elif castle_type == "穴熊":
            if self.k[-1] != self.reg_pos((9, 9)):
                self.__dprint(f"[{castle_type}]: 玉が{self.reg_pos((9, 9))}でない")
                valid_flag = False
            if self.reg_pos(self.left_s[-1]) <= 6:
                self.__dprint(f"[{castle_type}]: 左銀が左端から3筋までにない")
                valid_flag = False
            if self.reg_pos(self.left_g[-1]) <= 6:
                self.__dprint(f"[{castle_type}]: 左金が左端から3筋までにない")
                valid_flag = False
            if self.left_n[-1] != self.reg_pos((8, 9)):
                self.__dprint(f"[{castle_type}]: 左桂が{self.reg_pos((8, 9))}でない")
                valid_flag = False
            self.__dprint(f"[{castle_type}]: check passed")
        elif castle_type == "ミレニアム":
            if self.k[-1] != self.reg_pos((8, 9)):
                self.__dprint(f"[{castle_type}]: 玉が{self.reg_pos((8, 9))}でない")
                valid_flag = False
            if self.reg_pos(self.left_s[-1]) <= 6:
                self.__dprint(f"[{castle_type}]: 左銀が左端から3筋までにない")
                valid_flag = False
            if self.reg_pos(self.left_g[-1]) <= 6:
                self.__dprint(f"[{castle_type}]: 左金が左端から3筋までにない")
                valid_flag = False
            if self.reg_pos(self.right_g[-1]) <= 5:
                self.__dprint(f"[{castle_type}]: 右金が左端から4筋までにない")
                valid_flag = False
            if self.left_n[-1] != self.reg_pos((7, 7)):
                self.__dprint(f"[{castle_type}]: 左桂が{self.reg_pos((7, 7))}でない")
                valid_flag = False
            self.__dprint(f"[{castle_type}]: check passed")
        elif castle_type == "菊水矢倉":
            if self.k[-1] != self.reg_pos((8, 9)):
                self.__dprint(f"[{castle_type}]: 玉が{self.reg_pos((8, 9))}でない")
                valid_flag = False
            if self.left_s[-1] != self.reg_pos((8, 8)):
                self.__dprint(f"[{castle_type}]: 左銀が{self.reg_pos((8, 8))}でない")
                valid_flag = False
            if self.left_g[-1] != self.reg_pos((7, 8)):
                self.__dprint(f"[{castle_type}]: 左金が{self.reg_pos((7, 8))}でない")
                valid_flag = False
            if self.right_g[-1] != self.reg_pos((6, 7)):
                self.__dprint(f"[{castle_type}]: 右金が{self.reg_pos((6, 7))}でない")
                valid_flag = False
            if self.left_n[-1] != self.reg_pos((7, 7)):
                self.__dprint(f"[{castle_type}]: 左桂が{self.reg_pos((7, 7))}でない")
                valid_flag = False
            self.__dprint(f"[{castle_type}]: check passed")
        elif castle_type == "端玉銀冠":
            if self.k[-1] != self.reg_pos((9, 8)):
                self.__dprint(f"[{castle_type}]: 玉が{self.reg_pos((9, 8))}でない")
                valid_flag = False
            if self.left_s[-1] != self.reg_pos((8, 7)):
                self.__dprint(f"[{castle_type}]: 左銀が{self.reg_pos((8, 7))}でない")
                valid_flag = False
            if self.left_g[-1] != self.reg_pos((7, 8)):
                self.__dprint(f"[{castle_type}]: 左金が{self.reg_pos((7, 8))}でない")
                valid_flag = False
            if self.reg_pos(self.right_g[-1]) <= 5:
                self.__dprint(f"[{castle_type}]: 右金が左端から4筋までにない")
                valid_flag = False
            self.__dprint(f"[{castle_type}]: check passed")
        elif castle_type == "天守閣美濃":
            if self.k[-1] != self.reg_pos((8, 7)):
                self.__dprint(f"[{castle_type}]: 玉が{self.reg_pos((8, 7))}でない")
                valid_flag = False
            if self.left_s[-1] != self.reg_pos((7, 8)):
                self.__dprint(f"[{castle_type}]: 左銀が{self.reg_pos((7, 8))}でない")
                valid_flag = False
            if self.left_g[-1] != self.reg_pos((6, 9)):
                self.__dprint(f"[{castle_type}]: 左金が{self.reg_pos((6, 9))}でない")
                valid_flag = False
            if self.reg_pos(self.right_g[-1]) <= 4:
                self.__dprint(f"[{castle_type}]: 右金が端から5筋までにない")
                valid_flag = False
            self.__dprint(f"[{castle_type}]: check passed")
        elif castle_type == "左美濃":
            if self.k[-1] != self.reg_pos((8, 8)) and self.k[-1] != self.reg_pos((7, 9)):
                self.__dprint(f"[{castle_type}]: 玉が{self.reg_pos((8, 8))}、{self.reg_pos((7, 9))}でない")
                valid_flag = False
            if self.left_s[-1] != self.reg_pos((7, 8)):
                self.__dprint(f"[{castle_type}]: 左銀が{self.reg_pos((7, 8))}でない")
                valid_flag = False
            if self.left_g[-1] != self.reg_pos((6, 9)):
                self.__dprint(f"[{castle_type}]: 左金が{self.reg_pos((6, 9))}でない")
                valid_flag = False
            self.__dprint(f"[{castle_type}]: check passed")
        elif castle_type == "銀冠":
            if self.k[-1] != self.reg_pos((8, 8)) and self.k[-1] != self.reg_pos((7, 9)):
                self.__dprint(f"[{castle_type}]: 玉が{self.reg_pos((8, 8))}、{self.reg_pos((7, 9))}でない")
                valid_flag = False
            if self.left_s[-1] != self.reg_pos((8, 7)):
                self.__dprint(f"[{castle_type}]: 左銀が{self.reg_pos((8, 7))}でない")
                valid_flag = False
            if self.left_g[-1] != self.reg_pos((7, 8)):
                self.__dprint(f"[{castle_type}]: 左金が{self.reg_pos((7, 8))}でない")
                valid_flag = False
            self.__dprint(f"[{castle_type}]: check passed")
        elif castle_type == "舟囲い":
            if self.k[-1] != self.reg_pos((7, 8)) and self.k[-1] != self.reg_pos((6, 8)):
                self.__dprint(f"[{castle_type}]: 玉が{self.reg_pos((7, 8))}、{self.reg_pos((6, 8))}でない")
                valid_flag = False
            self.__dprint(f"[{castle_type}]: check passed")
        elif castle_type == "elmo囲い":
            if self.k[-1] != self.reg_pos((8, 8)) and self.k[-1] != self.reg_pos((7, 8)):
                self.__dprint(f"[{castle_type}]: 玉が{self.reg_pos((8, 8))}、{self.reg_pos((7, 8))}でない")
                valid_flag = False
            if self.left_s[-1] != self.reg_pos((6, 8)):
                self.__dprint(f"[{castle_type}]: 左銀が{self.reg_pos((6, 8))}でない")
                valid_flag = False
            if self.left_g[-1] != self.reg_pos((7, 9)):
                self.__dprint(f"[{castle_type}]: 左金が{self.reg_pos((7, 9))}でない")
                valid_flag = False
            self.__dprint(f"[{castle_type}]: check passed")
        elif castle_type == "中住まい":
            if self.k[-1] != self.reg_pos((5, 8)):
                self.__dprint(f"[{castle_type}]: 玉が{self.reg_pos((5, 8))}でない")
                valid_flag = False
            if self.right_s[-1] != self.reg_pos((4, 8)):
                self.__dprint(f"[{castle_type}]: 右銀が{self.reg_pos((4, 8))}でない")
                valid_flag = False
            if self.right_g[-1] != self.reg_pos((3, 8)):
                self.__dprint(f"[{castle_type}]: 右金が{self.reg_pos((3, 8))}でない")
                valid_flag = False
            self.__dprint(f"[{castle_type}]: check passed")
        elif castle_type == self.s38_str:
            if self.k[-1] != self.reg_pos((5, 8)) and self.k[-1] != self.reg_pos((6, 8)):
                self.__dprint(f"[{castle_type}]: 玉が{self.reg_pos((5, 8))}、{self.reg_pos((6, 8))}でない")
                valid_flag = False
            if self.right_s[-1] != self.reg_pos((3, 8)) and self.right_s[-1] != self.reg_pos((4, 7)):
                self.__dprint(f"[{castle_type}]: 右銀が{self.reg_pos((3, 8))}、{self.reg_pos((4, 7))}でない")
                valid_flag = False
            if self.right_g[-1] != self.reg_pos((4, 9)) and self.right_g[-1] != self.reg_pos((5, 8)):
                self.__dprint(f"[{castle_type}]: 右金が{self.reg_pos((4, 9))}、{self.reg_pos((5, 8))}でない")
                valid_flag = False
            self.__dprint(f"[{castle_type}]: check passed")
        elif castle_type == "中原囲い":
            if self.k[-1] != self.reg_pos((5, 8)) and self.k[-1] != self.reg_pos((6, 9)):
                self.__dprint(f"[{castle_type}]: 玉が{self.reg_pos((5, 8))}、{self.reg_pos((6, 9))}でない")
                valid_flag = False
            if self.right_s[-1] != self.reg_pos((4, 8)):
                self.__dprint(f"[{castle_type}]: 右銀が{self.reg_pos((4, 8))}でない")
                valid_flag = False
            if self.right_g[-1] != self.reg_pos((5, 9)):
                self.__dprint(f"[{castle_type}]: 右金が{self.reg_pos((5, 9))}でない")
                valid_flag = False
            self.__dprint(f"[{castle_type}]: check passed")
        elif castle_type == "早囲い":
            if self.left_s[-1] != self.reg_pos((7, 7)):
                self.__dprint(f"[{castle_type}]: 左銀が{self.reg_pos((7, 7))}でない")
                valid_flag = False
            if self.left_g[-1] != self.reg_pos((6, 9)):
                self.__dprint(f"[{castle_type}]: 左金が{self.reg_pos((6, 9))}でない")
                valid_flag = False
            if self.right_g[-1] != self.reg_pos((6, 7)):
                self.__dprint(f"[{castle_type}]: 右金が{self.reg_pos((6, 7))}でない")
                valid_flag = False
            self.__dprint(f"[{castle_type}]: check passed")
        elif castle_type == "片矢倉":
            if self.k[-1] != self.reg_pos((7, 8)):
                self.__dprint(f"[{castle_type}]: 玉が{self.reg_pos((7, 8))}でない")
                valid_flag = False
            if self.left_s[-1] != self.reg_pos((7, 7)):
                self.__dprint(f"[{castle_type}]: 左銀が{self.reg_pos((7, 7))}でない")
                valid_flag = False
            if self.left_g[-1] != self.reg_pos((6, 8)):
                self.__dprint(f"[{castle_type}]: 左金が{self.reg_pos((6, 8))}でない")
                valid_flag = False
            if self.right_g[-1] != self.reg_pos((6, 7)):
                self.__dprint(f"[{castle_type}]: 右金が{self.reg_pos((6, 7))}でない")
                valid_flag = False
            self.__dprint(f"[{castle_type}]: check passed")
        elif castle_type == "Bonanza囲い":
            if self.k[-1] != self.reg_pos((7, 8)):
                self.__dprint(f"[{castle_type}]: 玉が{self.reg_pos((7, 8))}でない")
                valid_flag = False
            if self.left_s[-1] != self.reg_pos((7, 7)):
                self.__dprint(f"[{castle_type}]: 左銀が{self.reg_pos((7, 7))}でない")
                valid_flag = False
            if self.left_g[-1] != self.reg_pos((6, 8)):
                self.__dprint(f"[{castle_type}]: 左金が{self.reg_pos((6, 8))}でない")
                valid_flag = False
            if self.right_g[-1] != self.reg_pos((5, 8)):
                self.__dprint(f"[{castle_type}]: 右金が{self.reg_pos((5, 8))}でない")
                valid_flag = False
            self.__dprint(f"[{castle_type}]: check passed")
        elif castle_type == "雁木":
            if self.left_s[-1] != self.reg_pos((6, 7)):
                self.__dprint(f"[{castle_type}]: 左銀が{self.reg_pos((6, 7))}でない")
                valid_flag = False
            if self.left_g[-1] != self.reg_pos((7, 8)):
                self.__dprint(f"[{castle_type}]: 左金が{self.reg_pos((7, 8))}でない")
                valid_flag = False
            self.__dprint(f"[{castle_type}]: check passed")
        elif castle_type == "矢倉":
            if self.left_s[-1] != self.reg_pos((7, 7)):
                self.__dprint(f"[{castle_type}]: 左銀が{self.reg_pos((7, 7))}でない")
                valid_flag = False
            if self.left_g[-1] != self.reg_pos((7, 8)):
                self.__dprint(f"[{castle_type}]: 左金が{self.reg_pos((7, 8))}でない")
                valid_flag = False
            if self.right_g[-1] != self.reg_pos((6, 7)) and self.right_g[-1] != self.reg_pos((6, 8)):
                self.__dprint(f"[{castle_type}]: 右金が{self.reg_pos((6, 7))}、{self.reg_pos((6, 8))}でない")
                valid_flag = False
            self.__dprint(f"[{castle_type}]: check passed")
        elif castle_type == "急戦矢倉":
            if not self.p6:
                self.__dprint(f"[{castle_type}]: 角道を歩で止めている")
                valid_flag = False
            self.__dprint(f"[{castle_type}]: check passed")
        return valid_flag

    def stat_str(self) -> Set[str]:
        if len(self.castle_set) == 0:
            return {"その他の囲い"}
        if len(self.castle_set) == 1:
            return {x for x in self.castle_set}
        for x in self.castle_set:
            if not self.deep_check(x):
                self.castle_set.remove(x)
        return {x for x in self.castle_set}


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
    def __init__(self, debug=False):
        super().__init__()
        self.state = True  # 正常形かどうか
        self.update = True
        self.is_exchange = False  # 角交換したか
        self.b_captured = False  # 先手が角を捕獲した
        self.w_captured = False  # 後手が角を捕獲した
        self.b_tezon = 0
        self.w_tezon = 0
        self.comment = []
        self.debug = debug

    # デバッグプリント用
    def __dprint(self, string: str):
        d_print(string, is_debug=self.debug)

    def move(self, m_d: Move_Detail):
        if not self.update:
            return
        if m_d.type == "place":  # 駒を打ったならスルー
            return
        if self.update:
            if self.w_captured:  # 先手が後手の角を取り返しに行く
                self.__dprint("先手が後手の角を取り返しに行く")
                self.update = False
                if m_d.move_piece_str == "R":  # 先手が飛を動かした
                    self.is_exchange = True
                    self.comment.append("先手向かい飛車")
                elif m_d.move_piece_str == "G":  # 先手が金を動かした
                    self.__dprint("先手が金を動かした")
                    self.b_tezon += 1
                    self.is_exchange = True
                    if m_d.moved == (8, 8):  # 78に戻るために手損することになる
                        self.comment.append("先手一手損角換わり")
                    elif m_d.moved == (7, 7):  # 77金型(阪田流)
                        self.comment.append("先手77金型")
                    else:
                        self.state = False
                elif m_d.move_piece_str == "S":  # 先手が銀を動かした
                    self.__dprint("先手が銀を動かした")
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
                    self.__dprint("先手の動かす駒：正常形でない")
                    self.update = False
                    self.state = False

            elif self.b_captured:  # 後手が先手の角を取り返しに行く
                self.__dprint("後手が先手の角を取り返しに行く")
                self.update = False
                if m_d.move_piece_str == "r":  # 後手が飛を動かした
                    self.is_exchange = True
                    self.comment.append("後手向かい飛車")
                elif m_d.move_piece_str == "g":  # 後手が金を動かした
                    self.__dprint("後手が金を動かした")
                    self.w_tezon += 1
                    self.is_exchange = True
                    if m_d.moved == (2, 2):  # 32に戻るために手損することになる
                        self.comment.append("角換わり")
                    elif m_d.moved == (3, 3):  # 33金型(阪田流)
                        self.comment.append("後手33金型")
                    else:
                        self.state = False
                elif m_d.move_piece_str == "s":  # 後手が銀を動かした
                    self.__dprint("後手が銀を動かした")
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
                    self.__dprint("後手の動かす駒：正常形でない")
                    self.update = False
                    self.state = False
            elif m_d.move_piece_str == "B":  # 先手の角を動かした
                self.__dprint("先手の角を動かした")
                if not (m_d.moved == (7, 7) or m_d.moved == (3, 3) or m_d.moved == (2, 2)):  # 77、33、22以外に動くと通常形でない
                    self.__dprint("77、33、22以外に動くと通常形でない")
                    self.state = False
                    self.update = False
                else:
                    self.b_tezon += 1
                    if m_d.get_piece_origin_str == "b":  # 後手の角を捕獲した
                        self.__dprint("後手の角を捕獲した")
                        self.b_captured = True
            elif m_d.move_piece_str == "b":  # 後手の角を動かした
                self.__dprint("後手の角を動かした")
                if not (m_d.moved == (3, 3) or m_d.moved == (7, 7) or m_d.moved == (8, 8)):  # 33、77、88以外に動くと通常形でない
                    self.__dprint("33、77、88以外に動くと通常形でない")
                    self.state = False
                    self.update = False
                else:
                    self.w_tezon += 1
                    if m_d.get_piece_origin_str == "B":  # 先手の角を捕獲した
                        self.__dprint("先手の角を捕獲した")
                        self.w_captured = True

    def stat_str(self) -> List[str]:
        if not self.state:
            return ["角交換の通常形でない"]
        tezon = self.b_tezon - self.w_tezon
        self.__dprint(f"先手の手損は{tezon}")
        return self.comment


class BishopLine(SenkeiPartsBase):
    """角道の開閉を規定する"""
    def __init__(self):
        super().__init__()
        self.update = True
        self.p_76 = False
        self.p_66 = False
        self.p_34 = False
        self.p_44 = False

    def move(self, m_d: Move_Detail):
        if not self.update:
            return
        if m_d.type == "place":  # 駒を打ったならスルー
            return
        if m_d.move_piece_str == "P" and m_d.pos == (7, 7):  # 76歩
            self.p_76 = True
        elif m_d.move_piece_str == "P" and m_d.pos == (6, 7):  # 66歩
            self.p_66 = True
        elif m_d.move_piece_str == "p" and m_d.pos == (3, 3):  # 34歩
            self.p_34 = True
        elif m_d.move_piece_str == "p" and m_d.pos == (4, 3):  # 44歩
            self.p_44 = True
        if self.p_76 and self.p_66 and self.p_34 and self.p_44:
            self.update = False

    def stat_str(self) -> List[str]:
        result = []
        if self.p_76 and self.p_66:
            result.append("先手は角道クローズ")
        elif self.p_76 and not self.p_66:
            result.append("先手は角道オープン")
        elif not self.p_76 and not self.p_66:
            result.append("先手は角道不突")
        if self.p_34 and self.p_44:
            result.append("後手は角道クローズ")
        elif self.p_34 and not self.p_44:
            result.append("後手は角道オープン")
        elif not self.p_34 and not self.p_44:
            result.append("後手は角道不突")
        return result


class KingRookTrace(SenkeiPartsBase):
    """玉と飛車の軌跡を表すクラス"""
    def __init__(self):
        super().__init__()
        self.state = True
        self.update = True  # 更新フラグ
        self.b_update = True  # 先手フラグ
        self.w_update = True  # 後手フラグ
        self.b_rook_front = 0  # 先手の2筋の歩をいくつ突いたか(3なら飛車先の歩を切っている)
        self.w_rook_front = 0  # 後手の8筋の歩をいくつ突いたか(3なら飛車先の歩を切っている)
        self.b_rook = [(2, 8)]
        self.w_rook = [(8, 2)]
        self.b_king = [(5, 9)]
        self.w_king = [(5, 1)]

    def __move_black_p(self, m_d: Move_Detail):
        if m_d.pos == (2, 7):  # 26歩
            self.b_rook_front = 1
        elif m_d.pos == (2, 6):  # 25歩
            self.b_rook_front = 2
        elif m_d.pos == (2, 5):  # 24歩
            self.b_rook_front = 3

    def __move_white_p(self, m_d: Move_Detail):
        if m_d.pos == (8, 3):  # 84歩
            self.w_rook_front = 1
        elif m_d.pos == (8, 4):  # 85歩
            self.w_rook_front = 2
        elif m_d.pos == (8, 5):  # 86歩
            self.w_rook_front = 3

    def __move_black_r(self, m_d: Move_Detail):
        if m_d.pos == (2, 8) and m_d.moved == (2, 4):  # 24飛と歩を取った
            self.b_rook.append((2, 4))
        elif m_d.pos == (2, 4) and m_d.moved == (2, 5):  # 25飛
            self.b_rook.append((2, 5))
        elif m_d.pos == (2, 4) and m_d.moved == (2, 6):  # 26飛
            self.b_rook.append((2, 6))
        elif m_d.pos == (2, 4) and m_d.moved == (2, 8):  # 28飛
            self.b_rook.append((2, 8))
            self.b_update = False
        elif m_d.pos == (2, 4) and m_d.moved == (3, 4):  # 34飛 (横歩取り)
            self.b_rook.append((3, 4))
            return "横歩取り"
        elif m_d.pos == (2, 4) and m_d.moved == (2, 1):  # 何らかの超急戦
            self.b_rook.append((2, 1))
            self.b_update = False
            self.w_update = False
        elif m_d.pos == (2, 8) and m_d.moved == (3, 8):  # 38飛
            self.b_rook.append((3, 8))
            self.b_update = False
        elif m_d.pos == (2, 8) and m_d.moved == (4, 8):  # 48飛
            self.b_rook.append((4, 8))
            self.b_update = False
        elif m_d.pos == (2, 8) and m_d.moved == (5, 8):  # 58飛
            self.b_rook.append((5, 8))
            self.b_update = False
        elif m_d.pos == (2, 8) and m_d.moved == (6, 8):  # 68飛
            self.b_rook.append((6, 8))
        elif m_d.pos == (2, 8) and m_d.moved == (7, 8):  # 78飛
            self.b_rook.append((7, 8))
        elif m_d.pos == (2, 8) and m_d.moved == (8, 8):  # 88飛
            self.b_rook.append((8, 8))
            self.b_update = False
        elif m_d.pos == (6, 8) and m_d.moved == (7, 8):  # 4→3
            self.b_rook.append((7, 8))
        elif m_d.pos == (6, 8) and m_d.moved == (8, 8):  # 4→2
            self.b_rook.append((8, 8))
            self.b_update = False
        elif m_d.pos == (7, 8) and m_d.moved == (7, 6):  # 三間飛車浮き飛車
            self.b_rook.append((7, 6))
            self.b_update = False
        elif m_d.pos == (6, 8) and m_d.moved == (6, 6):  # 四間飛車浮き飛車
            self.b_rook.append((6, 6))
            self.b_update = False
        elif m_d.pos == (5, 8) and m_d.moved == (5, 6):  # 中飛車浮き飛車
            self.b_rook.append((5, 6))
            self.b_update = False

    def __move_white_r(self, m_d: Move_Detail):
        if m_d.pos == (8, 2) and m_d.moved == (8, 6):  # 86飛と歩を取った
            self.w_rook.append((8, 6))
        elif m_d.pos == (8, 6) and m_d.moved == (8, 5):  # 85飛
            self.w_rook.append((8, 5))
        elif m_d.pos == (8, 6) and m_d.moved == (8, 4):  # 84飛
            self.w_rook.append((8, 4))
        elif m_d.pos == (8, 6) and m_d.moved == (8, 2):  # 82飛
            self.w_rook.append((8, 2))
            self.w_update = False
        elif m_d.pos == (8, 6) and m_d.moved == (7, 6):  # 76飛 (横歩取り)
            self.w_rook.append((7, 6))
            return "横歩取り"
        elif m_d.pos == (8, 6) and m_d.moved == (8, 9):  # 何らかの超急戦
            self.w_rook.append((8, 9))
            self.b_update = False
            self.w_update = False
        elif m_d.pos == (8, 2) and m_d.moved == (7, 2):  # 72飛
            self.w_rook.append((7, 2))
            self.w_update = False
        elif m_d.pos == (8, 2) and m_d.moved == (6, 2):  # 62飛
            self.w_rook.append((6, 2))
            self.w_update = False
        elif m_d.pos == (8, 2) and m_d.moved == (5, 2):  # 52飛
            self.w_rook.append((5, 2))
            self.w_update = False
        elif m_d.pos == (8, 2) and m_d.moved == (4, 2):  # 42飛
            self.w_rook.append((4, 2))
        elif m_d.pos == (8, 2) and m_d.moved == (3, 2):  # 32飛
            self.w_rook.append((3, 2))
        elif m_d.pos == (8, 2) and m_d.moved == (2, 2):  # 22飛
            self.w_rook.append((2, 2))
            self.w_update = False
        elif m_d.pos == (4, 2) and m_d.moved == (3, 2):  # 4→3
            self.w_rook.append((3, 2))
        elif m_d.pos == (4, 2) and m_d.moved == (2, 2):  # 4→2
            self.w_rook.append((2, 2))
            self.w_update = False
        elif m_d.pos == (3, 2) and m_d.moved == (3, 4):  # 三間飛車浮き飛車
            self.w_rook.append((3, 4))
            self.w_update = False
        elif m_d.pos == (4, 2) and m_d.moved == (4, 4):  # 四間飛車浮き飛車
            self.w_rook.append((4, 4))
            self.w_update = False
        elif m_d.pos == (5, 2) and m_d.moved == (5, 4):  # 中飛車浮き飛車
            self.w_rook.append((5, 4))
            self.w_update = False

    def __move_black_k(self, m_d: Move_Detail):
        self.b_king.append(m_d.moved)

    def __move_white_k(self, m_d: Move_Detail):
        self.w_king.append(m_d.moved)

    def move(self, m_d: Move_Detail):
        if not self.update:
            return
        if m_d.type == "place":  # 駒を打ったならスルー
            return
        if m_d.move_piece_str == "P":
            return self.__move_black_p(m_d)
        elif m_d.move_piece_str == "p":
            return self.__move_white_p(m_d)
        elif m_d.move_piece_str == "R":
            return self.__move_black_r(m_d)
        elif m_d.move_piece_str == "r":
            return self.__move_white_r(m_d)
        elif m_d.move_piece_str == "K":
            return self.__move_black_k(m_d)
        elif m_d.move_piece_str == "k":
            return self.__move_white_k(m_d)

    def stat_str(self) -> List[str]:
        if not self.state:
            return ["飛車の軌跡が通常形でない"]
        return [
            f"先手{self.check_b()}",
            f"後手{self.check_w()}"
        ]

    def check_b(self):
        if self.b_rook_front == 3:
            return "横歩取り・相掛かり"
        if self.b_rook_front >= 1:
            if self.b_king[-1] == (5, 8) or self.b_king[-1][0] >= 6:
                return "居飛車"
            elif self.b_king[-1][0] <= 4:
                return "居飛車右玉・陽動振り飛車"
        if len(self.b_rook) <= 1:
            if self.b_king[-1] == (5, 8) or self.b_king[-1][0] >= 6:
                return "居飛車模様"
            return
        if self.b_rook[1] == (5, 8) and not self.b_rook[-1] == (2, 8):
            if self.b_king[-1][0] >= 6:
                return "中飛車左"
            elif self.b_king[-1][0] <= 4:
                return "中飛車右"
        if self.b_rook[1] == (6, 8):
            return "四間飛車"
        if self.b_rook[1] == (7, 8):
            return "三間飛車"
        if self.b_rook[1] == (8, 8):
            return "向かい飛車"

    def check_w(self):
        if self.w_rook_front == 3:
            return "横歩取り・相掛かり"
        if self.w_rook_front >= 1:
            if self.w_king[-1] == (5, 2) or self.w_king[-1][0] <= 4:
                return "居飛車"
            elif self.w_king[-1][0] >= 6:
                return "居飛車右玉・陽動振り飛車"
        if len(self.w_rook) <= 1:
            if self.w_king[-1] == (5, 2) or self.w_king[-1][0] <= 4:
                return "居飛車模様"
            return
        if self.w_rook[1] == (5, 2) and not self.w_rook[-1] == (8, 2):
            if self.w_king[-1][0] <= 4:
                return "中飛車左"
            elif self.w_king[-1][0] >= 6:
                return "中飛車右"
        if self.w_rook[1] == (4, 2):
            return "四間飛車"
        if self.w_rook[1] == (3, 2):
            return "三間飛車"
        if self.w_rook[1] == (2, 2):
            return "向かい飛車"


class DoubleStaticRook:  # 相居飛車クラス
    # 横歩取りと矢倉はさらに専用のルーチンに分割する
    # 横歩は微妙に形が違う亜種の概念を実装する(ここだけ先後反転盤面をうまく扱う関数を作るかも)
    # 矢倉は雁木も含めて実装する(阿久津流と米長流を区別できるぐらいの粒度で)
    # 角換わりは相腰掛銀を細分化するなら専用ルーチンが必要だが現状大丈夫だろう
    # 相掛かりは横歩取りが完成してから考える(これも亜種だらけなので)
    # 右玉は？
    def __init__(self):
        self.right_silver_method = RightSilverMethod()
        self.right_gold_method = RightGoldMethod()

    def move(self, m_d: Move_Detail):
        self.right_silver_method.move(m_d)
        self.right_gold_method.move(m_d)

    def print(self):
        self.right_silver_method.print()
        self.right_gold_method.print()


class BlackRangingRook:  # 先手振り飛車クラス
    # 飛車の筋と角道で大分類する
    # 囲い判定ルーチンが必要になると思われる
    # 左玉なども同時に判定したい
    pass


class WhiteRangingRook:  # 後手振り飛車クラス
    # 先手を反転させたクラスとして実装する
    pass


class DoubleRangingRook:  # 相振り飛車クラス
    # とりあえず互いの飛車の筋だけの分類でよいと思われる
    pass


class Senkei:
    def __init__(self, debug=False):
        self.edge_p36 = EdgeP36()
        self.bishop_exchange = BishopExchange()
        self.bishop_line = BishopLine()
        self.rook_trace = KingRookTrace()
        # 居飛車と振り飛車のフラグを持って不要になったら落とす
        self.is_black_static_rook = True  # 飛車が左に行き かつ 玉が右に行くまで保持
        self.is_white_static_rook = True  # 飛車が左に行き かつ 玉が右に行くまで保持
        self.is_black_ranging_rook = True  # 先手玉が左に行くか、24歩突くまで保持
        self.is_white_ranging_rook = True  # 後手玉が左に行くか、86歩突くまで保持
        self.double_static_rook = DoubleStaticRook()
        self.black_ranging_rook = BlackRangingRook()
        self.white_ranging_rook = WhiteRangingRook()
        self.double_ranging_rook = DoubleRangingRook()
        self.black_king_left_castle = KingLeftCastle(is_black=True)
        self.white_king_left_castle = KingLeftCastle(is_black=False)
        self.black_str = None
        self.white_str = None
        self.senkei_classify = SenkeiClassify()
        self.debug = debug

    # デバッグプリント用
    def __dprint(self, string: str):
        d_print(string, is_debug=self.debug)

    def move(self, m_d: Move_Detail, tesuu=1):
        self.edge_p36.move(m_d)
        if self.is_black_static_rook and self.is_white_static_rook:
            self.double_static_rook.move(m_d)
        self.black_king_left_castle.move(m_d)
        self.white_king_left_castle.move(m_d)
        self.bishop_exchange.move(m_d)
        self.bishop_line.move(m_d)
        self.rook_trace.move(m_d)
        if tesuu > 10:
            [b, w] = self.rook_trace.stat_str()
            if b in {"先手居飛車", "先手横歩取り・相掛かり", "先手居飛車右玉・陽動振り飛車", "先手中飛車左"}:
                self.is_black_ranging_rook = False
                self.black_str = b
            elif b in {"先手中飛車右", "先手四間飛車", "先手三間飛車", "先手向かい飛車"}:
                self.is_black_static_rook = False
                self.black_str = "先手中飛車" if b == "先手中飛車左" else b
            if w in {"後手居飛車", "後手横歩取り・相掛かり", "後手居飛車右玉・陽動振り飛車", "後手中飛車左"}:
                self.is_white_ranging_rook = False
                self.white_str = w
            elif w in {"後手中飛車右", "後手四間飛車", "後手三間飛車", "後手向かい飛車"}:
                self.is_white_static_rook = False
                self.white_str = "後手中飛車" if w == "後手中飛車右" else w
            if tesuu > 40:
                if b == "先手居飛車模様":
                    self.is_black_ranging_rook = False
                    self.black_str = b
                if w == "後手居飛車模様":
                    self.is_white_ranging_rook = False
                    self.white_str = w

    def print(self):
        self.edge_p36.print()
        if self.is_black_static_rook and self.is_white_static_rook:
            self.double_static_rook.print()
        self.bishop_exchange.print()
        self.bishop_line.print()
        self.rook_trace.print()
        if self.black_str and self.white_str:
            print(f"{self.black_str}")
            print(f"{self.white_str}")
        print(f"先手{self.black_king_left_castle.castle_set}")
        print(f"後手{self.white_king_left_castle.castle_set}")

    def test(self):
        b = self.rook_trace.check_b()
        w = self.rook_trace.check_w()
        if b and w:
            print(f"先手{b}、後手{w}")

    def get_large_classification(self):
        if not xor(self.is_black_static_rook, self.is_black_ranging_rook):
            self.__dprint("先手が居飛車か振り飛車か未確定")
            self.senkei_classify.kingdom = "その他"
            self.senkei_classify.phylum = "その他の戦型"
        elif not xor(self.is_white_static_rook, self.is_white_ranging_rook):
            self.__dprint("後手が居飛車か振り飛車か未確定")
            self.senkei_classify.kingdom = "その他"
            self.senkei_classify.phylum = "その他の戦型"
        elif self.is_black_static_rook and self.is_white_static_rook:
            self.__dprint("相居飛車")
            self.senkei_classify.kingdom = "相居飛車"
            move_black_rook = len(self.rook_trace.b_rook) >= 2
            move_white_rook = len(self.rook_trace.w_rook) >= 2
            if self.bishop_exchange.is_exchange:  # 角交換が行われた
                self.__dprint("角換わり")
                self.senkei_classify.phylum = "角換わり"
            elif (move_black_rook and self.rook_trace.b_rook[1] == (2, 4)) or\
                    (move_white_rook and self.rook_trace.w_rook[1] == (8, 6)):
                if self.rook_trace.b_rook[2] == (3, 4):
                    self.__dprint("横歩取り")
                    self.senkei_classify.phylum = "横歩取り"
                elif self.rook_trace.w_rook[2] == (7, 6):
                    self.__dprint("後手横歩取り")  # ひとまず先後分けておく
                    self.senkei_classify.phylum = "後手横歩取り"
                else:
                    self.__dprint("相掛かり")
                    self.senkei_classify.phylum = "相掛かり"
            elif self.black_king_left_castle.stat_str() & \
                    {"矢倉", "雁木", "急戦矢倉", "菊水矢倉", "早囲い", "片矢倉", "Bonanza囲い"}\
                    and self.white_king_left_castle.stat_str() & \
                    {"矢倉", "雁木", "急戦矢倉", "菊水矢倉", "早囲い", "片矢倉", "Bonanza囲い"}:
                self.__dprint("矢倉")
                self.senkei_classify.phylum = "矢倉"
                if self.black_king_left_castle.stat_str() & {"矢倉"} \
                        and self.white_king_left_castle.stat_str() & {"矢倉"}:
                    self.senkei_classify.subphylum = "相矢倉"
                elif self.black_king_left_castle.stat_str() & {"雁木"} \
                        and self.white_king_left_castle.stat_str() & {"雁木"}:
                    self.senkei_classify.subphylum = "相雁木"
                elif self.black_king_left_castle.stat_str() & {"雁木"}:
                    self.senkei_classify.subphylum = "先手雁木"
                elif self.white_king_left_castle.stat_str() & {"雁木"}:
                    self.senkei_classify.subphylum = "後手雁木"
                elif self.white_king_left_castle.stat_str() & {"急戦矢倉"}:
                    self.senkei_classify.subphylum = "急戦矢倉"
                elif self.black_king_left_castle.stat_str() & {"急戦矢倉"}:
                    self.senkei_classify.subphylum = "先手急戦矢倉"
                elif self.black_king_left_castle.stat_str() & {"片矢倉"} and self.bishop_exchange.is_exchange:
                    self.senkei_classify.subphylum = "藤井矢倉"
                else:
                    self.senkei_classify.subphylum = "矢倉その他"
            else:
                self.__dprint("相居飛車その他の戦型")
                self.senkei_classify.phylum = "相居飛車その他の戦型"
        elif self.is_black_ranging_rook and self.is_white_ranging_rook:
            self.__dprint("相振り飛車")
            self.senkei_classify.kingdom = "相振り飛車"
            self.__dprint(self.black_str + self.white_str)
            self.senkei_classify.phylum = self.black_str + self.white_str
            return self.black_str + self.white_str
        elif self.is_black_static_rook and self.is_white_ranging_rook:
            self.senkei_classify.kingdom = "後手振り飛車"
            if self.bishop_exchange.is_exchange:  # 角交換が行われた
                self.__dprint("後手角交換振り飛車")
                self.__dprint(self.white_str)
                self.senkei_classify.phylum = f"後手角交換{self.white_str[2:]}"
            else:
                self.__dprint("後手ノーマル振り飛車")
                self.__dprint(self.white_str)
                self.senkei_classify.phylum = f"後手ノーマル{self.white_str[2:]}"
        elif self.is_black_ranging_rook and self.is_white_static_rook:
            self.senkei_classify.kingdom = "先手振り飛車"
            if self.bishop_exchange.is_exchange:  # 角交換が行われた
                self.__dprint("先手角交換振り飛車")
                self.__dprint(self.black_str)
                self.senkei_classify.phylum = f"先手角交換{self.black_str[2:]}"
            else:
                self.__dprint("先手ノーマル振り飛車")
                self.__dprint(self.black_str)
                self.senkei_classify.phylum = f"先手ノーマル{self.black_str[2:]}"
