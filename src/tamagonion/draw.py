from typing import Self

from tamagonion import art
from tamagonion.app_data import AppData, Flags


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
    instance: Self | None = None

    def __init(self, app_data: AppData) -> None:
        self.app_data = app_data

    def __new__(cls, *args, **kwargs) -> Self:
        if cls.instance is None:
            cls.instance = super().__new__(cls)
            cls.instance.__init(*args, **kwargs)
        return cls.instance

    def draw(self) -> None:
        Pen.erase()

        ## Draw Stinky

        # Bootstrap statuses
        if self.app_data.info["bootstrap_percent"] < 100:
            Pen.draw(art.stinky_egg[self.app_data.frame], 10, 0)

        # Network statuses
        elif not self.app_data.info["network_liveness"]:
            Pen.draw(art.stinky_blackout[self.app_data.frame], 9, 0)
        elif not self.app_data.info["has_enough_dir_info"]:
            Pen.draw(art.stinky_confused[self.app_data.frame], 10, 0)

        # Relay network statuses
        elif not self.app_data.info["reachability"]:
            Pen.draw(art.stinky_turned_around[self.app_data.frame], 10, 0)
        elif not self.app_data.info["good_server_descriptor"]:
            Pen.draw(art.stinky_embarrassed[self.app_data.frame], 10, 0)

        # Relay statuses
        elif Flags.NO_ED_CONSENSUS in self.app_data.flags or {Flags.VALID, Flags.RUNNING} - set(self.app_data.flags):
            Pen.draw(art.stinky_sad[self.app_data.frame], 10, 0)
        elif Flags.STALE_DESC in self.app_data.flags:
            Pen.draw(art.stinky_old[self.app_data.frame], 10, 0)
        elif Flags.STABLE not in self.app_data.flags:
            Pen.draw(art.stinky_unstable[self.app_data.frame], 10, 0)
        elif Flags.MIDDLE_ONLY in self.app_data.flags:
            Pen.draw(art.stinky_bored[self.app_data.frame], 10, 0)
        elif self.app_data.info["dormant"]:
            Pen.draw(art.stinky_asleep[self.app_data.frame], 10, 0)
        else:
            Pen.draw(art.stinky_base[self.app_data.frame], 10, 0)

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

        if Flags.GUARD in self.app_data.flags and self.app_data.info["reachability"]:
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
            f"Download (Cur/Avg/Tot): {AppData.format_bytes(self.app_data.info['bw_event_cache_down'])} / {AppData.format_bytes(self.app_data.info['bw_avg_down'])} / {AppData.format_bytes(self.app_data.info['traffic_read'])}",
            4,
            1,
        )
        Pen.draw(
            f"Upload (Cur/Avg/Tot): {AppData.format_bytes(self.app_data.info['bw_event_cache_up'])} / {AppData.format_bytes(self.app_data.info['bw_avg_up'])} / {AppData.format_bytes(self.app_data.info['traffic_written'])}",
            5,
            1,
        )
        Pen.draw(f"Version: {self.app_data.version} ({self.app_data.version_status})", 6, 1)
