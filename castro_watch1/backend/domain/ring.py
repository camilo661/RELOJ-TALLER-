"""Circular domain structures used by the watch."""


class RingUnit:
    """Node in a circular doubly linked ring."""

    def __init__(self, value: int):
        self.value = value
        self.forward: "RingUnit | None" = None
        self.backward: "RingUnit | None" = None

    def next(self) -> "RingUnit":
        return self.forward  # type: ignore[return-value]

    def previous(self) -> "RingUnit":
        return self.backward  # type: ignore[return-value]


class CyclicRing:
    """Circular doubly linked ring for wrap-around time values."""

    def __init__(self, start: int, end: int):
        if end < start:
            raise ValueError("end must be greater than or equal to start")

        self._head: RingUnit | None = None
        self._cursor: RingUnit | None = None
        self._length = 0

        for value in range(start, end + 1):
            self._append(value)

        self._cursor = self._head

    @property
    def current(self) -> int:
        return self._cursor.value  # type: ignore[union-attr]

    def seek(self, value: int) -> None:
        node = self._head
        for _ in range(self._length):
            if node.value == value:  # type: ignore[union-attr]
                self._cursor = node
                return
            node = node.next()  # type: ignore[assignment]
        raise ValueError(f"value {value} does not exist in the ring")

    def tick(self) -> bool:
        self._cursor = self._cursor.next()  # type: ignore[union-attr]
        return self._cursor is self._head

    def tock(self) -> bool:
        self._cursor = self._cursor.previous()  # type: ignore[union-attr]
        return self._cursor is self._head.backward  # type: ignore[union-attr]

    def _append(self, value: int) -> None:
        node = RingUnit(value)
        self._length += 1

        if self._head is None:
            node.forward = node
            node.backward = node
            self._head = node
            self._cursor = node
            return

        tail = self._head.backward
        tail.forward = node  # type: ignore[union-attr]
        node.backward = tail
        node.forward = self._head
        self._head.backward = node
