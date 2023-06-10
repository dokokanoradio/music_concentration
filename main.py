import random
import itertools
from typing import List, Tuple, Optional, Final, Protocol
import time
from enum import Enum, unique
from dataclasses import dataclass
import csv

# Config項目
GAMES: Final[int] = 1000000  # シミュレーションするゲーム数
MAX_TRY: Final[int] = 3  # 1ゲームにつき何度挑戦するか？(3回)

CSV_BARA: Final[str] = "result_barabara.csv"  # バラバラの実行結果のCSVファイル名
CSV_KOTEI: Final[str] = "result_kotei.csv"  # 固定の実行結果のCSVファイル名
OUTPUT_INTERVAL = 1  # CSVへの出力間隔(指定した回数に1回の割合で出力。1だと毎回)
INTERVAL_OFFSET = 0  # 出力間隔のオフセット(出力をずらしたいとき用。通常は0でよい)


@unique
class Music(Enum):
    """音楽の定義(Enum)

    通常であれば5曲の異なる曲を選曲する
    """

    # 以下5曲を定義(曲名は異なっていればなんでもよい:デバッグ用)
    MUSIC_A: str = "A"
    MUSIC_B: str = "B"
    MUSIC_C: str = "C"
    MUSIC_D: str = "D"
    MUSIC_E: str = "E"

    @classmethod
    def get_list(cls) -> list["Music"]:
        """神経衰弱する音楽のリストを取得

        Returns:
            list[Music]: 音楽のリスト(5曲のリスト)
        """
        return [e for e in cls]

    @classmethod
    def get_len(cls) -> int:
        """神経衰弱に使う音楽の曲数を取得

        Returns:
            int: 曲数(5曲)
        """
        return len(Music.get_list())


@dataclass(frozen=True)
class Call:
    """前1、後2のような前/後半のコールを表す

    ゲーム時にリスナーがコールする内容を表す
    """

    first: int  # 前(前1-前5)
    second: int  # 後(後1-後5)


@dataclass(frozen=True)
class PlayResult:
    """前1、後2などのコール後に流れる前後半の曲を表す

    コールに合わせてスタッフが流す音楽を表す
    """

    first: Music  # 前半の曲
    second: Music  # 後半の曲


class Staff:
    """番組スタッフ(ゲームの出題者)を表す

    ゲームにおいては以下の役割を持つ
    * 番号と曲の対応付けを決める(ランダム)
    * 曲を流す
    * リスナーのコールに対する正解判定
    """

    # 1～5の数字に対応する曲の組み合わせを全パターン列挙(120通り)したもの
    MUSIC_PERMUTATIONS: Final[List[Tuple[Music, ...]]] = list(
        itertools.permutations(Music.get_list())
    )

    def __init__(self) -> None:
        """インスタンス初期化"""

        # インスタンス変数の初期化
        # 前後半それぞれ、取りうる曲の組み合わせからランダムに1つ選ぶ
        # これにより、前1～5、後1～5に対応する曲が決まる
        self.music_perm_first: Tuple[Music, ...] = random.choice(
            Staff.MUSIC_PERMUTATIONS
        )
        self.music_perm_second: Tuple[Music, ...] = random.choice(
            Staff.MUSIC_PERMUTATIONS
        )

    def play_music(self, call: Call) -> PlayResult:
        """音楽を流す

        コールに対応する音楽を取り出す
        Args:
            call (Call): コール

        Returns:
            PlayResult: 音楽を流した結果
        """

        return PlayResult(
            # コールは1始まり、Pythonのindexは0始まりなので1引く
            self.music_perm_first[call.first - 1],
            self.music_perm_second[call.second - 1],
        )

    def judge(self, result: PlayResult) -> bool:
        """流した曲の正誤判定

        前後共に同じ曲が流れれば正解となる
        Args:
            result (PlayResult): 流した曲

        Returns:
            bool: 正解ならTrue, 失敗ならFalse
        """
        return result.first == result.second


