import numpy as np
from scipy.stats import beta
import sys
args = sys.argv
max_delta_rating = 2**15 # レーティング差の最大値を表す定数

def infer_rating(win, lose, draw): # レーティングの区間推定を行う
    def erorate(winrate): # 勝率からレーティング差を計算する
        if winrate == 1:
            return max_delta_rating
        if winrate == 0:
            return -max_delta_rating
        return 400.0 * np.log10(winrate / (1 - winrate))

    def clopper_pearson(k, n, alpha): # clopper_pearson法による二項分布近似
        alpha2 = (1 - alpha) / 2
        lower = beta.ppf(alpha2, k, n - k + 1)
        upper = beta.ppf(1 - alpha2, k + 1, n - k)
        return (lower, upper)
 
    def print_result(result, alpha_string): # 結果の出力
        lower = -max_delta_rating if result[0] != result[0] else erorate(result[0])
        upper = max_delta_rating if result[1] != result[1] else erorate(result[1])
        print(f"R({alpha_string}): {lower:.2f}～{upper:.2f}, Range: {upper - lower:.2f}")

    match = win + lose
    print(f"有効試合数: {match}")
    print(f"勝率: {100 * win / match:.2f}%, ⊿R: {erorate(win / match):.1f}, 引分率: {100 * draw / (draw + match):.2f}%")
    print_result(clopper_pearson(win, match, 0.95), "95.0000%")
    print_result(clopper_pearson(win, match, 0.99), "99.0000%")
    print_result(clopper_pearson(win, match, 0.999), "99.9000%")
    print_result(clopper_pearson(win, match, 0.999999), "99.9999%")

infer_rating(int(args[1]), int(args[2]), int(args[3]))
