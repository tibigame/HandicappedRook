import subprocess
import time
import os

class Info:
    def __init__(self, info_str):
        info_flag = ""
        for info_elm in info_str[5:].split(" "):
            if info_flag == "depth":
                info_flag = ""
                self.depth = info_elm
            elif info_elm == "depth":
                info_flag = "depth"
            elif info_flag == "seldepth":
                info_flag = ""
                self.seldepth = info_elm
            elif info_elm == "seldepth":
                info_flag = "seldepth"
            elif info_flag == "multipv":
                info_flag = ""
                self.multipv = info_elm
            elif info_elm == "multipv":
                info_flag = "multipv"
            elif info_flag == "score":
                if info_elm == "cp":
                    info_flag = "cp"
                else:
                    info_flag = "mate"
            elif info_flag == "cp":
                info_flag = ""
                self.score = info_elm
            elif info_flag == "mate":
                info_flag = ""
                self.mate = info_elm
            elif info_elm == "score":
                info_flag = "score"
            elif info_flag == "nodes":
                info_flag = ""
                self.nodes = info_elm
            elif info_elm == "nodes":
                info_flag = "nodes"
            elif info_flag == "nps":
                info_flag = ""
                self.nps = info_elm
            elif info_elm == "nps":
                info_flag = "nps"
            elif info_flag == "time":
                info_flag = ""
                self.time = info_elm
            elif info_elm == "time":
                info_flag = "time"
            elif info_flag == "pv":
                self.pv.append(info_elm)
            elif info_elm == "pv":
                info_flag = "pv"
                self.pv = []

    def get_score(self) -> str:
        """評価値の文字列かmateを返す"""
        if hasattr(self, "score"):
            return self.score
        if hasattr(self, "mate"):
            return f"mate {self.mate}"
        return "0"

    def get_score_val(self) -> int:
        """評価値を整数値で返す"""
        if hasattr(self, "score"):
            return int(self.score)
        if hasattr(self, "mate"):
            m = int(self.mate)
            if m == 0 or m == 1 or m == -1:
                return 0
            return 2**15 if m >= 0 else -2**15
        return 0

