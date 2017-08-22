import numpy as np
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
fp = FontProperties(fname=r'C:\Windows\Fonts\ipaexg.ttf', size=24)
from Bitboard import piece
from Bitboard import reverse_piece
from Bitboard import get_pos
from Bitboard import B_BLACK, B_WHITE
from collections import Counter
from collections import OrderedDict

row = ["〇", "一", "二", "三", "四", "五", "六", "七", "八", "九",
          "十", "十一", "十二", "十三", "十四", "十五", "十六", "十七", "十八"]
colmun = ["０", "１", "２", "３", "４", "５", "６", "７", "８", "９"]

def dec_piecenum(piecenum): #駒の数字から駒文字に変更する
    mod = piecenum % 4
    if mod == 0 or mod == 1: # 成り判定
        piece_base = piecenum
        promote = ""
    else:
        piece_base = piecenum - 2 # 成りなら2を引く
        promote = "+"
    return promote + reverse_piece[piece_base]

# 駒インデックスのタプルから符号リストに変換します
def conv_pos_taple(p):
    result = []
    for (x, y) in zip(p[0], p[1]):
        result.append((y + 1, x + 1)) # インデックスと符号は1ずれる
    return result

# 指し手の詳細
class Move_Detail:
    def __init__(self):
        self.type_ = ""
        self.pos = ""
        self.moved = ""
        self.is_promote = False
        self.move_piece_str = ""
        self.get_piece_str = ""
        self.detail = ""

