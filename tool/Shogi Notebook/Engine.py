import subprocess
import time
import os

class Engine:
    # コンストラクタ
    def __init__(self, engine, debug=False):
        self.engine_cmd = engine["engine_cmd"]
        self.temp = engine["stdout"]
        self.option = engine["option"]
        self.debug = debug # Trueならデバッグ用の出力をする
        self.__dprint("on")

    # デバッグプリント用
    def __dprint(self, string):
        if self.debug:
            print(f"[Debug] {string}")

    # エンジンにコマンド列を送る
    def __stdin(self, cmd):
        print(cmd, file=self.p.stdin, flush=True)

    # エンジンの初期化
    def init_engine(self):
        if os.path.isfile(self.temp): #tempファイルの存在確認
            os.remove(self.temp) # 存在していれば消す
        self.fw = open(self.temp, 'a') # 標準出力用にファイルを書き込みで開く
        self.fr = open(self.temp, 'r') # 読み込みでファイルを開く
        self.stat = os.stat(self.temp) # ファイルの情報を取得
        self.__dprint(f"size={self.stat.st_size}")
        self.p = subprocess.Popen(self.engine_cmd, stdin=subprocess.PIPE, stdout=self.fw, stderr=subprocess.PIPE, universal_newlines=True)
        # usiコマンドとその応答確認
        self.__stdin('usi')
        if not self.__polling_file(0.05, 0.3, 5):
            self.__kill()
            return False
        if not self.__check_usi(self.get_stdout_lines()):
            self.__kill()
            return False

        # エンジンにオプションセット用のコマンド列を送る
        self.__setopt()

        # isreadyコマンドとその応答確認
        self.__stdin('isready')
        if not self.__polling_file(0.05, 0.5, 10):
            self.__kill()
            return False
        if not self.__check_isready(self.get_stdout_lines()):
            self.__kill()
            return False
        return True

    # オプションをセットする
    def __setopt(self):
        for option in self.option:
            self.__stdin(option)
        self.__dprint("オプションをセットしました")

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
                return True
            elif ls[0:8] == "id name ":
                print(f"ID:「{ls[8:]}」")
            elif ls[0:13] == "id author by ":
                print(f"author:「{ls[13:]}」")
        self.__dprint("usiokを確認できませんでした")
        return False

    # isreadyコマンドの結果を確認する
    def __check_isready(self, isready):
        for l in isready:
            ls = l[:-1]
            if ls == "readyok":
                print(f"READY： OK")
                return True
            elif ls[0:12] == "info string ":
                self.__dprint(f"{ls[13:]}")
        self.__dprint("readyokを確認できませんでした")
        return False

    # goコマンドの結果を確認する
    def __check_go(self, go):
        for l in go:
            ls = l[:-1]
            if ls[0:5] == "info ":
                self.__dprint(ls[5:])
            elif ls[0:9] == "bestmove ":
                ls_list = ls.split(" ")
                print(f"bestmove: {ls_list[1]}")
                return True
        return False

    def sfen_think(self, sfen, time_):
        self.__stdin(sfen)
        s = "go btime " + str(time_) + " wtime " + str(time_)
        self.__stdin(s)
        if not self.__polling_file(2, 1, 10):
            self.__kill()
            return
        if not self.__check_go(self.get_stdout_lines()):
            self.__kill()
            return

    def get_stdout_lines(self):
        return self.fr.readlines()

    # エンジンの終了とファイルのクローズ
    def quit(self):
        self.__stdin('quit')
        self.fr.close()
        self.fw.close()

    # 何らかのエラーのときに強制終了させる
    def __kill(self):
        self.quit()
        self.__dprint("強制終了しました")