class Engine:
    # コンストラクタ
    def __init__(self, engine, debug=False):
        self.cwd = engine["cwd"]
        self.engine_cmd = engine["engine_cmd"]
        self.temp = engine["stdout"]
        self.option = engine["option"]
        self.debug = debug # Trueならデバッグ用の出力をする
        self.__dprint("on")

    # デバッグプリント用
    def __dprint(self, string: str):
        if self.debug:
            print(f"[Debug] {string}")

    # エンジンにコマンド列を送る
    def __stdin(self, cmd: str):
        print(cmd, file=self.p.stdin, flush=True)

    # オプションをセットする
    def __setopt(self):
        for option in self.option:
            self.__stdin(option)
        self.__dprint("オプションをセットしました")

    # コマンドの実行と確認
    def __exe_and_check_cmd(self, cmd: str, check, polling, times=1, kill=True):
        self.__stdin(cmd)
        l = 0
        while True:
            l += 1
            if self.__polling_file(polling[0], polling[1], polling[2]): # ファイルが更新されたら
                result = check(self.get_stdout_lines()) # ファイルを読みに行く
                if result[0]: # ファイルを読みに行って結果をチェックルーチンに渡す
                    return (True, result[1]) # 成功, 結果はresult[1]に格納
            if l >= times: # 規定回数のループで成功しなかった
                if kill: # killフラグがTrueのときは失敗時にkill処理を実行する
                    self.__kill()
                return (False, False)

    # エンジンの初期化
    def init_engine(self):
        if os.path.isfile(self.temp): #tempファイルの存在確認
            os.remove(self.temp) # 存在していれば消す
        self.fw = open(self.temp, 'a') # 標準出力用にファイルを書き込みで開く
        self.fr = open(self.temp, 'r') # 読み込みでファイルを開く
        self.stat = os.stat(self.temp) # ファイルの情報を取得
        self.__dprint(f"size={self.stat.st_size}")
        self.p = subprocess.Popen(self.engine_cmd, stdin=subprocess.PIPE, stdout=self.fw, stderr=subprocess.PIPE, universal_newlines=True, cwd=self.cwd)
        # usiコマンドとその応答確認
        if not self.__exe_and_check_cmd("usi", self.__check_usi, (0.05, 0.3, 5))[0]:
            return False

        # エンジンにオプションセット用のコマンド列を送る
        self.__setopt()

        # isreadyコマンドとその応答確認
        return self.__exe_and_check_cmd("isready", self.__check_isready, (0.05, 0.5, 10), 10, True)[0]

    def usinewgame(self):
        self.__stdin("usinewgame")

    def gameover(self, param="draw"):
        self.__stdin("gameover " + param)

    # 標準出力ファイルが更新されたかを確認する
    def __is_update_stdout(self):
        new_stat = os.stat(self.temp) # 現在のファイル情報を取得
        if self.stat.st_size != new_stat.st_size: # ファイルサイズが異なれば更新されたということ
            self.stat = new_stat # ファイル情報を最新のものにする
            self.__dprint(f"size={new_stat.st_size}")
            self.__dprint("ファイルが更新されました")
            return True
        return False

    # offset秒待ってからtimes回interval秒ごとにファイル更新をチェックする (正しくポーリングされていないっぽい)
    def __polling_file(self, offset, interval, times):
        time.sleep(offset)
        for t in range(times):
            time.sleep(interval)
            if self.__is_update_stdout():
                self.__dprint(f"__polling_file:{t}回目のループ")
                return True
        # タイムアウト
        self.__dprint("ファイルの更新を確認できませんでした")
        return False

    # usiコマンドの結果を確認する
    def __check_usi(self, usi):
        for l in usi:
            ls = l[:-1]
            if ls == "usiok":
                print(f"USIコマンド： OK")
                return (True, "usiok")
            elif ls[0:8] == "id name ":
                print(f"ID:「{ls[8:]}」")
            elif ls[0:13] == "id author by ":
                print(f"author:「{ls[13:]}」")
        self.__dprint("usiokを確認できませんでした")
        return (False, False)

    # isreadyコマンドの結果を確認する
    def __check_isready(self, isready):
        for l in isready:
            ls = l[:-1]
            if ls == "readyok":
                print(f"READY： OK")
                return (True, "readyok")
            elif ls[0:12] == "info string ":
                self.__dprint(f"{ls[13:]}")
        self.__dprint("readyokを確認できませんでした")
        return (False, False)

    # goコマンドの結果を確認する
    def __check_go(self, go):
        info_list = []
        for l in go:
            ls = l[:-1]
            if ls[0:5] == "info ":
                self.__dprint(ls[5:])
                info_list.append(Info(ls))
            elif ls[0:9] == "bestmove ":
                ls_list = ls.split(" ")
                print_str = f"bestmove: {ls_list[1]}"
                if len(info_list) >= 1:
                    print_str += f" {info_list[-1].get_score()}"
                print(print_str)
                return (True, (ls_list[1], info_list))
        return (False, False)

    def go_think(self, sfen, time_):
        self.__dprint(sfen)
        self.__stdin(sfen)
        s = "go btime 0 wtime 0 byoyomi " + str(time_)
        return self.__exe_and_check_cmd(s, self.__check_go, (time_/1000, time_/3000, 10), 10)

    # 深さベースの思考。time_refは参考思考時間
    def go_depth(self, sfen, depth, time_ref=5):
        self.__stdin(sfen)
        s = "go depth {str(depth)}"
        return self.__exe_and_check_cmd(s, self.__check_go, (1, time_ref, 10), 10)

    # time_秒間詰将棋を考える
    def go_mate(self, sfen, time_):
        self.__stdin(sfen)
        s = f"go mate {str(time_ * 1000)}"
        return self.__exe_and_check_cmd(s, self.__check_go_mate, (1, 1, time_), 10)

    # go_mateコマンドの結果を確認する
    def __check_go_mate(self, go):
        for l in go:
            ls = l[:-1]
            if ls[0:5] == "info ":
                self.__dprint(ls[5:])
            elif ls[0:10] == "checkmate ":
                ls_list = ls.split(" ")
                print(f"checkmate: {ls_list[1:]}")
                return (True, ls_list[1:]) # 詰将棋の解答
        return (False, False)

    # benchコマンドとその応答確認
    def bench(self):
        self.__exe_and_check_cmd("bench 1024 1 10 default depth", self.__check_bench, (10, 1, 10), 1, True)

    # benchコマンドの結果を確認する
    def __check_bench(self, bench):
        for l in bench:
            ls = l[:-1]
            print(ls)
        return True

    def get_stdout_lines(self):
        return self.fr.readlines()

    # エンジンの思考停止
    def stop(self):
        self.__stdin('stop')

    # エンジンの終了とファイルのクローズ
    def quit(self):
        self.__stdin('quit')
        self.fr.close()
        self.fw.close()

    # 何らかのエラーのときに強制終了させる
    def __kill(self):
        self.quit()
        self.__dprint("強制終了しました")
