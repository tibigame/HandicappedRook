from scipy.stats import binom_test
import sys
args = sys.argv

win = int(args[1])
lose = int(args[2])
match = win + lose
p = float(args[3]) if len(args) >= 4 else 50.0
if len(args) < 5:
    alternative = "less" # 勝率が指定の値より強いかどうかの検定
    type = "以上"
elif args[4] == "l": # 採択率を取るので引数の値は逆になる
    alternative = "greater" # 勝率が指定の値より弱いかどうかの検定
    type = "以下"
elif args[4] == "g": # 採択率を取るので引数の値は逆になる
    alternative = "less"
    type = "以上"
else:
    alternative = "two-sided" # 勝率が指定の値かどうかの検定
    type = "両側検定"

result = binom_test(win, match, p / 100.0, alternative)
print(f"試合数：{match}")
print(f"実勝率：{100.0 * win / match:.2f}%")
print(f"仮勝率：{p:.2f}% {type}")
print(f"採択率：{result * 100:.2f}% ({result})")
