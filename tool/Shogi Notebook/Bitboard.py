import numpy as np

# 後手は+1 成りは+2にする
piece = {
    "k": [4 + 1, "王"],
    "r": [8 + 1, "飛"],
    "+r": [8 + 3, "龍"],
    "b": [12 + 1, "角"],
    "+b": [12 + 3, "馬"],
    "g": [16 + 1, "金"],
    "s": [20 + 1, "銀"],
    "+s": [20 + 3, "全"],
    "n": [24 + 1, "桂"],
    "+n": [24 + 3, "圭"],
    "l": [28 + 1, "香"],
    "+l": [28 + 3, "杏"],
    "p": [32 + 1, "歩"],
    "+p": [32 + 3, "と"],
    "K": [4, "玉"],
    "R": [8, "飛"],
    "+R": [8 + 2, "龍"],
    "B": [12, "角"],
    "+B": [12 + 2, "馬"],
    "G": [16, "金"],
    "S": [20, "銀"],
    "+S": [20 + 2, "全"],
    "N": [24, "桂"],
    "+N": [24 + 2, "圭"],
    "L": [28, "香"],
    "+L": [28 + 2, "杏"],
    "P": [32, "歩"],
    "+P": [32 + 2, "と"]
}
reverse_piece = {
    4 + 1: "k",
    8 + 1: "r",
    8 + 3: "+r",
    12 + 1: "b",
    12 + 3: "+b",
    16 + 1: "g",
    20 + 1: "s",
    20 + 3: "+s",
    24 + 1: "n",
    24 + 3: "+n",
    28 + 1: "l",
    28 + 3: "+l",
    32 + 1: "p",
    32 + 3: "+p",
    4: "K",
    8: "R",
    8 + 2: "+R",
    12: "B",
    12 + 2: "+B",
    16: "G",
    20: "S",
    20 + 2: "+S",
    24: "N",
    24 + 2: "+N",
    28: "L",
    28 + 2: "+L",
    32: "P",
    32 + 2: "+P"
}

B_0 = np.zeros([9, 9], "uint8") # 全て0
B_1 = np.invert(B_0) # 0をビット反転して全ビット1にする
B_one = np.ones([9, 9], "uint8") # 全て1

RANK = np.invert(np.zeros([1, 9], "uint8"))
FILE = np.invert(np.zeros([9, 1], "uint8"))

# 先手陣、後手陣
B_BLACK = np.zeros([9, 9], "uint8")
B_BLACK[6,:] = RANK
B_BLACK[7,:] = RANK
B_BLACK[8,:] = RANK
B_WHITE = np.zeros([9, 9], "uint8")
B_WHITE[0,:] = RANK
B_WHITE[1,:] = RANK
B_WHITE[2,:] = RANK

B_k = B_one * piece["k"][0]
B_r = B_one * piece["r"][0]
B_xr = B_one * piece["+r"][0]
B_b = B_one * piece["b"][0]
B_xb = B_one * piece["+b"][0]
B_g = B_one * piece["g"][0]
B_s = B_one * piece["s"][0]
B_xs = B_one * piece["+s"][0]
B_n = B_one * piece["n"][0]
B_xn = B_one * piece["+n"][0]
B_l = B_one * piece["l"][0]
B_xl = B_one * piece["+l"][0]
B_p = B_one * piece["p"][0]
B_xp = B_one * piece["+p"][0]
B_K = B_one * piece["K"][0]
B_R = B_one * piece["R"][0]
B_xR = B_one * piece["+R"][0]
B_B = B_one * piece["B"][0]
B_xB = B_one * piece["+B"][0]
B_G = B_one * piece["G"][0]
B_S = B_one * piece["S"][0]
B_xS = B_one * piece["+S"][0]
B_N = B_one * piece["N"][0]
B_xN = B_one * piece["+N"][0]
B_L = B_one * piece["L"][0]
B_xL = B_one * piece["+L"][0]
B_P = B_one * piece["P"][0]
B_xP = B_one * piece["+P"][0]
B_xP
def get_pos(p, ban): # 駒のインデックスのタプルを返す
    if p == "k":
        return np.where(B_k == ban)
    elif p == "r":
        return np.where(B_r == ban)
    elif p == "+r":
        return np.where(B_xr == ban)
    elif p == "b":
        return np.where(B_b == ban)
    elif p == "+b":
        return np.where(B_xb == ban)
    elif p == "g":
        return np.where(B_g == ban)
    elif p == "s":
        return np.where(B_s == ban)
    elif p == "+s":
        return np.where(B_xs == ban)
    elif p == "n":
        return np.where(B_n == ban)
    elif p == "+n":
        return np.where(B_xn == ban)
    elif p == "l":
        return np.where(B_l == ban)
    elif p == "+l":
        return np.where(B_xl == ban)
    elif p == "p":
        return np.where(B_p == ban)
    elif p == "+p":
        return np.where(B_xp == ban)
    elif p == "K":
        return np.where(B_K == ban)
    elif p == "R":
        return np.where(B_R == ban)
    elif p == "+R":
        return np.where(B_xR == ban)
    elif p == "B":
        return np.where(B_B == ban)
    elif p == "+B":
        return np.where(B_xB == ban)
    elif p == "G":
        return np.where(B_G == ban)
    elif p == "S":
        return np.where(B_S == ban)
    elif p == "+S":
        return np.where(B_xS == ban)
    elif p == "N":
        return np.where(B_N == ban)
    elif p == "+N":
        return np.where(B_xN == ban)
    elif p == "L":
        return np.where(B_L == ban)
    elif p == "+L":
        return np.where(B_xL == ban)
    elif p == "P":
        return np.where(B_P == ban)
    elif p == "+P":
        return np.where(B_xP == ban)
    else:
        raise ValueError("そのような駒はありません")
