import re
from enum import StrEnum

OPENING_TAG_REGEX = re.compile(r"\[([A-Z]+?)\]")
CLOSING_TAG_REGEX = re.compile(r"\[\/([A-Z]+?)\]")


class AnsiEscapeSequences(StrEnum):
    RED = "\033[31m"
    YELLOW = "\033[33m"
    GREEN = "\033[32m"
    GREY = "\033[90m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    RESET_COLOR = "\033[39m"
    RESET_BOLD = "\033[22m"
    RESET_UNDERLINE = "\033[24m"
    HIDE_CURSOR = "\033[?25l"
    SHOW_CURSOR = "\033[?25h"
    MOVE_HOME = "\033[H"
    ERASE_SCREEN = "\033[2J"
    ENTER_ALT_BUFFER = "\033[?1049h"
    EXIT_ALT_BUFFER = "\033[?1049l"


RESET_CODES = {
    AnsiEscapeSequences.RED: AnsiEscapeSequences.RESET_COLOR,
    AnsiEscapeSequences.YELLOW: AnsiEscapeSequences.RESET_COLOR,
    AnsiEscapeSequences.GREEN: AnsiEscapeSequences.RESET_COLOR,
    AnsiEscapeSequences.GREY: AnsiEscapeSequences.RESET_COLOR,
    AnsiEscapeSequences.BOLD: AnsiEscapeSequences.RESET_BOLD,
    AnsiEscapeSequences.UNDERLINE: AnsiEscapeSequences.RESET_UNDERLINE,
}


class DefaultRenderer:
    def setup(self) -> None:
        self.enter_alt_buffer()
        self.hide_cursor()

    def tear_down(self) -> None:
        self.show_cursor()
        self.exit_alt_buffer()

    def render(self, buffer: str) -> None:
        self.move_home()
        buffer = self._apply_tags(buffer)
        print(buffer, end="")

    def _apply_tags(self, buffer: str) -> str:
        unique_matches = self._get_unique_tag_matches(buffer, OPENING_TAG_REGEX)
        for match in unique_matches:
            ansi_code = AnsiEscapeSequences[match[1]]
            buffer = buffer.replace(match[0], ansi_code)

        unique_matches = self._get_unique_tag_matches(buffer, CLOSING_TAG_REGEX)
        for match in unique_matches:
            ansi_code = RESET_CODES[AnsiEscapeSequences[match[1]]]
            buffer = buffer.replace(match[0], ansi_code)

        return buffer

    def _get_unique_tag_matches(self, buffer: str, regex: re.Pattern[str]) -> set[tuple[str, str]]:
        matches = list(re.finditer(regex, buffer))
        return {(match.group(0), match.group(1)) for match in matches}

    @staticmethod
    def hide_cursor() -> None:
        print(AnsiEscapeSequences.HIDE_CURSOR, end="")

    @staticmethod
    def show_cursor() -> None:
        print(AnsiEscapeSequences.SHOW_CURSOR, end="")

    @staticmethod
    def move_home() -> None:
        print(AnsiEscapeSequences.MOVE_HOME, end="")

    @staticmethod
    def enter_alt_buffer() -> None:
        print(AnsiEscapeSequences.ENTER_ALT_BUFFER, end="")

    @staticmethod
    def exit_alt_buffer() -> None:
        print(AnsiEscapeSequences.EXIT_ALT_BUFFER, end="")