class Board:
    # コンストラクタ
    def __init__(self, sfen):
        self.ban = np.zeros([9, 9], "int8") # インデックスと符号は1つずれるので注意
        self.set_sfen(sfen)

    def __clear_koma(self): # 駒台を空にする
        self.koma = {
            "r": 0,
            "b": 0,
            "g": 0,
            "s": 0,
            "n": 0,
            "l": 0,
            "p": 0,
            "R": 0,
            "B": 0,
            "G": 0,
            "S": 0,
            "N": 0,
            "L": 0,
            "P": 0
        }

    # 手数カウント周り
    def get_count(self):
        return str(self.count)

    def set_count(self, count=0):
        self.count = int(count)
        return

    def inc_count(self, count=0):
        self.count += 1
        return

    # 手番周り
    def get_teban(self): # 手番を返す b(先手) or w(後手)
        return self.teban

    def set_teban(self, new_teban): # 手番を設定、bw以外を与えると手番反転
        if new_teban == "b" or new_teban == "w":
            self.teban = new_teban
        else:
            if self.teban == "b":
                self.teban = "w"
            else:
                self.teban = "b"

    def get_sfen_ban(self): # Boardクラスからsfen形式の盤面文字列を生成する
        sfen = ""
        for rank in self.ban: # 1行ずつ処理する
            sfen_rank = ""
            blank_pos = 0
            for pos in rank[::-1]: # 逆順に取り出す
                if pos == 0: # 空マスならカウントを増やす
                    blank_pos += 1
                else:
                    if blank_pos >= 1: # 空マスの分をフラッシュする
                        sfen_rank += str(blank_pos)
                        blank_pos = 0
                    sfen_rank += dec_piecenum(pos)
            if blank_pos >= 1: # 空マスがあればフラッシュする
                sfen_rank += str(blank_pos)
                blank_pos = 0
            sfen += (sfen_rank + "/") # 最後の行にもスラッシュが付与されるがreturnで除かれる
        return sfen[0:-1]

    def set_sfen_ban(self, sfen_ban): # sfen形式の盤面文字列からBoardクラスに値をセットする
        ranks = sfen_ban.split("/") # 1行ずつ分割
        promote_flag = False # Trueなら成り駒
        for i, rank in enumerate(ranks):
            temp_rank = [0, 0, 0, 0, 0, 0, 0, 0, 0]
            temp_itr = 8
            for char in list(rank): # 1行を1文字ずつスキャンする
                if char.isdigit(): # 数字なら空白マスなので飛ばす
                    temp_itr -= int(char)
                elif char == "+": # +のとき
                    promote_flag = True
                else: # 数字でないとき
                    temp_rank[temp_itr] = piece[char][0] # 入力文字を対応する駒の整数にして入れる
                    if promote_flag:
                        temp_rank[temp_itr] += 2 # 成り駒は2を足す
                        promote_flag = False
                    temp_itr -= 1 # sfenは9→1の順なので符号の数字とは逆順になる
            self.ban[i] = temp_rank # 1行ずつ盤面に代入する
        return self.ban

    def __enc_koma_string(self, koma, piece_string):
        num = koma[piece_string]
        if num == 0:
            return ""
        if num == 1:
            return piece_string
        return str(num) + piece_string

    def __enc_koma_BODstring(self, koma, piece_string):
        num = koma[piece_string]
        if num == 0:
            return ""
        if num == 1:
            return piece[piece_string][1]
        return piece[piece_string][1] + row[num]

    def get_sfen_koma(self): # Boardクラスからsfen形式の駒台文字列を生成する
        temp = ""
        temp += self.__enc_koma_string(self.koma, "R")
        temp += self.__enc_koma_string(self.koma, "B")
        temp += self.__enc_koma_string(self.koma, "G")
        temp += self.__enc_koma_string(self.koma, "S")
        temp += self.__enc_koma_string(self.koma, "N")
        temp += self.__enc_koma_string(self.koma, "L")
        temp += self.__enc_koma_string(self.koma, "P")
        temp += self.__enc_koma_string(self.koma, "r")
        temp += self.__enc_koma_string(self.koma, "b")
        temp += self.__enc_koma_string(self.koma, "g")
        temp += self.__enc_koma_string(self.koma, "s")
        temp += self.__enc_koma_string(self.koma, "n")
        temp += self.__enc_koma_string(self.koma, "l")
        temp += self.__enc_koma_string(self.koma, "p")
        return temp

    def set_sfen_koma(self, sfen_koma): # sfen形式の駒台文字列からBoardクラスに値をセットする
        self.__clear_koma() # まず駒台を空にする
        if sfen_koma == "-": # ハイフンなら持ち駒なしということ
            return
        num = 0 # 駒数
        for char in list(sfen_koma): # 引数を1文字ずつスキャンする
            if char.isdigit(): # 数字なら
                if num == 0: # 駒数が0なら数字を代入
                    num = int(char)
                else: # 駒数が0でないなら2桁の数字ということ
                    num = 10 * num + int(char)
            else: # 数字でないとき
                if num == 0: # 駒数が0なら1が省略されていたとみなす
                    num = 1
                self.koma[char] = num # 駒台にセットする
                num = 0 # 駒数を0にクリア

    def get_sfen(self): # Boardクラスからsfen文字列を生成する
        return "sfen " + self.get_sfen_ban() + " " + self.get_teban() + " " + self.get_sfen_koma() + " " + self.get_count()

    def set_sfen(self, sfen): # sfen文字列からBoardクラスに値をセットする
        sfen_list = sfen.split(" ") # スペースで分割
        if sfen_list[0] != "sfen":
            print("先頭がsfenではありません。")
            return
        self.set_sfen_ban(sfen_list[1])
        self.set_sfen_koma(sfen_list[3])
        self.set_teban(sfen_list[2])
        self.set_count(sfen_list[4])

    # 持ち駒のチェック：pieceの駒をnum枚以上持っているか
    def has(self, piece, num=1):
        if self.koma[piece] >= num:
            return True
        return False

    # 盤面のチェックを書く
    # 盤面の駒値を返す
    def get_num(self, pos):
        return self.ban[pos[1] - 1][pos[0] - 1]
    # マス目が空かどうか
    def is_space(self, pos):
        return self.get_num(pos) == 0
    # 先手の駒か
    def is_black_piece(self, pos):
        num = self.get_num(pos)
        if num & 1: # 後手の駒
            return False
        elif num != 0: # 先手の駒
            return True
        return False # 空マス
    # 後手の駒か
    def is_white_piece(self, pos):
        num = self.get_num(pos)
        if num & 1: # 後手の駒
            return True
        return False # 先手の駒 か 空マス
    # 成り駒か
    def is_promote(self, pos):
        if self.get_num(pos) % 4 >= 2:
            return True
        return False
    # 玉か
    def is_king(self, pos):
        num = self.get_num(pos)
        if num == 2**2 or num == 2**2 + 1:
            return True
        return False
    # 駒の先後を反転した値を返す
    def calc_reverse_num(self, num):
        if num == 0:
            raise ValueError("駒の先後反転を空マスに適用しようとしました")
        if num & 1: # 後手の駒はmod2==1なので1を引く
            return num -1
        return num + 1  # 先手の駒はmod2==0なので1を足す
    def get_reverse_num(self, pos):
        return calc_reverse_num(self.get_num(pos))

    # 駒を成った値を返す
    def get_promoted_num(self, pos):
        num = self.get_num(pos)
        if num == 0:
            raise ValueError("駒の成りを空マスに適用しようとしました")
        if num == 2**2 or num == 2**2 + 1 or num == 2**14 or num == 2**14 + 1:
            raise ValueError("駒の成りを成れない駒に適用しようとしました")
        if num % 4 >= 2:
            raise ValueError("駒の成りを既に成っている駒に適用しようとしました")
        return num + 2  # 成り駒は素の駒に2を足したもの
    # 駒の素の値を返す(成り駒も成る前の値)
    def get_raw_num(self, pos):
        num = self.get_num(pos)
        if num % 4 >= 2:
            return num - 2 # 成り駒は2を引いておく
        return num

    # 駒のインデックスのタプルを返す
    def get_pos(self, p):
        return get_pos(p, self.ban)
    # 駒の符号を返す(無い場合は0、複数ある場合は1つ目)
    def get_x_pos1(self, p):
        r = conv_pos_taple(self.get_pos(p))
        if len(r) == 0:
            return 0
        return r[0]
    # 駒の符号を返す(無い場合は0、複数ある場合はリストを返す)
    def get_x_pos2(self, p):
        r = conv_pos_taple(self.get_pos(p))
        if len(r) == 0:
            return 0
        return r

    # 玉の位置(玉は必ずある。stay=5筋、right=右側、left=左側、middle=中段、nyugyoku=敵陣)
    def is_k_stay(self):
        return self.get_pos("k")[1][0] == 4
    def is_K_stay(self):
        return self.get_pos("K")[1][0] == 4
    def is_k_right(self):
        return self.get_pos("k")[1][0] > 4
    def is_k_left(self):
        return self.get_pos("k")[1][0] < 4
    def is_K_right(self):
        return self.get_pos("K")[1][0] < 4
    def is_K_left(self):
        return self.get_pos("K")[1][0] > 4
    def is_k_middle(self):
        y = self.get_pos("k")[0][0]
        return y >= 3 and y <= 5
    def is_K_middle(self):
        y = self.get_pos("K")[0][0]
        return y >= 3 and y <= 5
    def is_k_nyugyoku(self):
        return self.get_pos("k")[0][0] >= 6
    def is_K_nyugyoku(self):
        return self.get_pos("K")[0][0] <= 2

    # 盤上の駒の枚数をカウントする
    def count_piece(self, p, enemy_field=False):
        return len(self.ban[self.ban == piece[p][0]])
    def count_b(self): # 先手の駒
        return len(self.ban[np.logical_and(self.ban % 2 == 0, self.ban != 0)]) # 偶数かつ0以外
    def count_w(self, bitboard=False): # 後手の駒
        return len(self.ban[self.ban % 2 == 1]) # 奇数
    def count_b_bitboard(self, bitboard): # 先手の駒をbitboardの場所でのみカウントする
        ban = np.where(self.ban & bitboard, self.ban, 0)
        return len(ban[np.logical_and(ban % 2 == 0, ban != 0)])
    def count_w_bitboard(self, bitboard): # 後手の駒をbitboardの場所でのみカウントする
        ban = np.where(self.ban & bitboard, self.ban, 0)
        return len(ban[ban % 2 == 1])
    # USIプロトコルの指し手文字列を分析します。
    def __analize_move(self, move_string: str):
        def int_to_file(char: str) -> int:
            if(char == "1"):
                return 1
            elif(char == "2"):
                return 2
            elif(char == "3"):
                return 3
            elif(char == "4"):
                return 4
            elif(char == "5"):
                return 5
            elif(char == "6"):
                return 6
            elif(char == "7"):
                return 7
            elif(char == "8"):
                return 8
            elif(char == "9"):
                return 9
            else:
                raise ValueError("行は1-9で指定する必要があります：" + char)

        def char_to_rank(char: str) -> int:
            if(char == "a"):
                return 1
            elif(char == "b"):
                return 2
            elif(char == "c"):
                return 3
            elif(char == "d"):
                return 4
            elif(char == "e"):
                return 5
            elif(char == "f"):
                return 6
            elif(char == "g"):
                return 7
            elif(char == "h"):
                return 8
            elif(char == "i"):
                return 9
            else:
                raise ValueError("段はa-iで指定する必要があります：" + char)

        m_l = list(move_string)
        # 持ち駒を打つ
        if(m_l[0] == "R" or m_l[0] == "B" or m_l[0] == "G" or m_l[0] == "S" or m_l[0] == "N" or m_l[0] == "L" or m_l[0] == "P"):
            peace = m_l[0]
            if m_l[1] != "*":
                raise ValueError("駒を打つときの2文字目は*である必要があります")
            pos = (int_to_file(m_l[2]), char_to_rank(m_l[3]))
            return ("place", peace, pos, False)
        # 盤上の駒を動かす
        pos = (int_to_file(m_l[0]), char_to_rank(m_l[1]))
        moved = (int_to_file(m_l[2]), char_to_rank(m_l[3]))
        if len(m_l) >= 5 and m_l[4] == "+":
            is_promote = True
        else:
            is_promote = False
        return ("move", pos, moved, is_promote)

    # USIプロトコルの指し手を与えて実行します。駒の動きの正当性のチェックはしません。
    def move(self, move_string: str, detail_kif=False):
        m = self.__analize_move(move_string)
        m_d = Move_Detail()
        m_d.type = m[0]
        m_d.pos = m[1]
        m_d.moved = m[2]
        m_d.is_promote = m[3]
        if m[0] == "move":
            # 起点の座標が自分の駒か
            if self.get_teban() == "b":
                if not self.is_black_piece(m[1]):
                    print(self.get_sfen())
                    print(f"{m[1]}→{m[2]}")
                    raise ValueError("先手の手番で先手の駒以外を動かそうとしました")
            else:
                if not self.is_white_piece(m[1]):
                    print(self.get_sfen())
                    print(f"{m[1]}→{m[2]}")
                    raise ValueError("後手の手番で後手の駒以外を動かそうとしました")
            # 終点の座標が空か
            if self.is_space(m[2]):
                get_piece = False
            # 終点の座標が相手の駒か
            elif self.get_teban() == "b" and self.is_white_piece(m[2]):
                get_piece = self.calc_reverse_num(self.get_raw_num(m[2]))
            elif self.get_teban() == "w" and self.is_black_piece(m[2]):
                get_piece = self.calc_reverse_num(self.get_raw_num(m[2]))
            else:
                print(self.get_sfen())
                print(f"{m[1]}→{m[2]}")
                raise ValueError("自分の駒がある位置に動かそうとしました")
            if self.is_king(m[2]):
                print(self.get_sfen())
                print(f"{m[1]}→{m[2]}")
                raise ValueError("玉を捕獲しようとしました")
            # 駒を動かす
            m_d.move_piece_str = dec_piecenum(self.ban[m[1][1] - 1][m[1][0] - 1])
            # 詳細な棋譜表記生成
            if detail_kif:
                detail = colmun(m[2][0]) + row(m[2][1])
                detail += piece[move_piece_str][1]
                 # TODO 上下寄右左などの条件を作成する必要がある
                if m[3]: # TODO 不成の条件を作成する必要がある
                    detail += "成"
            if m[3]: # 駒を成る場合
                self.ban[m[2][1] - 1][m[2][0] - 1] = self.get_promoted_num(m[1])
            else: # 通常の場合
                self.ban[m[2][1] - 1][m[2][0] - 1] = self.ban[m[1][1] - 1][m[1][0] - 1]
            self.ban[m[1][1] - 1][m[1][0] - 1] = 0
            # 駒を取得する
            if get_piece:
                m_d.get_piece_str = dec_piecenum(get_piece)
                self.koma[m_d.get_piece_str] += 1

        elif m[0] == "place":
            # 指し手は駒種しか入っていないので後手番なら小文字にする
            if self.get_teban() == "w":
                p = m[1].lower()
            else:
                p = m[1]
            # 駒が打てるかのチェック
            if not self.has(p):
                raise ValueError("指定された駒を持っていません")
            if not self.is_space(m[2]):
                raise ValueError("駒を打つ場所が空ではありません")
            self.koma[p] -= 1 # 駒台から駒を1つ減らす
            self.ban[m[2][1] - 1][m[2][0] - 1] = piece[p][0] # 盤面に駒を置く
            m_d.move_piece_str = p
            # 詳細な棋譜表記生成
            if detail_kif:
                detail = colmun(m[2][0]) + row(m[2][1])
                detail += piece[p][1]
                detail += "打" # TODO 打が入る条件を作成する必要がある
        else:
            raise ValueError("想定されたmoveではありません")
        self.set_teban("r") # 指し手が進んだので手番変更
        self.inc_count() # 手数カウントを1増やしておく
        # 分析した指し手、取得した駒、詳細な棋譜表記のクラスを返す
        if detail_kif:
            m_d.detail = detail
        return m_d

    def __plot_common(self, plt):
        one = np.ones(9)
        range = np.arange(-9.0, 0.0, 0.1)
        plt.figure(figsize=(7, 7))
        plt.xlim((-10.5, 1.5))
        plt.ylim((-10.5, 1.5))
        plt.tick_params(labelbottom='off')
        plt.tick_params(labelleft='off')

        plt.plot([-9.0, 0.0], [-9.0, -9.0], color="#000000")
        plt.plot([-9.0, 0.0], [-8.0, -8.0], color="#000000")
        plt.plot([-9.0, 0.0], [-7.0, -7.0], color="#000000")
        plt.plot([-9.0, 0.0], [-6.0, -6.0], color="#000000")
        plt.plot([-9.0, 0.0], [-5.0, -5.0], color="#000000")
        plt.plot([-9.0, 0.0], [-4.0, -4.0], color="#000000")
        plt.plot([-9.0, 0.0], [-3.0, -3.0], color="#000000")
        plt.plot([-9.0, 0.0], [-2.0, -2.0], color="#000000")
        plt.plot([-9.0, 0.0], [-1.0, -1.0], color="#000000")
        plt.plot([-9.0, 0.0], [-0.0, -0.0], color="#000000")

        plt.plot([-9.0, -9.0], [-9.0, 0.0], color="#000000")
        plt.plot([-8.0, -8.0], [-9.0, 0.0], color="#000000")
        plt.plot([-7.0, -7.0], [-9.0, 0.0], color="#000000")
        plt.plot([-6.0, -6.0], [-9.0, 0.0], color="#000000")
        plt.plot([-5.0, -5.0], [-9.0, 0.0], color="#000000")
        plt.plot([-4.0, -4.0], [-9.0, 0.0], color="#000000")
        plt.plot([-3.0, -3.0], [-9.0, 0.0], color="#000000")
        plt.plot([-2.0, -2.0], [-9.0, 0.0], color="#000000")
        plt.plot([-1.0, -1.0], [-9.0, 0.0], color="#000000")
        plt.plot([-0.0, -0.0], [-9.0, 0.0], color="#000000")

    def __plt_text(self, x, y, char, rot=0):
        plt.text(x, y, char, fontsize = 24, rotation = rot, fontproperties=fp, ha='center', va='center')
    def __plot_ban(self, plt, kato123=False):
        if kato123: # ひふみんアイでの反転した盤面を作る
            ban = self.ban[::-1]
            for i, rank in enumerate(ban):
                ban[i] = rank[::-1]
        else:
            ban = self.ban
        offset_x = -0.9
        offset_y = -0.8
        for i, rank in enumerate(ban): # 1行ずつ処理する
            for j, pos in enumerate(rank):
                if pos != 0: # 空マス以外なら駒の文字を出力する
                    char = piece[reverse_piece[pos]][1]
                    if kato123:
                        if pos % 2:
                            self.__plt_text(-0.50 - j, -0.50 - i, char)
                        else:
                            self.__plt_text(-0.60 - j, - 0.30 - i, char, 180)
                    else:
                        if pos % 2: # 後手の駒
                            self.__plt_text(-0.60 - j, - 0.30 - i, char, 180)
                        else: # 先手の駒
                            self.__plt_text(-0.50 - j, -0.50 - i, char)

    def __get_koma_b_string(self, koma):
        temp = ""
        temp += self.__enc_koma_BODstring(koma, "R")
        temp += self.__enc_koma_BODstring(koma, "B")
        temp += self.__enc_koma_BODstring(koma, "G")
        temp += self.__enc_koma_BODstring(koma, "S")
        temp += self.__enc_koma_BODstring(koma, "N")
        temp += self.__enc_koma_BODstring(koma, "L")
        temp += self.__enc_koma_BODstring(koma, "P")
        return temp

    def __get_koma_w_string(self, koma):
        temp = ""
        temp += self.__enc_koma_BODstring(koma, "r")
        temp += self.__enc_koma_BODstring(koma, "b")
        temp += self.__enc_koma_BODstring(koma, "g")
        temp += self.__enc_koma_BODstring(koma, "s")
        temp += self.__enc_koma_BODstring(koma, "n")
        temp += self.__enc_koma_BODstring(koma, "l")
        temp += self.__enc_koma_BODstring(koma, "p")
        return temp

    def __plot_koma(self, plt, kato123=False):
        if kato123: # ひふみんアイでは駒台が逆になる
            plt.text(0.05, -0.6, "☖", fontsize = 24, rotation = 0, fontproperties=fp)
            plt.text(-10.02, -8.7, "☗", fontsize = 24, rotation = 180, fontproperties=fp)
            for i, char in enumerate(list(self.__get_koma_b_string(self.koma))):
                plt.text(-9.95, -8.0 + 0.7 * i, char, fontsize = 24, rotation = 180, fontproperties=fp)
            for i, char in enumerate(list(self.__get_koma_w_string(self.koma))):
                plt.text(0.05, -1.4 - 0.7 * i, char, fontsize = 24, rotation = 0, fontproperties=fp)
        else:
            plt.text(0.05, -0.6, "☗", fontsize = 24, rotation = 0, fontproperties=fp)
            plt.text(-10.02, -8.7, "☖", fontsize = 24, rotation = 180, fontproperties=fp)
            for i, char in enumerate(list(self.__get_koma_b_string(self.koma))):
                plt.text(0.05, -1.4 - 0.7 * i, char, fontsize = 24, rotation = 0, fontproperties=fp)
            for i, char in enumerate(list(self.__get_koma_w_string(self.koma))):
                plt.text(-9.95, -8.0 + 0.7 * i, char, fontsize = 24, rotation = 180, fontproperties=fp)

    def plot(self, pre=False):
        self.__plot_common(plt)
        self.__plot_ban(plt)
        self.__plot_koma(plt)
        if pre:
            plt.fill_between((-pre[0], -pre[0] + 1), -pre[1], -pre[1] + 1, color='#97fef1')
        plt.show()

    def plot123(self, pre=False): # ひふみんアイ
        self.__plot_common(plt)
        self.__plot_ban(plt, True)
        self.__plot_koma(plt, True)
        if pre:
            plt.fill_between((pre[0] - 10, pre[0] - 9), pre[1] - 10, pre[1] - 9, color='#97fef1')
        plt.show()

