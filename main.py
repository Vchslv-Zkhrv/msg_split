import re as _re

import click as _click
import colorama as _colors

from msg_split import split_msg


def _print_delimeter(number: int, size: int) -> None:
    print(
        _colors.Fore.BLUE,
        f"-- fragment #{number}: {size} chars --",
        _colors.Style.RESET_ALL
    )


def _print_html(html: str) -> None:
    """
    Prints text with HTML syntax highlight
    """
    html = _re.sub(
        r"\<", f"{_colors.Fore.LIGHTBLACK_EX}<", html
    )
    html = _re.sub(
        r"\>", f"{_colors.Fore.LIGHTBLACK_EX}>{_colors.Style.RESET_ALL}", html
    )
    print(html)


@_click.command()
@_click.argument('source')
@_click.option('--max-len', default=4096, help='max message lenght')
def main(source: str, max_len: int) -> None:
    with open(source, "r", encoding="utf-8") as file:
        contents = file.read()
    for number, portion in enumerate(split_msg(contents, max_len)):
        _print_delimeter(number+1, len(portion))
        _print_html(portion)


if __name__ == '__main__':
    main()