class Storategy(Protocol):
    """コールのためのI/F定義用Protocolクラス"""

    def call_nth(self, nth: int) -> Call:
        """nth回目のコールを行う

        Args:
            nth (int): nth回目のコール(初回は1。1～MAX_TRYの範囲)

        Returns:
            Call: コール内容
        """
        ...

    def receive_result_nth(self, nth: int, result: PlayResult) -> None:
        """nth回目のコールに対応する音楽を受け取る

        Args:
            nth (int): nth回目のコール(初回は1。1～MAX_TRYの範囲)
            result (PlayResult): nth回目のコールに対する音楽
        """
        ...


class Listener:
    """リスナー(ゲームの回答者)を表す

    ゲームにおいて、前？、後？のコールを行う役割
    """

    # コールに使える番号を列挙したリスト[1,2,3,4,5]
    NO_LIST: Final[List[int]] = [i + 1 for i in range(Music.get_len())]  # 0始まりなので1足す

    # 取りうるコールを列挙したリスト。前1後1～前5後5までの25通り
    CALL_LIST: Final[List[Call]] = [
        Call(first, second) for first, second in itertools.product(NO_LIST, NO_LIST)
    ]

    def __init__(self, strategy: Storategy) -> None:
        """インスタンス初期化

        Args:
            strategy (Storatagy): Callのストラテジ(戦略)
        """

        # インスタンス変数の初期化
        self.storatagy: Storategy = strategy

    def call_nth(self, nth: int) -> Call:
        """N回目のコールを行う

        Args:
            nth (int): N回目(1～MAX_TRY)

        Raises:
            ValueError: コールの値が範囲外(実装ミスが無いと起きない)

        Returns:
            Call: コールに対応する前後の数字
        """

        # ポカヨケ(ありえない回数のコールは例外で強制終了)
        # TODO: 1から順番に呼ばれているかの判定を入れても良いが現状は未実装
        #       (回数の管理責務はgameにあるので過剰すぎる気もする)
        if not (1 <= nth <= MAX_TRY):
            raise ValueError

        # 以降(1<=nth<=MAX_TRY)の時のみ実行

        return self.storatagy.call_nth(nth)  # storategy側に移譲

    def receive_result_nth(self, nth: int, result: PlayResult) -> None:
        """リスナーがコールした結果(対応する音楽)を受け取る

        Args:
            nth (int): N回目(1～MAX_TRY)
            result (PlayResult): nth回目のコールに対応する音楽

        Raises:
            ValueError: コールの値が範囲外(実装ミスが無いと起きない)
        """

        # ポカヨケ(ありえない回数のコールは例外で強制終了)
        # TODO: 1から順番に呼ばれているかの判定を入れても良いが現状は未実装
        #       (回数の管理責務はgameにあるので過剰すぎる気もする)
        if not (1 <= nth <= MAX_TRY):
            raise ValueError

        # 以降(1<=nth<=MAX_TRY)の時のみ実行

        return self.storatagy.receive_result_nth(nth, result)  # storategy側に移譲


