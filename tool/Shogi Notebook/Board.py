import numpy as np
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
fp = FontProperties(fname=r'C:\Windows\Fonts\ipaexg.ttf', size=24)

row = ["〇", "一", "二", "三", "四", "五", "六", "七", "八", "九",
          "十", "十一", "十二", "十三", "十四", "十五", "十六", "十七", "十八"]
colmun = ["０", "１", "２", "３", "４", "５", "６", "７", "８", "９"]
# 後手は+1 成りは+2にする
piece = {
    "k": [2**2 + 1, "王"],
    "r": [2**6 + 1, "飛"],
    "+r": [2**6 + 3, "龍"],
    "b": [2**10 + 1, "角"],
    "+b": [2**10 + 3, "馬"],
    "g": [2**14 + 1, "金"],
    "s": [2**18 + 1, "銀"],
    "+s": [2**18 + 3, "全"],
    "n": [2**22 + 1, "桂"],
    "+N": [2**22 + 3, "圭"],
    "l": [2**26 + 1, "香"],
    "+l": [2**26 + 3, "杏"],
    "p": [2**30 + 1, "歩"],
    "+p": [2**30 + 3, "と"],
    "K": [2**2, "玉"],
    "R": [2**6, "飛"],
    "+R": [2**6 + 2, "龍"],
    "B": [2**10, "角"],
    "+B": [2**10 + 2, "馬"],
    "G": [2**14, "金"],
    "S": [2**18, "銀"],
    "+S": [2**18 + 2, "全"],
    "N": [2**22, "桂"],
    "+N": [2**22 + 2, "圭"],
    "L": [2**26, "香"],
    "+L": [2**26 + 2, "杏"],
    "P": [2**30, "歩"],
    "+P": [2**30 + 2, "と"]
}
reverse_piece = {
    2**2 + 1: "k",
    2**6 + 1: "r",
    2**6 + 3: "+r",
    2**10 + 1: "b",
    2**10 + 3: "+b",
    2**14 + 1: "g",
    2**18 + 1: "s",
    2**18 + 3: "+s",
    2**22 + 1: "n",
    2**22 + 3: "+n",
    2**26 + 1: "l",
    2**26 + 3: "+l",
    2**30 + 1: "p",
    2**30 + 3: "+p",
    2**2: "K",
    2**6: "R",
    2**6 + 2: "+R",
    2**10: "B",
    2**10 + 2: "+B",
    2**14: "G",
    2**18: "S",
    2**18 + 2: "+S",
    2**22: "N",
    2**22 + 2: "+N",
    2**26: "L",
    2**26 + 2: "+L",
    2**30: "P",
    2**30 + 2: "+P"
}

def dec_piecenum(piecenum): #駒の数字から駒文字に変更する
    mod = piecenum % 4
    if mod == 0 or mod == 1: # 成り判定
        piece_base = piecenum
        promote = ""
    else:
        piece_base = piecenum - 2 # 成りなら2を引く
        promote = "+"
    return promote + reverse_piece[piece_base]

class Board:
    # コンストラクタ
    def __init__(self, sfen):
        self.ban = np.zeros([9, 9], "int32") # インデックスと符号は1つずれるので注意
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
        print(f"pos={pos}")
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
    # 玉が右か左か
    # 飛、角の位置

    # USIプロトコルの指し手文字列を分析します。
    def __analize_move(self, move_string):
        def int_to_file(char):
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

        def char_to_rank(char):
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
            return ("place", peace, pos)
        # 盤上の駒を動かす
        pos = (int_to_file(m_l[0]), char_to_rank(m_l[1]))
        moved = (int_to_file(m_l[2]), char_to_rank(m_l[3]))
        if len(m_l) >= 5 and m_l[4] == "+":
            is_promote = True
        else:
            is_promote = False
        return ("move", pos, moved, is_promote)

    # USIプロトコルの指し手を与えて実行します。駒の動きの正当性のチェックはしません。
    def move(self, move_string):
        m = self.__analize_move(move_string)
        if m[0] == "move":
            # 起点の座標が自分の駒か
            if self.get_teban() == "b":
                if not self.is_black_piece(m[1]):
                    raise ValueError("先手の手番で先手の駒以外を動かそうとしました")
            else:
                if not self.is_white_piece(m[1]):
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
                raise ValueError("自分の駒がある位置に動かそうとしました")
            if self.is_king(m[2]):
                raise ValueError("玉を捕獲しようとしました")
            # 駒を動かす
            if m[3]: # 駒を成る場合
                self.ban[m[2][1] - 1][m[2][0] - 1] = self.get_promoted_num(m[1])
            else: # 通常の場合
                self.ban[m[2][1] - 1][m[2][0] - 1] = self.ban[m[1][1] - 1][m[1][0] - 1]
            self.ban[m[1][1] - 1][m[1][0] - 1] = 0
            # 駒を取得する
            if get_piece:
                self.koma[dec_piecenum(get_piece)] += 1

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
            self.ban[m[2][1] - 1][m[2][0] - 1] = piece[m[1]][0] # 盤面に駒を置く
        else:
            raise ValueError("想定されたmoveではありません")
        self.set_teban("r") # 指し手が進んだので手番変更
        self.inc_count() # 手数カウントを1増やしておく
        return

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
