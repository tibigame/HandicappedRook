from typing import Tuple


def xor(x: bool, y: bool)-> bool:
    """排他的論理和"""
    return x and not y or not x and y


def reverse_bw(pos: Tuple[int, int], is_black=True) -> Tuple[int, int]:
    """先後の符号を反転したタプルを返す"""
    if is_black:
        return pos
    return (10 - pos[0], 10 - pos[1])


def d_print(string: str, debug_str="[Debug] ", is_debug=False):
    """デバッグプリント用"""
    if is_debug:
        print(f"{debug_str + string}")