# sfen形式の棋譜を扱うクラス(予定)
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

class Kifu:
    # コンストラクタ
    def __init__(self, sfen="sfen lnsgkgsnl/1r5b1/ppppppppp/9/9/9/PPPPPPPPP/1B5R1/LNSGKGSNL b - 1", stat_flag=True):
        """初期局面を与える。stat_flagは詰将棋など特殊局面で棋譜統計を切りたい時にFalseにする"""
        self.startBoard = Board(sfen) # 初期局面(固定)
        self.nowBoard = Board(sfen) # 現局面
        self.position_ = "position " + sfen + " moves " # position用のsfen
        self.movelist = [] # 棋譜
        self.stat_flag = stat_flag
        if stat_flag:
            self.__init_stat()

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

    def move(self, m: str, info=None):
        move_detail = self.nowBoard.move(m) # 現局面を動かす
        self.movelist.append(m) # 棋譜に追加
        if self.stat_flag:
            self.__move_stat(move_detail, info) # 統計情報用の分析を行います

    def gameover(self, black_result: str): # 投了、千日手など対局を終了させる
        self.result = black_result # 先手の勝敗結果を与える

    def __move_stat(self, m_d, info):
        if m_d.type == "move": # 盤上の駒が移動する場合
            self.stat_move[m_d.move_piece_str] += 1 # 動かした駒種の統計を更新

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

            if m_d.is_promote: # 指し手が成りの場合
                if self.nowBoard.get_teban() == "w": # 現局面が後手なら直前の指し手は先手のもの
                    self.stat_promote_b += 1 # 先手の成りの数を1増やす
                else: # 後手の指し手
                    self.stat_promote_w += 1 # 後手の成りの数を1増やす

        elif m_d.type == "place": # 駒を打つ場合
            if self.nowBoard.get_teban() == "w": # 現局面が後手なら直前の指し手は先手のもの
                self.stat_move['*_b'] += 1 # 動かした駒種の統計を更新
            else: # 後手の指し手
                self.stat_move['*_w'] += 1 # 動かした駒種の統計を更新

        if info: # infoは送られるなら常に送られることが前提
            self.stat_score_val.append(info.get_score_val()) # 評価値を追加する
        else: # infoが無かった場合は前の評価値を流用することで代用
            if len(self.stat_score_val) <= 2:
                self.stat_score_val.append(0)
            else:
                self.stat_score_val.append(self.stat_score_val[-2])

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
def battle(black_engine, white_engine, kifu):
    think_time = 100
    while kifu.get_tesuu() <= 256:
        pos = kifu.get_sfen()
        now_engine = black_engine if kifu.nowBoard.get_teban() == "w" else white_engine
        go_result = now_engine.go_think(pos, think_time)[1]
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
        kifu.move(bestmove, info)

    # 256手超えで引き分け
    black_engine.gameover()
    white_engine.gameover()
    kifu.gameover("draw")
    return kifu
