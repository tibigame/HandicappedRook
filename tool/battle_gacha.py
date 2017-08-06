import numpy as np

p = np.random.rand() * 0.6 + 0.2 # 真の確率も乱数で設定
battle_num = 100 # 1セットあたりの対局数です
set_num = 10 # 10セット行います

def go_battle(battle_array, p):
    return len(np.where(battle_array < p)[0]) # そのまま勝率(%)になる

win_list = []
for battle in np.random.rand(set_num, battle_num): # 0〜1の乱数セットを生成してループを回す
    win_list.append(go_battle(battle, p)) # 勝利数を記録していく

print("100試合対局ガチャの結果です。")
print(win_list)
print(f"真の勝率は{p*100}%です。")
print(f"最小勝率は{np.min(win_list)}%です。")
print(f"平均勝率は{np.average(win_list)}%です。")
print(f"最高勝率は{np.max(win_list)}%です。")