class BaraBara:
    """コール戦略(2回目バラバラ)"""

    def __init__(self) -> None:
        # インスタンス変数の初期化
        # (ポカヨケのため意図的にNone)
        # TODO:データ構造は考え直しても良いかも

        # コールした前後の数字と結果(1回目をindex1とするため意図的に+1)
        # ※最終トライ(通常は3回目)は記憶不要なので本来は2要素あれば十分
        self.no_try: List[Optional[Call]] = [None] * (MAX_TRY + 1)
        self.result_try: List[Optional[PlayResult]] = [None] * (MAX_TRY + 1)

    def call_nth(self, nth: int) -> Call:
        """N回目のコールを行う

        Args:
            nth (int): N回目(1～3)

        Raises:
            ValueError: コールの値が範囲外(実装ミスが無いと起きない)

        Returns:
            Call: コールに対応する前後の数字
        """

        if nth == 1:
            return self.call_try1()
        elif nth == 2:
            return self.call_try2()
        elif nth == 3:
            return self.call_try3()
        else:
            raise ValueError

    def call_try1(self) -> Call:
        """1回目のコール

        Returns:
            Call: コール結果
        """

        # 全パターンからランダムに1つ選ぶ
        call_list = Listener.CALL_LIST  # 25通りが候補
        target = random.choice(call_list)

        self.no_try[1] = target  # 1回目のコール内容を記憶

        return target

    def call_try2(self) -> Call:
        """2回目のコール

        Raises:
            TypeError: 1回目のコール結果が記憶されていない(実装ミスが無いと起きない)

        Returns:
            Call: コール結果
        """

        no_try1 = self.no_try[1]  # 1回目のコール
        # ポカヨケ
        if no_try1 is None:
            raise TypeError

        # 前、後共に1回目に選んでいない数字より選択(5曲なら4*4=16通り)
        call_list = [
            e
            for e in Listener.CALL_LIST
            if e.first != no_try1.first and e.second != no_try1.second
        ]
        target = random.choice(call_list)

        self.no_try[2] = target  # 2回目のコール内容を記憶
        return target

    def call_try3(self) -> Call:
        no_try1 = self.no_try[1]
        no_try2 = self.no_try[2]
        result_try1 = self.result_try[1]
        result_try2 = self.result_try[2]

        # ポカヨケ
        if (
            no_try1 is None
            or no_try2 is None
            or result_try1 is None
            or result_try2 is None
        ):
            raise TypeError

        if result_try1.first == result_try2.second:
            # 1回目の前と2回目の後ろが一致
            target = Call(no_try1.first, no_try2.second)
        elif result_try2.first == result_try1.second:
            # 2回目の前と1回目の後ろが一致
            target = Call(no_try2.first, no_try1.second)
        else:
            # 1,2回目のコールで番号が特定できなかったので、前固定の3択(ランダム)
            call_list = [
                e
                for e in Listener.CALL_LIST
                if e.first == no_try1.first  # 前は1回目にコールした番号
                and e.second != no_try1.second  # かつ後は1回目にコールした番号"ではない"
                and e.second != no_try2.second  # かつ後ろは2回目にコールした番号"ではない"
            ]
            target = random.choice(call_list)

        return target

    def receive_result_nth(self, nth: int, result: PlayResult) -> None:
        """nth回目のコールに対応する結果を受け取る

        Args:
            nth (int): N回目(1～MAX_TRY)
            result (PlayResult): nth回目のコールに対応する音楽

        Raises:
            ValueError: コールの値が範囲外(実装ミスが無いと起きない)
        """
        self.result_try[nth] = result


class Kotei:
    """コール戦略(前固定)

    ゲームにおいて、前？、後？のコールを行う役割
    """

    def __init__(self) -> None:
        # インスタンス変数の初期化
        # (ポカヨケのため意図的にNone)
        # TODO:データ構造は考え直しても良いかも

        # コールした前後の数字と結果(1回目をindex1とするため意図的に+1)
        # ※最終トライ(通常は3回目)は記憶不要なので本来は2要素あれば十分
        self.no_try: List[Optional[Call]] = [None] * (MAX_TRY + 1)
        self.result_try: List[Optional[PlayResult]] = [None] * (MAX_TRY + 1)

    def call_nth(self, nth: int) -> Call:
        """N回目のコールを行う

        Args:
            nth (int): N回目(1～3)

        Raises:
            ValueError: コールの値が範囲外(実装ミスが無いと起きない)

        Returns:
            Call: コールに対応する前後の数字
        """

        if nth == 1:
            return self.call_try1()
        elif nth == 2:
            return self.call_try2()
        elif nth == 3:
            return self.call_try3()
        else:
            raise ValueError

    def call_try1(self) -> Call:
        """1回目のコール

        Returns:
            Call: コール結果
        """

        # 全パターンからランダムに1つ選ぶ
        call_list = Listener.CALL_LIST  # 25通りが候補
        target = random.choice(call_list)

        self.no_try[1] = target  # 1回目のコール内容を記憶

        return target

    def call_try2(self) -> Call:
        """2回目のコール

        Raises:
            TypeError: 1回目のコール結果が記憶されていない(実装ミスが無いと起きない)

        Returns:
            Call: コール結果
        """

        no_try1 = self.no_try[1]  # 1回目のコール

        # ポカヨケ
        if no_try1 is None:
            raise TypeError

        # 前は1回目と同じ、後は1回目と異なるものから選択(5曲の場合4択)
        call_list = [
            e
            for e in Listener.CALL_LIST
            if e.first == no_try1.first and e.second != no_try1.second
        ]
        target = random.choice(call_list)

        self.no_try[2] = target  # 2回目のコール内容を記憶
        return target

    def call_try3(self) -> Call:
        no_try1 = self.no_try[1]  # 1回目のコール
        no_try2 = self.no_try[2]  # 2回目のコール
        result_try1 = self.result_try[1]  # 1回目の結果
        result_try2 = self.result_try[2]  # 2回目の結果

        # ポカヨケ
        if (
            no_try1 is None
            or no_try2 is None
            or result_try1 is None
            or result_try2 is None
        ):
            raise TypeError

        # 前は1回目と同じ、後は1回目/2回目と異なるものから選択(5曲の場合3択)
        call_list = [
            e
            for e in Listener.CALL_LIST
            if e.first == no_try1.first
            and e.second != no_try1.second
            and e.second != no_try2.second
        ]
        target = random.choice(call_list)

        return target

    def receive_result_nth(self, nth: int, result: PlayResult) -> None:
        """nth回目のコールに対応する結果を受け取る

        Args:
            nth (int): N回目(1～MAX_TRY)
            result (PlayResult): nth回目のコールに対応する音楽

        Raises:
            ValueError: コールの値が範囲外(実装ミスが無いと起きない)
        """
        self.result_try[nth] = result


