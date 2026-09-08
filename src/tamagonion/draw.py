from typing import Self

from tamagonion import art
from tamagonion.app_data import AppData, Flags

frame_skip = False


class Pen:
    def draw(self, image: str, pos_y: int, pos_x: int) -> None:
        move_x = f"\033[{pos_x}C" if pos_x > 0 else ""
        move_y = f"\033[{pos_y}B" if pos_y > 0 else ""

        print("\033[s", end="")
        print(f"{move_x}{move_y}", end="")
        for line in image.split("\n"):
            print(line, end="")
            print(f"\r{move_x}\033[B", end="")
        print("\033[u", end="")


class Paper:
    pen: Pen
    app_data: AppData
    instance: Self | None = None

    def __init(self, app_data: AppData) -> None:
        self.app_data = app_data
        self.pen = Pen()

    def __new__(cls, *args, **kwargs) -> Self:
        if cls.instance is None:
            cls.instance = super().__new__(cls)
            cls.instance.__init(*args, **kwargs)
        return cls.instance

    def draw(self):
        global frame_skip

        self.erase()
        self.pen.draw(art.frame, 0, 0)

        # Bootstrap statuses
        if self.app_data.info["bootstrap_percent"] < 100:
            self.pen.draw(art.egg, 10, 0)

        # Network statuses
        elif not self.app_data.info["network_liveness"]:
            self.pen.draw(art.blackout[self.app_data.frame], 9, 0)
        elif not self.app_data.info["has_enough_dir_info"]:
            self.pen.draw(art.confused[self.app_data.frame], 10 + self.app_data.frame, 0)

        # Relay network statuses
        elif not self.app_data.info["reachability"]:
            self.pen.draw(art.turned_around[self.app_data.frame], 10 + self.app_data.frame, 0)
        elif not self.app_data.info["good_server_descriptor"]:
            self.pen.draw(art.embarassed[self.app_data.frame], 10 + self.app_data.frame, 0)

        # Relay statuses
        elif Flags.NO_ED_CONSENSUS in self.app_data.flags or {Flags.VALID, Flags.RUNNING} - set(self.app_data.flags):
            self.pen.draw(art.sad[self.app_data.frame], 10 + self.app_data.frame, 0)
        elif Flags.STALE_DESC in self.app_data.flags:
            self.pen.draw(art.old[self.app_data.frame], 10 + self.app_data.frame, 0)
        elif Flags.STABLE not in self.app_data.flags:
            self.pen.draw(art.unstable[self.app_data.frame], 10 + self.app_data.frame, 0)
        elif Flags.MIDDLE_ONLY in self.app_data.flags:
            self.pen.draw(art.bored[self.app_data.frame], 10 + self.app_data.frame, 0)
        elif self.app_data.info["dormant"]:
            self.pen.draw(art.sleep[self.app_data.frame], 10 + self.app_data.frame, 0)
        else:
            self.pen.draw(art.base[self.app_data.frame], 10 + self.app_data.frame, 0)

        if Flags.BAD_EXIT in self.app_data.flags:
            self.pen.draw(art.broken_exit_sign, 9, 31)
        elif Flags.EXIT in self.app_data.flags:
            self.pen.draw(art.exit_sign, 8, 30)

        if Flags.HS_DIR in self.app_data.flags:
            self.pen.draw(art.book, 15, 30)

        if Flags.V2_DIR in self.app_data.flags:
            self.pen.draw(art.cassette, 16, 1)

        if Flags.GUARD in self.app_data.flags:
            self.pen.draw(art.shield, 13 + self.app_data.frame, 19)

        if Flags.FAST not in self.app_data.flags and frame_skip:
            frame_skip = False
        else:
            self.app_data.frame ^= 1
            frame_skip = True

        self.pen.draw(f"Uptime: {self.app_data.formated_uptime}", 1, 1)
        self.pen.draw(
            f"Connections (N/L/Co/F/Cl): {self.app_data.connection_status_map['NEW']},{self.app_data.connection_status_map['LAUNCHED']},{self.app_data.connection_status_map['CONNECTED']},{self.app_data.connection_status_map['FAILED']},{self.app_data.connection_status_map['CLOSED']}",
            2,
            1,
        )
        self.pen.draw(
            f"Download (CUR/AVG/TOT): {AppData.format_bytes(self.app_data.info['bw_event_cache_down'])} / {AppData.format_bytes(self.app_data.info['bw_avg_down'])} / {AppData.format_bytes(self.app_data.info['traffic_read'])}",
            3,
            1,
        )
        self.pen.draw(
            f"Upload (CUR/AVG/TOT): {AppData.format_bytes(self.app_data.info['bw_event_cache_up'])} / {AppData.format_bytes(self.app_data.info['bw_avg_up'])} / {AppData.format_bytes(self.app_data.info['traffic_written'])}",
            4,
            1,
        )
        self.pen.draw(f"Version: {self.app_data.version} ({self.app_data.version_status})", 5, 1)

        if self.app_data.relay_manager.is_local:
            self.pen.draw(
                f"Process info (CPU/Mem/IO_R/IO_W): {self.app_data.process_info['cpu']}/{self.app_data.process_info['memory']}/{self.app_data.process_info['io_read']}/{self.app_data.process_info['io_write']}/",
                6,
                1,
            )
        # print(f"Flags: {self.app_data.flags}")
        # print(f"Uptime: {self.app_data.uptime}")
        # print(f"PID: {self.app_data.pid}")
        # print(f"Number of streams: {self.app_data.num_streams}")
        # print(f"Number of circuits: {self.app_data.num_circuits}")
        # print(f"Info: {self.app_data.info}")

    def erase(self, include_frame: bool = False):
        if include_frame:
            print("\033[0J", end="")
        else:
            split_frame = art.frame.split("\n")
            frame_height = len(split_frame)
            frame_witdh = len(split_frame[0])
            for i in range(1, frame_height - 1):
                self.pen.draw(" " * (frame_witdh - 2), i, 1)
