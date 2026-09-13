import select
import sys
import termios
import textwrap
import tty
from datetime import datetime
from enum import Enum, auto
from typing import Any, Self

from tamagonion import art, strings
from tamagonion.app_data import SECONDS_IN_HOUR, UNKNOWN, AppData, Flags, VersionStatus


class StopDrawingException(Exception):
    pass


class Screen(Enum):
    HOME = auto()
    STATUS = auto()
    HINT = auto()


class Pen:
    @classmethod
    def draw(cls, image: str, pos_y: int, pos_x: int, transparent: bool = False) -> None:
        if transparent:
            image.replace(" ", "\033C")

        cls.move_home().move_down(pos_y).move_right(pos_x)
        for line in image.split("\n"):
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
        split_frame = frame.split("\n")
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
        self.app_data.wait_until_consensus_fetch -= 1
        if self.app_data.wait_until_consensus_fetch <= 0:
            self.app_data._get_consensus_info()
            self.app_data.wait_until_consensus_fetch = SECONDS_IN_HOUR

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

        ## Draw Stinky
        info = self.app_data.info

        # Bootstrap statuses
        if info["bootstrap_percent"] < 100:
            Pen.draw(art.stinky_egg[self.app_data.frame], 10, 7)

        # Network statuses
        elif not info["network_liveness"]:
            Pen.draw(art.stinky_blackout[self.app_data.frame], 9, 1)
        elif not info["has_enough_dir_info"]:
            Pen.draw(art.stinky_confused[self.app_data.frame], 10, 7)

        # Relay network statuses
        elif not info["reachability"]:
            Pen.draw(art.stinky_turned_around[self.app_data.frame], 10, 7)
        elif not info["good_server_descriptor"]:
            Pen.draw(art.stinky_embarrassed[self.app_data.frame], 10, 7)

        # Relay statuses
        elif Flags.NO_ED_CONSENSUS in self.app_data.flags or {Flags.VALID, Flags.RUNNING} - set(self.app_data.flags):
            Pen.draw(art.stinky_sad[self.app_data.frame], 10, 7)
        elif Flags.STALE_DESC in self.app_data.flags:
            Pen.draw(art.stinky_old[self.app_data.frame], 10, 7)
        elif self.app_data.version_status in {VersionStatus.OBSOLETE, VersionStatus.UNRECOMMENDED}:
            Pen.draw(art.stinky_hurt[self.app_data.frame], 10, 7)
        elif Flags.STABLE not in self.app_data.flags:
            Pen.draw(art.stinky_unstable[self.app_data.frame], 10, 7)
        elif Flags.MIDDLE_ONLY in self.app_data.flags:
            Pen.draw(art.stinky_bored[self.app_data.frame], 10, 7)
        else:
            if datetime.now().astimezone().hour in {0, 1, 2, 3, 4, 5, 6, 7, 22, 23}:
                Pen.draw(art.stinky_asleep[self.app_data.frame], 10, 7)
            else:
                Pen.draw(art.stinky_base[self.app_data.frame], 10, 7)

        if info["bootstrap_percent"] == 100 and info["network_liveness"]:
            ## Draw the exit sign
            if Flags.BAD_EXIT in self.app_data.flags:
                Pen.draw(art.broken_exit_sign, 9, 31)
            elif Flags.EXIT in self.app_data.flags:
                Pen.draw(art.exit_sign, 8, 30)

            ## Draw the books
            if Flags.HS_DIR in self.app_data.flags:
                Pen.draw(art.book, 15, 30)

            ## Draw the cassette
            if Flags.V2_DIR in self.app_data.flags:
                Pen.draw(art.cassette, 16, 1)

            ## Draw the shield
            if Flags.GUARD in self.app_data.flags and info["reachability"]:
                Pen.draw(art.shield[self.app_data.frame], 13, 19)

        ## Slow down the animation
        if Flags.FAST not in self.app_data.flags and self.app_data.frame_skip:
            self.app_data.frame_skip = False
        else:
            self.app_data.frame ^= 1
            self.app_data.frame_skip = True

        ## Draw the stats
        Pen.draw(strings.STATS_DESCRIPTIONS[strings.Stats.NICKNAME].format(name=self.app_data.relay_name), 1, 1)
        Pen.draw(strings.STATS_DESCRIPTIONS[strings.Stats.UPTIME].format(uptime=self.app_data.formated_uptime), 2, 1)
        Pen.draw(
            strings.STATS_DESCRIPTIONS[strings.Stats.CONNECTIONS].format(
                new=self.app_data.connection_status_map["NEW"],
                launched=self.app_data.connection_status_map["LAUNCHED"],
                connected=self.app_data.connection_status_map["CONNECTED"],
                failed=self.app_data.connection_status_map["FAILED"],
                closed=self.app_data.connection_status_map["CLOSED"],
            ),
            3,
            1,
        )
        Pen.draw(
            strings.STATS_DESCRIPTIONS[strings.Stats.DOWNLOAD].format(
                current=AppData.format_bytes(info["bw_event_cache_down"]),
                average=AppData.format_bytes(info["bw_avg_down"]),
                total=AppData.format_bytes(info["traffic_read"]),
            ),
            4,
            1,
        )
        Pen.draw(
            strings.STATS_DESCRIPTIONS[strings.Stats.UPLOAD].format(
                current=AppData.format_bytes(info["bw_event_cache_up"]),
                average=AppData.format_bytes(info["bw_avg_up"]),
                total=AppData.format_bytes(info["traffic_written"]),
            ),
            5,
            1,
        )
        Pen.draw(strings.STATS_DESCRIPTIONS[strings.Stats.VERSION].format(version=self.app_data.version), 6, 1)

    def draw_status(self) -> None:
        Pen.erase_in_frame(art.status_frame)
        Pen.draw(art.status_frame, 1, 1)

        info = self.app_data.info

        network_liveness = Paper.good_status("Live") if info["network_liveness"] else Paper.bad_status("Down")
        bootstrap_progress = (
            Paper.good_status(f"{info['bootstrap_percent']}%") if info["bootstrap_percent"] == 100 else Paper.bad_status(f"{info['bootstrap_percent']}%")
        )
        enough_dir_info = Paper.good_status("Yes") if info["has_enough_dir_info"] else Paper.bad_status("No")
        good_server_descriptor = Paper.good_status("Yes") if info["good_server_descriptor"] else Paper.bad_status("No")
        reachability = Paper.good_status("Reachable") if info["reachability"] else Paper.bad_status("Unreachable")

        if self.app_data.version_status == VersionStatus.RECOMMENDED:
            version_status = Paper.good_status(self.app_data.version_status)
        elif self.app_data.version_status in {VersionStatus.OBSOLETE, VersionStatus.UNRECOMMENDED}:
            version_status = Paper.bad_status(self.app_data.version_status)
        else:
            version_status = Paper.warning_status(self.app_data.version_status)

        Pen.draw(strings.STATUSES_DESCRIPTION[strings.Statuses.NETWORK_LIVENESS].format(network_liveness=network_liveness), 2, 2)
        Pen.draw(strings.STATUSES_DESCRIPTION[strings.Statuses.BOOTSTRAP_PROGRESS].format(bootstrap_progress=bootstrap_progress), 3, 2)
        Pen.draw(strings.STATUSES_DESCRIPTION[strings.Statuses.ENOUGH_DIR_INFO].format(enough_dir_info=enough_dir_info), 4, 2)
        Pen.draw(strings.STATUSES_DESCRIPTION[strings.Statuses.GOOD_SERVER_DESCRIPTOR].format(good_server_descriptor=good_server_descriptor), 5, 2)
        Pen.draw(strings.STATUSES_DESCRIPTION[strings.Statuses.REACHABILITY].format(reachability=reachability), 6, 2)
        Pen.draw(strings.STATUSES_DESCRIPTION[strings.Statuses.VERSION_STATUS].format(version_status=version_status), 7, 2)

        self._draw_flags()

    def _draw_flags(self) -> None:
        line = ""
        line_len = 0
        line_pos_y = 8
        max_line_len = 37

        Pen.draw("Flags: ", line_pos_y, 2)

        for flag in self.app_data.flags:
            added_len = len(flag) if flag == self.app_data.flags[-1] else len(flag + ", ")
            if line_len + added_len > max_line_len:
                Pen.draw(line.rstrip(", "), line_pos_y, 9)
                line_pos_y += 1
                line = ""
                line_len = 0

            colored_flag = (
                Paper.bad_status(flag) if flag in {Flags.BAD_EXIT, Flags.MIDDLE_ONLY, Flags.NO_ED_CONSENSUS, Flags.STALE_DESC} else Paper.good_status(flag)
            )
            line += colored_flag + ", "
            line_len += len(flag + ", ")

        if line:
            Pen.draw(line.rstrip(", "), line_pos_y, 9)

    def draw_hints(self):
        Pen.erase_in_frame(art.hints_frame)
        Pen.draw(art.hints_frame, 1, 1)
        info = self.app_data.info

        hints = ""

        # Bootstrap statuses
        if info["bootstrap_percent"] < 100:
            hints += Paper.wrap_hint(
                strings.HINTS_TITLES[strings.Hints.BOOTSTRAP],
                strings.HINTS_DESCRIPTIONS[strings.Hints.BOOTSTRAP].format(phase=info["bootstrap_phase"], percent=info["bootstrap_percent"]),
            )

        # Network statuses
        if not info["network_liveness"]:
            hints += Paper.wrap_hint(
                strings.HINTS_TITLES[strings.Hints.NETWORK_LIVENESS],
                strings.HINTS_DESCRIPTIONS[strings.Hints.NETWORK_LIVENESS],
            )
        if not info["has_enough_dir_info"]:
            hints += Paper.wrap_hint(
                strings.HINTS_TITLES[strings.Hints.ENOUGH_DIR_INFO],
                strings.HINTS_DESCRIPTIONS[strings.Hints.ENOUGH_DIR_INFO],
            )

        # Relay network statuses
        if not info["reachability"]:
            if self.app_data.orport != UNKNOWN and self.app_data.dirport != UNKNOWN:
                ports = f"ORPort ({self.app_data.orport}) or DirPort ({self.app_data.dirport})"
            elif self.app_data.orport != UNKNOWN:
                ports = f"ORPort ({self.app_data.orport})"
            else:
                ports = f"DirPort ({self.app_data.dirport})"

            hints += Paper.wrap_hint(
                strings.HINTS_TITLES[strings.Hints.REACHABILITY],
                strings.HINTS_DESCRIPTIONS[strings.Hints.REACHABILITY].format(ports),
            )
        if not info["good_server_descriptor"]:
            hints += Paper.wrap_hint(
                strings.HINTS_TITLES[strings.Hints.GOOD_SERVER_DESCRIPTOR],
                strings.HINTS_DESCRIPTIONS[strings.Hints.GOOD_SERVER_DESCRIPTOR],
            )

        # Relay statuses
        if Flags.NO_ED_CONSENSUS in self.app_data.flags:
            hints += Paper.wrap_hint(
                strings.HINTS_TITLES[strings.Hints.ED_CONSENSUS_FLAG],
                strings.HINTS_DESCRIPTIONS[strings.Hints.ED_CONSENSUS_FLAG],
            )
        if Flags.VALID not in self.app_data.flags:
            hints += Paper.wrap_hint(
                strings.HINTS_TITLES[strings.Hints.NO_VALID_FLAG],
                strings.HINTS_DESCRIPTIONS[strings.Hints.NO_VALID_FLAG],
            )
        if Flags.RUNNING not in self.app_data.flags:
            hints += Paper.wrap_hint(
                strings.HINTS_TITLES[strings.Hints.NO_RUNNING_FLAG],
                strings.HINTS_DESCRIPTIONS[strings.Hints.NO_RUNNING_FLAG],
            )
        if self.app_data.version_status == VersionStatus.OBSOLETE:
            hints += Paper.wrap_hint(
                strings.HINTS_TITLES[strings.Hints.VERSION_OBSOLETE],
                strings.HINTS_DESCRIPTIONS[strings.Hints.VERSION_OBSOLETE].format(version=self.app_data.consensus_info["version"]),
            )
        elif self.app_data.version_status == VersionStatus.UNRECOMMENDED:
            hints += Paper.wrap_hint(
                strings.HINTS_TITLES[strings.Hints.VERSION_UNRECOMMENDED],
                strings.HINTS_DESCRIPTIONS[strings.Hints.VERSION_UNRECOMMENDED].format(version=self.app_data.consensus_info["version"]),
            )
        if Flags.STABLE not in self.app_data.flags:
            hints += Paper.wrap_hint(
                strings.HINTS_TITLES[strings.Hints.NO_STABLE_FLAG],
                strings.HINTS_DESCRIPTIONS[strings.Hints.NO_STABLE_FLAG],
            )
        if Flags.MIDDLE_ONLY in self.app_data.flags:
            hints += Paper.wrap_hint(
                strings.HINTS_TITLES[strings.Hints.MIDDLE_ONLY_FLAG],
                strings.HINTS_DESCRIPTIONS[strings.Hints.MIDDLE_ONLY_FLAG],
            )
        if Flags.BAD_EXIT in self.app_data.flags:
            hints += Paper.wrap_hint(
                strings.HINTS_TITLES[strings.Hints.BAD_EXIT_FLAG],
                strings.HINTS_DESCRIPTIONS[strings.Hints.BAD_EXIT_FLAG],
            )
        if Flags.FAST not in self.app_data.flags:
            hints += Paper.wrap_hint(
                strings.HINTS_TITLES[strings.Hints.NO_FAST_FLAG],
                strings.HINTS_DESCRIPTIONS[strings.Hints.NO_FAST_FLAG],
            )

        if not hints:
            hints = strings.HINTS_DESCRIPTIONS[strings.Hints.OK]

        hints = hints.rstrip()
        hints_lines = hints.split("\n")
        self.hints_scroll_index = max(0, min(self.hints_scroll_index, len(hints_lines) - 1))
        hints_view = "\n".join(hints_lines[0 + self.hints_scroll_index : 16 + self.hints_scroll_index])

        Pen.draw(hints_view, 2, 2)

        up_dim = art.DIM if self.hints_scroll_index == 0 else ""
        down_dim = art.DIM if self.hints_scroll_index == len(hints_lines) - 1 else ""
        Pen.draw(
            f"|{up_dim}Scroll {art.BOLD_UNDERLINE}u{art.RESET}{up_dim}p{art.RESET}|{down_dim}Scroll {art.BOLD_UNDERLINE}d{art.RESET}{down_dim}own{art.RESET}",
            18,
            24,
        )

    @staticmethod
    def good_status(s: str) -> str:
        return f"{art.GREEN}{s}{art.RESET}"

    @staticmethod
    def bad_status(s: str) -> str:
        return f"{art.RED}{s}{art.RESET}"

    @staticmethod
    def warning_status(s: str) -> str:
        return f"{art.YELLOW}{s}{art.RESET}"

    @staticmethod
    def wrap_hint(title: str, text: str) -> str:
        return textwrap.fill(f"{art.BOLD}{title}{art.RESET}: {text}", 44) + "\n\n"
