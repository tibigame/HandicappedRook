import numpy as np
from scipy.stats import beta

def r_elorating(A, B): # レーティングから勝率を計算する
        return 1 / (1 + 10**((B - A) / 400)) # A側の勝率を返す

max_delta_rating = 9999 # レーティング差の最大値を表す定数
def elorating(winrate): # 勝率からレーティング差を計算する
        if winrate == 1:
            return max_delta_rating
        if winrate == 0:
            return -max_delta_rating
        return 400.0 * np.log10(winrate / (1 - winrate))

def infer_rating(win, lose, alpha): # レーティングの区間推定を行う
    def clopper_pearson(k, n, alpha): # clopper_pearson法による二項分布近似
        lower = beta.ppf(alpha, k, n - k + 1)
        upper = beta.ppf(1 - alpha, k + 1, n - k)
        return (lower, upper, elorating(lower), elorating(upper), alpha)

    match = win + lose
    winrate = np.nan if match == 0 else 100 * win / match
    deltarate = np.nan if match == 0 else elorating(win / match)
    return clopper_pearson(win, match, alpha)

print("t:両側推定する。\nu:上側推定する。\nd:下側推定する。")
infer_type = input() # 検定のタイプ

# 神が評価関数の設定を行います
Apery_twig = 3000 # 基準となる評価関数のレート (キリの良い数字にしておく)
print("作成する評価関数の数を入力してください。例：26")
eval_num = int(input()) #  作成する評価関数の数
if eval_num < 9:
    raise ValueError("10以上の数値を入力してください。")
if eval_num > 2000000:
    raise ValueError("数値が大きすぎるので実行しません。")
god_eval_list = Apery_twig  + np.random.rand(eval_num) * 600 - 300 # 評価関数に上下300のR幅を持たせる
god_winrate_list = []
for e in god_eval_list:
    god_winrate_list.append(r_elorating(e, Apery_twig)) # 基準となる評価関数との勝率のリストを計算する
god_winrate_list

# ユーザーが神の定めた評価関数で対戦を行い強さを推定します
print("評価関数当たりの対局数を入力してください。例：300")
battle_num = int(input()) #  作成する評価関数の数
if battle_num < 9:
    raise ValueError("10以上の数値を入力してください。")
if battle_num > 10000:
    raise ValueError("数値が大きすぎるので実行しません。")

print("信頼区間を入力してください。例：0.95")
u_alpha = float(input()) # ユーザー指定信頼区間
if u_alpha < 0.01:
    raise ValueError("信頼区間が不正です。")
if u_alpha >= 1:
    raise ValueError("信頼区間が不正です。")

win_list = []
spot_list = []
infer_rating_list = []
for (battle, p) in zip(np.random.rand(eval_num, battle_num), god_winrate_list): # 乱数セットを生成して真の勝率リストから結果を計算する
    win = len(np.where(battle < p)[0])
    lose = battle_num - win
    win_list.append((win, lose))
    spot_list.append(elorating(win / (win + lose)))
    if infer_type == "u": # 上側推定
        alpha2 = 1 - u_alpha
    elif infer_type == "d": # 下側推定
        alpha2 = 1 - u_alpha
    else:
        alpha2 = (1 - u_alpha) / 2 # 両側推定
    infer_rating_list.append(infer_rating(win, lose, alpha2))
    
# 神がユーザーの解答を採点します
eval_error_list = god_eval_list - Apery_twig - spot_list # 真値と報告値との誤差
print("点推定の誤差評価をするよ。")
print(f"最も過小評価した評価関数はR{eval_error_list.max():.0f}小さく見積もってるよ。")
print(f"最も過大評価した評価関数はR{-eval_error_list.min():.0f}大きく見積もってるよ。")
print("区間推定の誤差評価をするよ。")
i = 0
for (infer, god) in zip(infer_rating_list, god_eval_list):
    min_rate = -max_delta_rating if infer_type == "u" else infer[2] + Apery_twig # レート下限
    max_rate = max_delta_rating if infer_type == "d" else infer[3] + Apery_twig # レート上限
    if god < min_rate: # 真値が推定下限を下回る
        i += 1
        print(f"R{min_rate:.0f} ～ R{max_rate:.0f}と推定したけど、真値は{god:.1f}だよ。区間左端からの距離({min_rate - god:.1f})")
    elif max_rate < god: # 真値が推定上限を上回る
        i += 1
        print(f"R{min_rate:.0f} ～ R{max_rate:.0f}と推定したけど、真値は{god:.1f}だよ。区間右端からの距離({god - max_rate:.1f})")
if i == 0:
    print("全ての評価関数の推定が真値を含んでいるよ。")
else:
    print(f"{eval_num}個の評価関数のうち{i}個の推定で真値を外したよ。")
