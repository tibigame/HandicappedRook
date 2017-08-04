# Komaochi Theorem

駒落ちに関する理論。

# 基礎知識

## はじめに

- 香、角、飛、飛香、飛角(2枚)、飛角両香(4枚)、飛角両桂香(6枚)…という固定の手合いしかメジャーではなかった。
- もっと一般的な駒落ちに関する理論を深めることを目的とする。
- 駒落ちによるハンディキャップは振り飛車によるハンディキャップの理論に応用できる可能性がある。

## 駒落ちの表記法

- 駒落ちはA(左)B右C両Dと表記する。
- ABCDに入る文字列は飛角金銀桂香の順でソートされている。
- Aには飛、角が入る。
- Bがnullのとき左は書かない。Cがnullのとき右は書かない。Dがnullのとき両は書かない。
- 左は省略してもよい。Bには金、銀、桂、香が入り、それぞれ角側の駒を落とすことを表す。
- 右は省略できない。Cには金、銀、桂、香が入り、それぞれ飛側の駒を落とすことを表す。
- 両は省略できない。Dには金、銀、桂、香が入り、それぞれ両側の駒を落とすことを表す。
- B, C, Dの任意の2つの共通集合はnullである。BとCの共通はDに移せる。BとDの共通からBを消せる。CとDの共通からCを消せる。
- 歩落ちの表記はここでは定義しない。

以上のルールにより駒落ちの表記は左を書くか書かないかを除いて一意に定まる。  
駒落ち表記と対応するsfenを下に記す。

'平手': 'sfen lnsgkgsnl/1r5b1/ppppppppp/9/9/9/PPPPPPPPP/1B5R1/LNSGKGSNL b - 1'  
'香': 'sfen lnsgkgsn1/1r5b1/ppppppppp/9/9/9/PPPPPPPPP/1B5R1/LNSGKGSNL w - 1'  
'右香': 'sfen 1nsgkgsnl/1r5b1/ppppppppp/9/9/9/PPPPPPPPP/1B5R1/LNSGKGSNL w - 1'  
'桂': 'sfen lnsgkgs1l/1r5b1/ppppppppp/9/9/9/PPPPPPPPP/1B5R1/LNSGKGSNL w - 1'  
'右桂': 'sfen l1sgkgsnl/1r5b1/ppppppppp/9/9/9/PPPPPPPPP/1B5R1/LNSGKGSNL w - 1'  
'銀': 'sfen lnsgkg1nl/1r5b1/ppppppppp/9/9/9/PPPPPPPPP/1B5R1/LNSGKGSNL w - 1'  
'右銀': 'sfen ln1gkgsnl/1r5b1/ppppppppp/9/9/9/PPPPPPPPP/1B5R1/LNSGKGSNL w - 1'  
'金': 'sfen lnsgk1snl/1r5b1/ppppppppp/9/9/9/PPPPPPPPP/1B5R1/LNSGKGSNL w - 1'  
'右金': 'sfen lns1kgsnl/1r5b1/ppppppppp/9/9/9/PPPPPPPPP/1B5R1/LNSGKGSNL w - 1'  
'両香': 'sfen 1nsgkgsn1/1r5b1/ppppppppp/9/9/9/PPPPPPPPP/1B5R1/LNSGKGSNL w - 1'  
'両桂': 'sfen l1sgkgs1l/1r5b1/ppppppppp/9/9/9/PPPPPPPPP/1B5R1/LNSGKGSNL w - 1'  
'両銀': 'sfen ln1gkg1nl/1r5b1/ppppppppp/9/9/9/PPPPPPPPP/1B5R1/LNSGKGSNL w - 1'  
'両金': 'sfen lns1k1snl/1r5b1/ppppppppp/9/9/9/PPPPPPPPP/1B5R1/LNSGKGSNL w - 1'  
'桂香': 'sfen lnsgkgs11/1r5b1/ppppppppp/9/9/9/PPPPPPPPP/1B5R1/LNSGKGSNL w - 1'  
'右桂香': 'sfen 11sgkgsnl/1r5b1/ppppppppp/9/9/9/PPPPPPPPP/1B5R1/LNSGKGSNL w - 1'  
'桂右香': 'sfen 1nsgkgs1l/1r5b1/ppppppppp/9/9/9/PPPPPPPPP/1B5R1/LNSGKGSNL w - 1'  
'香右桂': 'sfen l1sgkgsn1/1r5b1/ppppppppp/9/9/9/PPPPPPPPP/1B5R1/LNSGKGSNL w - 1'  
'両桂香': 'sfen 11sgkgs11/1r5b1/ppppppppp/9/9/9/PPPPPPPPP/1B5R1/LNSGKGSNL w - 1'  
'飛': 'sfen lnsgkgsnl/7b1/ppppppppp/9/9/9/PPPPPPPPP/1B5R1/LNSGKGSNL w - 1'  
'角': 'sfen lnsgkgsnl/1r7/ppppppppp/9/9/9/PPPPPPPPP/1B5R1/LNSGKGSNL w - 1'  
'飛香': 'sfen lnsgkgsn1/7b1/ppppppppp/9/9/9/PPPPPPPPP/1B5R1/LNSGKGSNL w - 1'  
'飛右香': 'sfen 1nsgkgsnl/7b1/ppppppppp/9/9/9/PPPPPPPPP/1B5R1/LNSGKGSNL w - 1'  
'角香': 'sfen lnsgkgsn1/1r7/ppppppppp/9/9/9/PPPPPPPPP/1B5R1/LNSGKGSNL w - 1'  
'角右香': 'sfen 1nsgkgsnl/1r7/ppppppppp/9/9/9/PPPPPPPPP/1B5R1/LNSGKGSNL w - 1'  
'飛角': 'sfen lnsgkgsnl/9/ppppppppp/9/9/9/PPPPPPPPP/1B5R1/LNSGKGSNL w - 1'

# 駒落ちに関する仮説

## 駒落ち平等の法則

- 同じ駒落ちなら誰に対しても同じR低下がもたらされるというもの。

## 駒落ち対称性の破れ

(検証中)

## 駒落ち非線形仮説

(検証中)

# 駒落ちR低下関数fを導出する

- f(香)=90のような関数fを作成したい。

非線形仮説から  
f(x, y) = f(x) + f(y) + α  
とかける。