class Game:
    """スタッフ(出題者)とリスナー(回答者)のやり取りを定義する

    ゲームの流れを定義することになる
    """

    def __init__(self, storatagy: Storategy) -> None:
        # インスタンス変数初期化
        self.staff = Staff()  # Staff
        self.listener = Listener(storatagy)  # Listener
        self.try_count = 1  # try_game()のN回目の呼び出し(初回呼び出しで1)

    def try_game(self) -> bool:
        """音楽神経衰弱を1回トライさせる

        Raises:
            ValueError: トライ回数が範囲外(実装ミスが無いと起きない)

        Returns:
            bool: 成功(当たり)ならTrue, 失敗(外れ)ならFalse
        """

        # インスタンス変数をローカルにキャッシュ(可読性都合上)
        staff = self.staff
        listener = self.listener
        try_count = self.try_count

        # ポカヨケ(最大で3回までトライ可)
        if not (1 <= try_count <= MAX_TRY):
            raise ValueError  # 例外で強制終了

        # 以降1～3回目の時のみ実行

        # 1)リスナーにコールさせる
        call_tryn = listener.call_nth(try_count)

        # 2)スタッフがコールに対応する音楽を流す
        play_result_tryn = staff.play_music(call_tryn)

        # 3)曲を流した結果で正誤判定
        judge_res = staff.judge(play_result_tryn)

        # 後処理1)次回以降の戦略を考えるため、リスナーに対してコールに対応する曲を教える
        listener.receive_result_nth(try_count, play_result_tryn)

        # 後処理2)1回分のトライが終わったので実行回数を1増やす
        self.try_count = try_count + 1

        return judge_res


