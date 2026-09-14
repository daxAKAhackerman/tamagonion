import select
import sys
import termios
import textwrap
import tty
from datetime import datetime
from enum import Enum, StrEnum, auto
from typing import Any, Self

from tamagonion import art, strings
from tamagonion.app_data import AppData, Flag, ORConnStatus, VersionStatus

SLEEP_HOURS = {*range(8), *range(22, 24)}


class StopDrawingException(Exception):
    pass


class Screen(Enum):
    HOME = auto()
    STATUS = auto()
    HINT = auto()


class Color(StrEnum):
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    RESET = "\033[39m"


class ColoredStr:
    text: str
    color: Color

    def __init__(self, s: str, color: Color) -> None:
        self.text = s
        self.color = color

    def __len__(self) -> int:
        return len(self.text)

    def __str__(self) -> str:
        return f"{self.color}{self.text}{Color.RESET}"


class Pen:
    @classmethod
    def draw(cls, image: str, pos_y: int, pos_x: int, transparent: bool = False) -> None:
        if transparent:
            image.replace(" ", "\033C")

        cls.move_home().move_down(pos_y).move_right(pos_x)
        for line in image.splitlines():
            print(line, end="")
            cls.move_to_beginning_of_line().move_right(pos_x).move_down()

    @classmethod
    def hide_cursor(cls) -> type[Self]:
        print("\033[?25l", end="")
        return cls

    @classmethod
    def show_cursor(cls) -> type[Self]:
        print("\033[?25h", end="")
        return cls

    @classmethod
    def move_home(cls) -> type[Self]:
        print("\033[H", end="")
        return cls

    @classmethod
    def move_to_beginning_of_line(cls) -> type[Self]:
        print("\r", end="")
        return cls

    @classmethod
    def move_up(cls, n: int = 1) -> type[Self]:
        if n > 0:
            print(f"\033[{n}A", end="")
        return cls

    @classmethod
    def move_down(cls, n: int = 1) -> type[Self]:
        if n > 0:
            print(f"\033[{n}B", end="")
        return cls

    @classmethod
    def move_right(cls, n: int = 1) -> type[Self]:
        if n > 0:
            print(f"\033[{n}C", end="")
        return cls

    @classmethod
    def move_left(cls, n: int = 1) -> type[Self]:
        if n > 0:
            print(f"\033[{n}D", end="")
        return cls

    @classmethod
    def erase_screen(cls) -> type[Self]:
        print("\033[2J", end="")

        return cls

    @classmethod
    def erase_in_frame(cls, frame: str) -> type[Self]:
        split_frame = frame.splitlines()
        frame_height = len(split_frame)
        frame_witdh = len(split_frame[0])
        for i in range(1, frame_height - 1):
            Pen.draw(" " * (frame_witdh - 2), i, 1)

        return cls


