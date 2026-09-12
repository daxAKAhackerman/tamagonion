import select
import sys
import termios
import textwrap
import tty
from datetime import datetime
from enum import IntEnum, auto
from typing import Any, Self

from tamagonion import art
from tamagonion.app_data import AppData, Flags, VersionStatus


class StopDrawingException(Exception):
    pass


class Screen(IntEnum):
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
    def erase(cls, include_frame: bool = False) -> type[Self]:
        if include_frame:
            print("\033[2J", end="")
        else:
            split_frame = art.frame.split("\n")
            frame_height = len(split_frame)
            frame_witdh = len(split_frame[0])
            for i in range(1, frame_height - 1):
                Pen.draw(" " * (frame_witdh - 2), i, 1)

        return cls


class Paper:
    app_data: AppData
    active_screen: Screen = Screen.HOME
    saved_term_setting: Any
    saved_fd: Any
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
        Pen.erase()

        info = self.app_data.info
        ## Draw Stinky

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
        elif self.app_data.version_status in {VersionStatus.OBSOLETE, VersionStatus.UNRECOMMENDED, VersionStatus.UNKNOWN}:
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

        Pen.draw(f"Relay nickname: {self.app_data.relay_name}", 1, 1)
        Pen.draw(f"Uptime: {self.app_data.formated_uptime}", 2, 1)
        Pen.draw(
            f"Connections (N/L/Co/F/Cl): {self.app_data.connection_status_map['NEW']}/{self.app_data.connection_status_map['LAUNCHED']}/{self.app_data.connection_status_map['CONNECTED']}/{self.app_data.connection_status_map['FAILED']}/{self.app_data.connection_status_map['CLOSED']}",
            3,
            1,
        )
        Pen.draw(
            f"Download (Cur/Avg/Tot): {AppData.format_bytes(info['bw_event_cache_down'])} / {AppData.format_bytes(info['bw_avg_down'])} / {AppData.format_bytes(info['traffic_read'])}",
            4,
            1,
        )
        Pen.draw(
            f"Upload (Cur/Avg/Tot): {AppData.format_bytes(info['bw_event_cache_up'])} / {AppData.format_bytes(info['bw_avg_up'])} / {AppData.format_bytes(info['traffic_written'])}",
            5,
            1,
        )

        Pen.draw(f"Version: {self.app_data.version}", 6, 1)

    def draw_status(self):
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
            verion_status = Paper.good_status(self.app_data.version_status)
        elif self.app_data.version_status in {VersionStatus.OBSOLETE, VersionStatus.UNRECOMMENDED, VersionStatus.UNKNOWN}:
            verion_status = Paper.bad_status(self.app_data.version_status)
        else:
            verion_status = Paper.warning_status(self.app_data.version_status)

        Pen.draw(f"Network liveness: {network_liveness}", 3, 2)
        Pen.draw(f"Bootstrap progress: {bootstrap_progress}", 4, 2)
        Pen.draw(f"Enough directory info: {enough_dir_info}", 5, 2)
        Pen.draw(f"Good server descriptor: {good_server_descriptor}", 6, 2)
        Pen.draw(f"Reachability: {reachability}", 7, 2)
        Pen.draw(f"Version status: {verion_status}", 8, 2)

        self._draw_flags()

    def _draw_flags(self):
        line = ""
        line_len = 0
        line_pos_y = 10

        Pen.draw("Flags: ", line_pos_y, 2)

        for flag in self.app_data.flags:
            if line_len + len(flag + ", ") <= 37:
                colored_flag = (
                    Paper.bad_status(flag) if flag in {Flags.BAD_EXIT, Flags.MIDDLE_ONLY, Flags.NO_ED_CONSENSUS, Flags.STALE_DESC} else Paper.good_status(flag)
                )
                line += colored_flag + ", "
                line_len += len(flag + ", ")
            else:
                Pen.draw(line.rstrip(", "), line_pos_y, 9)
                line_pos_y += 1
                line = ""
                line_len = 0

        if line:
            Pen.draw(line.rstrip(", "), line_pos_y, 9)

    def draw_hints(self):
        Pen.draw(art.hints_frame, 1, 1)
        info = self.app_data.info

        hints = ""

        # Bootstrap statuses
        if info["bootstrap_percent"] < 100:
            hints += Paper.wrap_hint(
                "Bootstrap incomplete",
                "Your relay is not done bootstrapping. Wait a few minutes, and if it is still incomplete, check your logs for any warnings or errors.",
            )

        # Network statuses
        if not info["network_liveness"]:
            hints += Paper.wrap_hint(
                "Network down",
                "Tor has not observed any network activity for the past few seconds. Is your network down? If not, check your logs for any warnings or errors.",
            )
        if not info["has_enough_dir_info"]:
            hints += Paper.wrap_hint(
                "Not enough directory information",
                "Our directory information is no longer up-to-date enough to build circuits. Is your network down? If not, check your logs for any warnings or errors.",
            )

        # Relay network statuses
        if not info["reachability"]:
            hints += Paper.wrap_hint(
                "ORPort or DirPort unreachable",
                "The Tor network is not able to reach your configured ORPort or DirPort. Have you open the correct ports to the internet? Is your network down?",
            )
        if not info["good_server_descriptor"]:
            hints += Paper.wrap_hint(
                "Server descriptor denied",
                "The directories have not accepted our server descriptors. Have you tampered with descriptor information? If not, check your logs for any warnings or errors.",
            )

        # Relay statuses
        if Flags.NO_ED_CONSENSUS in self.app_data.flags:
            hints += Paper.wrap_hint(
                "NoEdConsensus flag",
                "Any Ed25519 key in the router’s descriptor or microdescriptor does not reflect authority consensus. Have you tampered with descriptor information? If not, check your logs for any warnings or errors.",
            )
        if Flags.VALID not in self.app_data.flags:
            hints += Paper.wrap_hint("Missing Valid flag", "Authorities have decided that your relay is not valid. Check your logs for any warnings or errors.")
        if Flags.RUNNING not in self.app_data.flags:
            hints += Paper.wrap_hint(
                "Missing Running flag",
                "Your relay is not currently usable over all its published ORPorts. Have you open the correct ports to the internet? Is your network down?",
            )
        if self.app_data.version_status == VersionStatus.OBSOLETE:
            hints += Paper.wrap_hint("Tor binary version is obsolete", "Upgrade ASAP.")
        if self.app_data.version_status == VersionStatus.UNRECOMMENDED:
            hints += Paper.wrap_hint("Tor binary version is not recommended", "Upgrade NOW.")
        if self.app_data.version_status == VersionStatus.UNKNOWN:
            hints += Paper.wrap_hint("Tor binary version is unknown", "Download the official Tor binary NOW.")
        if Flags.STABLE not in self.app_data.flags:
            hints += Paper.wrap_hint(
                "Missing Stable flag",
                "Your relay has not been up for long enough or its mean time between failure is too low. Is the Tor process occasionally crashing? Is your server rebooting? Is your network stable?",
            )
        if Flags.MIDDLE_ONLY in self.app_data.flags:
            hints += Paper.wrap_hint(
                "MiddleOnly flag", "Your relay is considered unsuitable for usage other than as a middle relay. Check your logs for any warnings or errors."
            )

        if Flags.BAD_EXIT in self.app_data.flags:
            hints += Paper.wrap_hint(
                "BadExit flag",
                "Your relay is believed to be useless as an exit node because its ISP censors it, because it is behind a restrictive proxy, or for some similar reason. Take appropriate action.",
            )

        if Flags.FAST not in self.app_data.flags:
            hints += Paper.wrap_hint(
                "Missing Fast flag",
                "Your relay doesn't have enough bandwidth to build high-bandwidth circuits. Fit a bigger pipe, or accept that your relay will be underused.",
            )

        if not hints:
            hints = "Your Tamagonion has a clean bill of health!"

        Pen.draw(hints, 2, 2)

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
        return textwrap.fill(f"{art.BOLD}{title}:{art.RESET}: {text}", 44) + "\n\n"
