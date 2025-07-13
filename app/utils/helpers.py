from typing import Iterable, List, TypeVar

T = TypeVar("T")


def chunked(iterable: Iterable[T], n: int) -> List[List[T]]:
    """Разбивает последовательность на списки длиной n."""
    buf, result = [], []
    for item in iterable:
        buf.append(item)
        if len(buf) == n:
            result.append(buf)
            buf = []
    if buf:
        result.append(buf)
    return result
