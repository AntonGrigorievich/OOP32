import json
from dataclasses import dataclass
from pathlib import Path
from typing import Callable


@dataclass(frozen=True)
class TripleState:
    a: int
    b: int
    c: int


class TripleModel:
    def __init__(self, storage_path: Path) -> None:
        self._min_value = 0
        self._max_value = 100
        self._storage_path = storage_path
        self._listeners: list[Callable[[TripleState], None]] = []
        self._notify_count = 0

        loaded = self._load_state()
        self._state = self._normalize_loaded(loaded)

    @property
    def min_value(self) -> int:
        return self._min_value

    @property
    def max_value(self) -> int:
        return self._max_value

    @property
    def notify_count(self) -> int:
        return self._notify_count

    def state(self) -> TripleState:
        return self._state

    def add_listener(self, listener: Callable[[TripleState], None]) -> None:
        self._listeners.append(listener)
        self._notify(listener)

    def set_a(self, value: int) -> None:
        new_a = self._clamp_range(value)
        a, b, c = new_a, self._state.b, self._state.c

        if b < a:
            b = a
        if c < b:
            c = b

        self._apply_state(TripleState(a, b, c))

    def set_b(self, value: int) -> None:
        candidate = self._clamp_range(value)
        a, c = self._state.a, self._state.c
        new_b = max(a, min(candidate, c))
        self._apply_state(TripleState(a, new_b, c))

    def set_c(self, value: int) -> None:
        new_c = self._clamp_range(value)
        a, b, c = self._state.a, self._state.b, new_c

        if b > c:
            b = c
        if a > b:
            a = b

        self._apply_state(TripleState(a, b, c))

    def persist(self) -> None:
        data = {"a": self._state.a, "b": self._state.b, "c": self._state.c}
        try:
            self._storage_path.parent.mkdir(parents=True, exist_ok=True)
            self._storage_path.write_text(json.dumps(data, ensure_ascii=True), encoding="utf-8")
        except OSError as exc:
            print(f"[WARN] Не удалось сохранить модель: {exc}")

    def parse_user_number(self, raw: str) -> int | None:
        text = raw.strip()
        if text == "":
            return None
        try:
            return int(text)
        except ValueError:
            return None

    def _clamp_range(self, value: int) -> int:
        return max(self._min_value, min(value, self._max_value))

    def _apply_state(self, new_state: TripleState) -> None:
        if new_state == self._state:
            return
        self._state = new_state
        self._notify_all()

    def _notify_all(self) -> None:
        if not self._listeners:
            return
        self._notify_count += 1
        for listener in self._listeners:
            listener(self._state)

    def _notify(self, listener: Callable[[TripleState], None]) -> None:
        self._notify_count += 1
        listener(self._state)

    def _normalize_loaded(self, raw: dict | None) -> TripleState:
        if not raw:
            return TripleState(30, 50, 70)

        a = self._coerce_int(raw.get("a"), 30)
        b = self._coerce_int(raw.get("b"), 50)
        c = self._coerce_int(raw.get("c"), 70)

        a = self._clamp_range(a)
        b = self._clamp_range(b)
        c = self._clamp_range(c)

        if b < a:
            b = a
        if c < b:
            c = b

        return TripleState(a, b, c)

    def _coerce_int(self, value: object, fallback: int) -> int:
        if isinstance(value, int):
            return value
        if isinstance(value, str):
            try:
                return int(value.strip())
            except ValueError:
                return fallback
        return fallback

    def _load_state(self) -> dict | None:
        if not self._storage_path.exists():
            return None
        try:
            data = json.loads(self._storage_path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                return data
        except (OSError, json.JSONDecodeError) as exc:
            print(f"[WARN] Не удалось загрузить модель: {exc}")
        return None
