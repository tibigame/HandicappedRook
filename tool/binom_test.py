from scipy.stats import binom_test
import sys
args = sys.argv

win = int(args[1])
lose = int(args[2])
match = win + lose
p = float(args[3]) if len(args) >= 4 else 50.0

result = binom_test(win, match, p / 100.0)
print(f"試合数：{match}")
print(f"実勝率：　{100.0 * win / match:.2f}%")
print(f"仮定勝率：{p:.2f}%")
print(f"{result * 100:.2f}% ({result})")
