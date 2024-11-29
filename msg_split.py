from dataclasses import dataclass as _dataclass
import re as _re
import typing as _typing

import bs4 as _bs4


MAX_LEN = 4096
SPLITTABLE_TAGS = frozenset({
    'p', 'b', 'strong', 'i', 'ul', 'ol', 'div', 'span'
})


@_dataclass
class Position():
    """
    Element position wrapper object
    """
    start: int
    end: int

    @property
    def lenght(self) -> int:
        return self.end - self.start

    def contains(self, other: int):
        return other > self.start and other < self.end


@_dataclass
class Element():
    """
    bs4.Tag wrapper object
    """
    tag: _bs4.Tag
    position: Position

    @property
    def parents(self) -> list[_bs4.Tag]:
        return list(self.tag.parents)[:-1]

    @property
    def document(self) -> _bs4.Tag:
        parents = list(self.tag.parents)
        return parents[0] if parents else self.tag

    def splittable(self, cursor: int) -> bool:
        if self.tag.name == '[document]':
            return True
        return (
            self.tag.name in SPLITTABLE_TAGS
            and
            cursor > self.position.start + sum(
                len(f"</{p.name}>")
                for p in self.parents
            )
            and
            all(p.name in SPLITTABLE_TAGS for p in self.parents)
        )

    def split(self, area: Position) -> tuple[str, str]:
        """
        Closes tag within area.
        Returns it's tag HTML and the rest document HTML
        """
        closing_tags = "".join(f"</{p.name}>" for p in self.parents)
        opening_tags = "".join(f"<{p.name}>" for p in self.parents)
        if self.tag.name != '[document]':
            closing_tags = f"</{self.tag.name}>" + closing_tags
            opening_tags = opening_tags + f"<{self.tag.name}>"
        source = str(self.document)[area.start:area.end]
        head = (source[:-(len(closing_tags)+1)] if closing_tags else source)
        broken_tag = _re.search(r"\<[^\>]+$", head)
        if broken_tag:
            head = head[:broken_tag.start()]
        head += closing_tags
        tail = (
            opening_tags +
            str(self.document)[area.start+len(head)-len(opening_tags):]
        )
        return (head, tail)


def split_msg(
    source: str,
    max_len: int = MAX_LEN
) -> _typing.Generator[str, None, None]:
    """
    Splits the original message (`source`) into
    fragments of the specified length (`max_len`).
    """
    if max_len <= 0:
        raise ValueError("Invalid max_len")

    raw = source[:]
    while raw:
        soup = _bs4.BeautifulSoup(raw, 'html.parser')
        elements = _get_all_elements(soup)
        element = _get_element_under_cursor(elements, max_len)
        if not element:
            if len(raw) < max_len:
                yield raw
                raw = ''
                continue
            elif len(elements) == 1:
                element = elements[0]
            else:
                raise ValueError("Cannot split message")
        head, tail = element.split(Position(0, max_len))
        yield head
        raw = tail


def _get_all_elements(soup: _bs4.BeautifulSoup) -> list[Element]:
    tags: list[_bs4.Tag] = soup.find_all()
    return list(
        Element(
            tag=tag,
            position=_get_tag_position(str(soup), tag),
        ) for tag in [soup, *tags]
    )


def _get_element_under_cursor(
    elements: list[Element],
    cursor: int
) -> Element | None:
    """
    Finds closest splittable tag to cursor
    """
    filtered = list(filter(
        lambda e: e.position.contains(cursor) and e.splittable(cursor),
        elements,
    ))
    if filtered:
        closest = min(filtered, key=lambda e: e.position.lenght)
        # [document] itself is always splittablle, but we need to check
        # if all it's contents wrapped into a single unsplittable tag
        if (
            closest.tag.name == '[document]' and
            len(elements) > 1 and
            elements[1].tag.name not in SPLITTABLE_TAGS and
            max(elements, key=lambda e: e.position.end) == elements[1]
        ):
            return None
        return closest


def _get_tag_position(document: str, tag: _bs4.Tag) -> Position:
    """
    Returns tag absolute start and end position
    """
    if tag.sourceline is None or tag.sourcepos is None:
        return Position(0, len(document))
    lines = document.split("\n")
    position = 0
    for line in lines[0:tag.sourceline-1]:
        position += len(line) + 1
    position += tag.sourcepos
    return Position(position, position+len(tag.__str__()))