class Paper:
    app_data: AppData
    saved_term_setting: termios._AttrReturn
    saved_fd: Any
    active_screen: Screen = Screen.HOME
    hints_scroll_index: int = 0
    instance: Self | None = None

    def __init(self, app_data: AppData) -> None:
        self.app_data = app_data

    def __new__(cls, *args, **kwargs) -> Self:
        if cls.instance is None:
            cls.instance = super().__new__(cls)
            cls.instance.__init(*args, **kwargs)
        return cls.instance

    def setup_scan_key(self) -> None:
        self.saved_fd = sys.stdin.fileno()
        self.saved_term_setting = termios.tcgetattr(self.saved_fd)
        tty.setcbreak(self.saved_fd)

    def tear_down_scan_key(self) -> None:
        termios.tcsetattr(self.saved_fd, termios.TCSADRAIN, self.saved_term_setting)

    @staticmethod
    def scan_key() -> str | None:
        readable, _writeable, _executable = select.select([sys.stdin], [], [], 0)
        if readable:
            return sys.stdin.read(1)

    def draw(self) -> None:
        match self.active_screen:
            case Screen.HOME:
                self.draw_home()
            case Screen.STATUS:
                self.draw_status()
            case Screen.HINT:
                self.draw_hints()

    def draw_home(self) -> None:
        Pen.erase_in_frame(art.home_frame)
        Pen.draw(art.home_frame, 0, 0)

        info = self.app_data.info
        ## Draw Stinky

        # Bootstrap statuses
        if info["bootstrap_percent"] < 100:
            Pen.draw(art.stinky_egg[self.app_data.frame], 10, 7)

        # Network statuses
        elif not info["network_liveness"]:
            Pen.draw(art.stinky_blackout[self.app_data.frame], 9, 1)
        elif not info["enough_dir_info"]:
            Pen.draw(art.stinky_confused[self.app_data.frame], 10, 7)

        # Relay network statuses
        elif not info["reachability"]:
            Pen.draw(art.stinky_turned_around[self.app_data.frame], 10, 7)
        elif not info["good_server_descriptor"]:
            Pen.draw(art.stinky_embarrassed[self.app_data.frame], 10, 7)

        # Relay statuses
        elif Flag.NO_ED_CONSENSUS in self.app_data.flags or {Flag.VALID, Flag.RUNNING} - set(self.app_data.flags):
            Pen.draw(art.stinky_sad[self.app_data.frame], 10, 7)
        elif Flag.STALE_DESC in self.app_data.flags:
            Pen.draw(art.stinky_old[self.app_data.frame], 10, 7)
        elif self.app_data.version_status in {VersionStatus.OBSOLETE, VersionStatus.UNRECOMMENDED}:
            Pen.draw(art.stinky_hurt[self.app_data.frame], 10, 7)
        elif Flag.STABLE not in self.app_data.flags:
            Pen.draw(art.stinky_unstable[self.app_data.frame], 10, 7)
        elif Flag.MIDDLE_ONLY in self.app_data.flags:
            Pen.draw(art.stinky_bored[self.app_data.frame], 10, 7)
        else:
            if datetime.now().astimezone().hour in SLEEP_HOURS:
                Pen.draw(art.stinky_asleep[self.app_data.frame], 10, 7)
            else:
                Pen.draw(art.stinky_base[self.app_data.frame], 10, 7)

        if info["bootstrap_percent"] == 100 and info["network_liveness"]:
            ## Draw the exit sign
            if Flag.BAD_EXIT in self.app_data.flags:
                Pen.draw(art.broken_exit_sign, 9, 31)
            elif Flag.EXIT in self.app_data.flags:
                Pen.draw(art.exit_sign, 8, 30)

            ## Draw the books
            if Flag.HS_DIR in self.app_data.flags:
                Pen.draw(art.book, 15, 30)

            ## Draw the cassette
            if Flag.V2_DIR in self.app_data.flags:
                Pen.draw(art.cassette, 16, 1)

            ## Draw the shield
            if Flag.GUARD in self.app_data.flags and info["reachability"]:
                Pen.draw(art.shield[self.app_data.frame], 13, 19)

        ## Slow down the animation
        if Flag.FAST not in self.app_data.flags and self.app_data.frame_skip:
            self.app_data.frame_skip = False
        else:
            self.app_data.frame ^= 1
            self.app_data.frame_skip = True

        ## Draw the stats
        Pen.draw(strings.STAT_DESCRIPTIONS[strings.Stat.NICKNAME].format(name=self.app_data.relay_name), 1, 1)
        Pen.draw(strings.STAT_DESCRIPTIONS[strings.Stat.UPTIME].format(uptime=self.app_data.formated_uptime), 2, 1)
        Pen.draw(
            strings.STAT_DESCRIPTIONS[strings.Stat.CONNECTIONS].format(
                new=self.app_data.connection_status_map[ORConnStatus.NEW],
                launched=self.app_data.connection_status_map[ORConnStatus.LAUNCHED],
                connected=self.app_data.connection_status_map[ORConnStatus.CONNECTED],
                failed=self.app_data.connection_status_map[ORConnStatus.FAILED],
                closed=self.app_data.connection_status_map[ORConnStatus.CLOSED],
            ),
            3,
            1,
        )
        Pen.draw(
            strings.STAT_DESCRIPTIONS[strings.Stat.DOWNLOAD].format(
                current=AppData.format_bytes(info["bw_event_cache_down"]),
                average=AppData.format_bytes(info["bw_avg_down"]),
                total=AppData.format_bytes(info["traffic_read"]),
            ),
            4,
            1,
        )
        Pen.draw(
            strings.STAT_DESCRIPTIONS[strings.Stat.UPLOAD].format(
                current=AppData.format_bytes(info["bw_event_cache_up"]),
                average=AppData.format_bytes(info["bw_avg_up"]),
                total=AppData.format_bytes(info["traffic_written"]),
            ),
            5,
            1,
        )
        Pen.draw(strings.STAT_DESCRIPTIONS[strings.Stat.VERSION].format(version=self.app_data.version), 6, 1)

    def draw_status(self) -> None:
        Pen.erase_in_frame(art.status_frame)
        Pen.draw(art.home_frame, 0, 0)
        Pen.draw(art.status_frame, 1, 1)

        info = self.app_data.info

        network_liveness = (
            str(ColoredStr(strings.MISC_STRINGS[strings.Misc.STATUS_LIVE], Color.GREEN))
            if info["network_liveness"]
            else str(ColoredStr(strings.MISC_STRINGS[strings.Misc.STATUS_DOWN], Color.RED))
        )
        bootstrap_progress = (
            str(ColoredStr(f"{info['bootstrap_percent']}{strings.SUFFIXES[strings.Suffix.PERCENT]}", Color.GREEN))
            if info["bootstrap_percent"] == 100
            else str(ColoredStr(f"{info['bootstrap_percent']}{strings.SUFFIXES[strings.Suffix.PERCENT]}", Color.RED))
        )
        enough_dir_info = (
            str(ColoredStr(strings.MISC_STRINGS[strings.Misc.STATUS_YES], Color.GREEN))
            if info["enough_dir_info"]
            else str(ColoredStr(strings.MISC_STRINGS[strings.Misc.STATUS_NO], Color.RED))
        )
        good_server_descriptor = (
            str(ColoredStr(strings.MISC_STRINGS[strings.Misc.STATUS_YES], Color.GREEN))
            if info["good_server_descriptor"]
            else str(ColoredStr(strings.MISC_STRINGS[strings.Misc.STATUS_NO], Color.RED))
        )
        reachability = (
            str(ColoredStr(strings.MISC_STRINGS[strings.Misc.STATUS_REACHABLE], Color.GREEN))
            if info["reachability"]
            else str(ColoredStr(strings.MISC_STRINGS[strings.Misc.STATUS_UNREACHABLE], Color.RED))
        )

        if self.app_data.version_status == VersionStatus.RECOMMENDED:
            version_status = str(ColoredStr(self.app_data.version_status, Color.GREEN))
        elif self.app_data.version_status in {VersionStatus.OBSOLETE, VersionStatus.UNRECOMMENDED}:
            version_status = str(ColoredStr(self.app_data.version_status, Color.RED))
        else:
            version_status = str(ColoredStr(self.app_data.version_status, Color.YELLOW))

        Pen.draw(strings.STATUS_DESCRIPTION[strings.Status.NETWORK_LIVENESS].format(network_liveness=network_liveness), 2, 2)
        Pen.draw(strings.STATUS_DESCRIPTION[strings.Status.BOOTSTRAP_PROGRESS].format(bootstrap_progress=bootstrap_progress), 3, 2)
        Pen.draw(strings.STATUS_DESCRIPTION[strings.Status.ENOUGH_DIR_INFO].format(enough_dir_info=enough_dir_info), 4, 2)
        Pen.draw(strings.STATUS_DESCRIPTION[strings.Status.GOOD_SERVER_DESCRIPTOR].format(good_server_descriptor=good_server_descriptor), 5, 2)
        Pen.draw(strings.STATUS_DESCRIPTION[strings.Status.REACHABILITY].format(reachability=reachability), 6, 2)
        Pen.draw(strings.STATUS_DESCRIPTION[strings.Status.VERSION_STATUS].format(version_status=version_status), 7, 2)

        self._draw_flags()

    def _draw_flags(self) -> None:
        line = ""
        line_len = 0
        line_pos_y = 8
        max_line_len = len(art.status_frame.splitlines()[0]) - len(strings.STATUS_DESCRIPTION[strings.Status.FLAGS])

        Pen.draw(strings.STATUS_DESCRIPTION[strings.Status.FLAGS], line_pos_y, 2)

        for flag in self.app_data.flags:
            added_len = len(flag) if flag == self.app_data.flags[-1] else len(flag + strings.SEPARATORS[strings.Separator.COMMA])
            if line_len + added_len > max_line_len:
                Pen.draw(line.rstrip(strings.SEPARATORS[strings.Separator.COMMA]), line_pos_y, 9)
                line_pos_y += 1
                line = ""
                line_len = 0

            colored_flag = (
                str(ColoredStr(flag, Color.RED))
                if flag in {Flag.BAD_EXIT, Flag.MIDDLE_ONLY, Flag.NO_ED_CONSENSUS, Flag.STALE_DESC}
                else str(ColoredStr(flag, Color.GREEN))
            )
            line += colored_flag + strings.SEPARATORS[strings.Separator.COMMA]
            line_len += len(flag + strings.SEPARATORS[strings.Separator.COMMA])

        if line:
            Pen.draw(line.rstrip(strings.SEPARATORS[strings.Separator.COMMA]), line_pos_y, 9)

    def draw_hints(self) -> None:
        Pen.erase_in_frame(art.hints_frame)
        Pen.draw(art.home_frame, 0, 0)
        Pen.draw(art.hints_frame, 1, 1)

        info = self.app_data.info

        hints = ""

        # Bootstrap statuses
        if info["bootstrap_percent"] < 100:
            hints += Paper._wrap_hint(
                strings.HINT_TITLES[strings.Hint.BOOTSTRAP],
                strings.HINT_DESCRIPTIONS[strings.Hint.BOOTSTRAP].format(phase=info["bootstrap_phase"], percent=info["bootstrap_percent"]),
            )

        # Network statuses
        if not info["network_liveness"]:
            hints += Paper._wrap_hint(
                strings.HINT_TITLES[strings.Hint.NETWORK_LIVENESS],
                strings.HINT_DESCRIPTIONS[strings.Hint.NETWORK_LIVENESS],
            )
        if not info["enough_dir_info"]:
            hints += Paper._wrap_hint(
                strings.HINT_TITLES[strings.Hint.ENOUGH_DIR_INFO],
                strings.HINT_DESCRIPTIONS[strings.Hint.ENOUGH_DIR_INFO],
            )

        # Relay network statuses
        if not info["reachability"]:
            if self.app_data.orport != strings.MISC_STRINGS[strings.Misc.UNKNOWN] and self.app_data.dirport != strings.MISC_STRINGS[strings.Misc.UNKNOWN]:
                ports = strings.MISC_STRINGS[strings.Misc.HINT_ORPORT_AND_DIRPORT_UNREACHABLE].format(
                    orport=self.app_data.orport, dirport=self.app_data.dirport
                )
            elif self.app_data.orport != strings.MISC_STRINGS[strings.Misc.UNKNOWN]:
                ports = strings.MISC_STRINGS[strings.Misc.HINT_ORPORT_UNREACHABLE].format(orport=self.app_data.orport)
            else:
                ports = strings.MISC_STRINGS[strings.Misc.HINT_DIRPORT_UNREACHABLE].format(dirport=self.app_data.dirport)

            hints += Paper._wrap_hint(
                strings.HINT_TITLES[strings.Hint.REACHABILITY],
                strings.HINT_DESCRIPTIONS[strings.Hint.REACHABILITY].format(ports),
            )
        if not info["good_server_descriptor"]:
            hints += Paper._wrap_hint(
                strings.HINT_TITLES[strings.Hint.GOOD_SERVER_DESCRIPTOR],
                strings.HINT_DESCRIPTIONS[strings.Hint.GOOD_SERVER_DESCRIPTOR],
            )

        # Relay statuses
        if Flag.NO_ED_CONSENSUS in self.app_data.flags:
            hints += Paper._wrap_hint(
                strings.HINT_TITLES[strings.Hint.ED_CONSENSUS_FLAG],
                strings.HINT_DESCRIPTIONS[strings.Hint.ED_CONSENSUS_FLAG],
            )
        if Flag.VALID not in self.app_data.flags:
            hints += Paper._wrap_hint(
                strings.HINT_TITLES[strings.Hint.NO_VALID_FLAG],
                strings.HINT_DESCRIPTIONS[strings.Hint.NO_VALID_FLAG],
            )
        if Flag.RUNNING not in self.app_data.flags:
            hints += Paper._wrap_hint(
                strings.HINT_TITLES[strings.Hint.NO_RUNNING_FLAG],
                strings.HINT_DESCRIPTIONS[strings.Hint.NO_RUNNING_FLAG],
            )
        if self.app_data.version_status == VersionStatus.OBSOLETE:
            hints += Paper._wrap_hint(
                strings.HINT_TITLES[strings.Hint.VERSION_OBSOLETE],
                strings.HINT_DESCRIPTIONS[strings.Hint.VERSION_OBSOLETE].format(version=self.app_data.recommended_version),
            )
        elif self.app_data.version_status == VersionStatus.UNRECOMMENDED:
            hints += Paper._wrap_hint(
                strings.HINT_TITLES[strings.Hint.VERSION_UNRECOMMENDED],
                strings.HINT_DESCRIPTIONS[strings.Hint.VERSION_UNRECOMMENDED].format(version=self.app_data.recommended_version),
            )
        if Flag.STABLE not in self.app_data.flags:
            hints += Paper._wrap_hint(
                strings.HINT_TITLES[strings.Hint.NO_STABLE_FLAG],
                strings.HINT_DESCRIPTIONS[strings.Hint.NO_STABLE_FLAG],
            )
        if Flag.MIDDLE_ONLY in self.app_data.flags:
            hints += Paper._wrap_hint(
                strings.HINT_TITLES[strings.Hint.MIDDLE_ONLY_FLAG],
                strings.HINT_DESCRIPTIONS[strings.Hint.MIDDLE_ONLY_FLAG],
            )
        if Flag.BAD_EXIT in self.app_data.flags:
            hints += Paper._wrap_hint(
                strings.HINT_TITLES[strings.Hint.BAD_EXIT_FLAG],
                strings.HINT_DESCRIPTIONS[strings.Hint.BAD_EXIT_FLAG],
            )
        if Flag.FAST not in self.app_data.flags:
            hints += Paper._wrap_hint(
                strings.HINT_TITLES[strings.Hint.NO_FAST_FLAG],
                strings.HINT_DESCRIPTIONS[strings.Hint.NO_FAST_FLAG],
            )

        if not hints:
            hints = Paper._wrap_hint("", strings.HINT_DESCRIPTIONS[strings.Hint.OK])

        frame_vert_space = len(art.hints_frame.splitlines()) - 2
        hints_lines = hints.rstrip().splitlines()
        self.hints_scroll_index = max(0, min(self.hints_scroll_index, len(hints_lines) - frame_vert_space))
        hints_view = strings.SEPARATORS[strings.Separator.NEW_LINE].join(hints_lines[0 + self.hints_scroll_index : frame_vert_space + self.hints_scroll_index])
        Pen.draw(hints_view, 2, 2)

        up_dim = art.Effect.DIM if self.hints_scroll_index == 0 else ""
        down_dim = art.Effect.DIM if self.hints_scroll_index == frame_vert_space - 2 or len(hints_lines) <= frame_vert_space else ""
        Pen.draw(
            strings.MISC_STRINGS[strings.Misc.HINT_MENU].format(up_dim=up_dim, down_dim=down_dim),
            18,
            24,
        )

    @staticmethod
    def _wrap_hint(title: str, text: str) -> str:
        frame_horz_space = len(art.hints_frame.splitlines()[0]) - 2
        if title:
            return textwrap.fill(f"{art.Effect.BOLD}{title}{art.Effect.RESET}: {text}", frame_horz_space) + strings.SEPARATORS[strings.Separator.NEW_LINE] * 2
        else:
            return textwrap.fill(text, frame_horz_space) + strings.SEPARATORS[strings.Separator.NEW_LINE] * 2
