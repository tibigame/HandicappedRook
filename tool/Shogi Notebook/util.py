def xor(x: bool, y: bool)-> bool:
    """排他的論理和"""
    return x and not y or not x and y


def d_print(string: str, debug_str="[Debug] ", is_debug=False):
    """デバッグプリント用"""
    if is_debug:
        print(f"{debug_str + string}")
