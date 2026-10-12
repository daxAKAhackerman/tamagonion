import re


class DefaultRenderer:
    tag_regex: re.Pattern[str]

    def __init__(self) -> None:
        self.tag_regex = re.compile(r"\[[A-Z]+?\](.+?)\[\/[A-Z]+?\]")

    def setup(self) -> None:
        self.__class__.hide_cursor()
        self.__class__.erase_screen()
        self.__class__.move_home()

    def tear_down(self) -> None:
        self.__class__.erase_screen()
        self.__class__.move_home()
        self.__class__.show_cursor()

    def render(self, buffer: str) -> None:
        self.__class__.move_home()
        buffer = self.color(buffer)
        print(buffer, end="")

    def color(self, buffer: str) -> str:
        while True:
            matches = list(re.finditer(self.tag_regex, buffer))

            if not matches:
                return buffer

            for match in matches:
                buffer = buffer.replace(match.group(0), match.group(1), 1)

    @staticmethod
    def hide_cursor() -> None:
        print("\033[?25l", end="")

    @staticmethod
    def show_cursor() -> None:
        print("\033[?25h", end="")

    @staticmethod
    def move_home() -> None:
        print("\033[H", end="")

    @staticmethod
    def erase_screen() -> None:
        print("\033[2J", end="")
