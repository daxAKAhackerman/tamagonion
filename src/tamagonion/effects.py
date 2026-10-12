from enum import StrEnum


class Color(StrEnum):
    RED = "RED"
    GREEN = "GREEN"
    YELLOW = "YELLOW"


class Effect(StrEnum):
    BOLD = "BOLD"
    DIM = "DIM"
    UNDERLINE = "UNDERLINE"


class RichStr:
    text: str
    color: Color | None
    effects: tuple[Effect, ...] | None

    def __init__(self, s: str, color: Color | None = None, effects: tuple[Effect, ...] | None = None) -> None:
        self.text = s
        self.color = color
        self.effects = effects

    def __len__(self) -> int:
        return len(self.text)

    def __str__(self) -> str:
        rich_str = self.text

        if self.color:
            rich_str = f"[{self.color}]{rich_str}[/{self.color}]"

        if self.effects:
            for effect in self.effects:
                rich_str = f"[{effect}]{rich_str}[/{effect}]"

        return rich_str
