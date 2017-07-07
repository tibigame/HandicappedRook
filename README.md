﻿# HandicappedRook

振り飛車は本当に不利なのかを検証するプロジェクトです。

## 使い方

bookにある定跡をやねうら王の学習ルーチンに食わせてゼロベクトルから学習を行ってください。

## 評価関数

振り飛車定跡で絞った評価関数です。
やねうら王などで使用できます。

- [v3.0:2017/7/7](https://drive.google.com/file/d/0BwUOadFWQqvjYXoxQ0ZValFkUHc/view?usp=sharing)
- [v2.0:2017/7/3](https://drive.google.com/file/d/0BwUOadFWQqvjUFVIMW8xX0dBa28/view?usp=sharing)
- [v1.0:2017/6/30](https://drive.google.com/file/d/0BwUOadFWQqvjVFFmYnRIODdsbGc/view?usp=sharing)

## book

- standard_book.db 教師局面生成用の定跡です。
- user_book1.db 対局用に居飛車を指さないようにする定跡です。

## 現時点でわかっていること

- 振り飛車が不利という結論は覆せていない。
- depthが少ない状態での技巧2との対戦から振り飛車の教師局面が少ない評価関数は振り飛車の局面をうまく評価できないなどの
レーティングを超えた評価関数の相性はありそうだというのがわかったが、
まふ評価関数クラスに対してそれがあるのかは不明。
- ここから先に進むには定跡を何とかする必要がある。

## 作成した定跡について

プロの棋譜、floodgate、棋書などを参考に以下の戦型の序盤定跡を作成した。

ゼロベクトルからの学習にあたっては定跡は大筋だけ与えればいいという考えである。

- 向かい飛車
	- ダイレクト向かい飛車
		- ▲７五金型
		- ▲６五角スルー型
		- ゴキ中偽装型角打ち乱戦
	- 鬼殺し向かい飛車
	- 阪田流向かい飛車
	- メリケン向かい飛車
- 三間飛車
	- 初手▲７八飛戦法
	- ２手目△３二飛戦法
	- 升田式石田流
	- 早石田VS棒金
	- 早石田鈴木流
	- ノーマル三間飛車 VS 左美濃
	- 三間飛車 VS 中飛車左穴熊
	- コーヤン流
	- トマホーク
	- 糸谷流右玉
- 四間飛車
	- 先手藤井システム
	- 後手藤井システム
	- 山田定跡
	- 鷺宮定跡
	- 加藤流棒銀
	- 右銀急戦
	- 富沢キック
	- ▲４五歩早仕掛け郷田流
	- elmo式急戦
	- ノーマル四間飛車持久戦
		- 天守閣美濃
		- ▲６六角～銀冠穴熊
		- クラシック穴熊
		- 松尾流穴熊
		- 4枚穴熊
		- 銀冠
		- ミレニアム
	- 角交換四間飛車
	- クルクル角
	- 地下鉄飛車
- 中飛車
	- 先手中飛車
		- 居合い抜き超速
		- ５五龍中飛車
	- ゴキゲン中飛車
		- 超急戦
		- 超速▲３七銀
		- 丸山ワクチン
- 相振り飛車
	- 相三間飛車
		- 相金無双
		- 阿部流
	- 角交換四間飛車 VS 向かい飛車
	- ノーマル四間飛車 VS 三間飛車

## 棋風などメモ

### v3 (depth=6、5億局面)
- v2に毛が生えた程度。
- まふ評価関数には完敗。

### v2 (depth=6、4億局面)
- やっぱり端歩突きたがる。
- elmo相手にはまだまだ力負けするが技巧2相手には一発入るクラスから互角レベルまで育ってるとみえる。

### v1 (depth=3、数億局面、数周)
- 向かい飛車にしたがる。端歩を突きたがる。玉を囲わないまま戦いたがる。
- 振り飛車のみを学習させても振り飛車は不利と自己評価するようである。
- 居飛車畑でしか育ってない評価関数相手には中盤で逆転することも。
- depth=3でしか絞ってないので終盤力はないです。 (逆にまだまだ可能性あり)

## 開発メモ

- 無限絞り等を行うに当たって定跡の精査が必要になると思われる。
なぜなら既存の定跡の検証はelmoや技巧2などの居飛車の教師局面が多い評価関数によって行われているからである。
よってある程度強くなったら定跡を自力で再検証して有望なものを抽出する必要がある。
- 二手損居飛車対策をしないといけない。
- 定跡外し戦術で容易に相居飛車戦にされる。6手目ぐらいまでは全ての合法手の定跡作る？