class Counter:
    """カウンタ用のクラス"""

    def __init__(self) -> None:
        self.pass_count: int = 0  # 成功
        self.fail_count: int = 0  # 失敗

    def count_pass(self) -> None:
        """成功回数をインクリメント"""
        self.pass_count += 1

    def count_fail(self) -> None:
        """失敗回数をインクリメント"""
        self.fail_count += 1

    def get_pass(self) -> int:
        """成功回数を取得

        Returns:
            int: 成功回数
        """
        return self.pass_count

    def get_fail(self) -> int:
        """失敗回数を取得

        Returns:
            int: 失敗回数
        """
        return self.fail_count

    def get_total(self) -> int:
        """実行回数を取得

        Returns:
            int: 実行回数(成功＋失敗)
        """
        return self.pass_count + self.fail_count

    def get_percentage(self) -> float:
        """成功確率[%]を取得

        Returns:
            float: 成功確率[%](実行回数0の場合は0.0)
        """
        pass_count = self.get_pass()
        total = self.get_total()
        return (pass_count / total) * 100.0 if total > 0 else 0.0

    def csv_row(self) -> Tuple[int, int, float]:
        """CSV出力用の行を生成

        TODO:本来であればここで実装するのではなくて、別クラスで実装すべき(手間なので後回し)

        Returns:
            Tuple[int, int, float]:  CSV出力用の行データ
        """

        # (実行回数, 成功回数, 成功確率)
        return (self.get_total(), self.get_pass(), self.get_percentage())

    def summary(self) -> str:
        """_カウント結果のサマリ文字列を生成

        Returns:
            str: カウント結果のサマリ文字列
        """
        pass_count: int = self.get_pass()  # 成功数
        fail_count: int = self.get_fail()  # 失敗数
        total_count: int = self.get_total()  # カウント総数
        per: float = self.get_percentage()  # 成功確率

        return f"{total_count}回中{pass_count}回成功 {fail_count}回失敗 確率{per}[%]"


def main() -> None:
    """main関数

    音楽神経衰弱をGAMES回実行してその結果を表示
    """
    # CSVのヘッダ行
    csv_header_row = ("total", "pass", "percentage")  # 実行回数、成功回数、成功確率

    # 出力タイミングの値を計算(剰余が指定した値になると出力)
    output_val = (OUTPUT_INTERVAL - 1) + INTERVAL_OFFSET

    start = time.time()  # 計測開始

    # バラバラの場合の計算
    counter_bara = Counter()  # バラバラのカウンタ
    with open(CSV_BARA, newline="", mode="w") as file_bara:
        # CSVOpen
        csv_bara = csv.writer(file_bara)  # バラバラ

        # ヘッダ行出力
        csv_bara.writerow(csv_header_row)

        for i in range(GAMES):
            # 1ゲーム実行
            exec_game(exec_storatagy=BaraBara(), counter=counter_bara)

            # 指定したタイミングでCSV出力
            if i % OUTPUT_INTERVAL == output_val:
                csv_bara.writerow(counter_bara.csv_row())
        # end for loop
    # close file

    # 固定の場合の計算
    counter_kotei = Counter()  # 固定のカウンタ
    with open(CSV_KOTEI, newline="", mode="w") as file_kotei:  # fmt: skip
        # CSVOpen
        csv_kotei = csv.writer(file_kotei)  # 固定

        # ヘッダ行出力
        csv_kotei.writerow(csv_header_row)

        for i in range(GAMES):
            # 1ゲーム実行
            exec_game(exec_storatagy=Kotei(), counter=counter_kotei)

            # 指定したタイミングでCSV出力
            if i % OUTPUT_INTERVAL == output_val:
                csv_kotei.writerow(counter_kotei.csv_row())
        # end for loop
    # close file

    end = time.time()  # 計測終了

    print(f"処理時間：{end-start}[SEC]")
    print(f"バラバラ：{counter_bara.summary()}")
    print(f"固定：{counter_kotei.summary()}")


def exec_game(exec_storatagy: Storategy, counter: Counter) -> None:
    """音楽神経衰弱を1回実行

    Args:
        exec_storatagy (Storategy): リスナーの戦略
        counter (Counter): 実行回数のカウンタ
    """

    game = Game(storatagy=exec_storatagy)

    # 以降、最大3回トライさせ、成功or失敗のカウントを行う
    # TODO:本来ならループで回すべき...

    # 1回目の挑戦
    if game.try_game():
        # 1回目で成功
        counter.count_pass()
    else:
        # 1回目失敗

        # 2回目の挑戦
        if game.try_game():
            # 2回目で成功
            counter.count_pass()
        else:
            # 2回目失敗

            # 3回目の挑戦
            if game.try_game():
                # 3回目で成功
                counter.count_pass()
            else:
                # 3回目で失敗
                counter.count_fail()


if __name__ == "__main__":
    main()
