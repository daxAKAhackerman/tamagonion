from collections import defaultdict
from enum import StrEnum
from typing import Any, Self

import psutil
from stem import DescriptorUnavailable
from stem.version import Version

from tamagonion.relay_manager import RelayManager

SECONDS_IN_MINUTE = 60
SECONDS_IN_HOUR = SECONDS_IN_MINUTE * 60
SECONDS_IN_DAY = SECONDS_IN_HOUR * 24


class Flags(StrEnum):
    BAD_EXIT = "BadExit"
    EXIT = "Exit"
    FAST = "Fast"
    GUARD = "Guard"
    HS_DIR = "HSDir"
    MIDDLE_ONLY = "MiddleOnly"
    STABLE = "Stable"
    STALE_DESC = "StaleDesc"
    V2_DIR = "V2Dir"
    NO_ED_CONSENSUS = "NoEdConsensus"
    RUNNING = "Running"
    VALID = "Valid"


class AppData:
    relay_manager: RelayManager
    flags: list[str]
    version: Version
    info: dict[str, Any]
    process_info: dict[str, Any]
    uptime: float = 0.0
    connection_status_map: defaultdict[str, int]
    pid: int = 0
    version_status: str = ""
    relay_name: str = ""
    frame: int = 0
    frame_skip: bool = False
    instance: Self | None = None

    def __init(self, relay_manager: RelayManager) -> None:
        self.process_info = {}
        self.info = {}
        self.version = Version("0.0.0.0")
        self.flags = []
        self.connection_status_map = defaultdict(lambda: 0)

        self.relay_manager = relay_manager
        self._get_version()
        self._get_version_status()
        self._get_pid()
        self._get_relay_name()

    def __new__(cls, *args, **kwargs) -> Self:
        if cls.instance is None:
            cls.instance = super().__new__(cls)
            cls.instance.__init(*args, **kwargs)
        return cls.instance

    def update(self) -> None:
        self._get_flags()
        self._get_uptime()
        self._get_info()
        self._get_orconn_status()

        if self.relay_manager.is_local:
            self._get_process_info()

    def _get_flags(self) -> None:
        try:
            self.flags = self.relay_manager.controller.get_network_status().flags
        except DescriptorUnavailable:
            self.flags = []

    def _get_uptime(self) -> None:
        self.uptime = self.relay_manager.controller.get_uptime()

    @property
    def formated_uptime(self) -> str:
        uptime_as_int = int(self.uptime)
        days = uptime_as_int // SECONDS_IN_DAY
        hours = (uptime_as_int % SECONDS_IN_DAY) // SECONDS_IN_HOUR
        minutes = (uptime_as_int % SECONDS_IN_HOUR) // SECONDS_IN_MINUTE
        seconds = uptime_as_int % SECONDS_IN_MINUTE

        return f"{days}d {hours:02}h {minutes:02}m {seconds:02}s"

    def _get_pid(self) -> None:
        self.pid = self.relay_manager.controller.get_pid()

    def _get_version(self) -> None:
        self.version = self.relay_manager.controller.get_version()

    def _get_version_status(self) -> None:
        self.version_status = self.relay_manager.controller.get_info("status/version/current")

    def _get_relay_name(self) -> None:
        nickname = self.relay_manager.controller.get_conf("Nickname")
        self.relay_name = nickname or "Unknown"

    def _get_info(self) -> None:
        bw_event_cache = self.relay_manager.controller.get_info("bw-event-cache")
        bw_event_latest = bw_event_cache.split(" ")[-1].split(",")
        traffic_read = self.relay_manager.controller.get_info("traffic/read")
        traffic_written = self.relay_manager.controller.get_info("traffic/written")

        self.info = {
            "dormant": self.relay_manager.controller.get_info("dormant") != "0",
            "traffic_read": int(traffic_read),
            "traffic_written": int(traffic_written),
            "bw_event_cache_down": int(bw_event_latest[0]),
            "bw_event_cache_up": int(bw_event_latest[1]),
            "bw_avg_down": int(traffic_read) / self.uptime,
            "bw_avg_up": int(traffic_written) / self.uptime,
            "network_liveness": self.relay_manager.controller.get_info("network-liveness") == "up",
            "bootstrap_percent": int(self.relay_manager.controller.get_info("status/bootstrap-phase").split(" ")[2].split("=")[-1]),
            "has_enough_dir_info": self.relay_manager.controller.get_info("status/enough-dir-info") == "1",
            "good_server_descriptor": self.relay_manager.controller.get_info("status/good-server-descriptor") == "1",
            "reachability": self.relay_manager.controller.get_info("status/reachability-succeeded/or") == "1",
        }

    def _get_orconn_status(self) -> None:
        self.connection_status_map = defaultdict(lambda: 0)
        orconn_status = self.relay_manager.controller.get_info("orconn-status")

        for status in orconn_status.split("\n"):
            _node, state = status.split(" ")
            self.connection_status_map[state] += 1

    def _get_process_info(self) -> None:
        process = psutil.Process(self.pid)

        self.process_info = {
            "cpu": process.cpu_percent(),
            "memory": process.memory_info().rss,
        }

    @staticmethod
    def format_bytes(b: int) -> str:
        if b < 10**3:
            return f"{int(b)}B"
        elif b < 10**6:
            return f"{int(b / (10**3))}KB"
        elif b < 10**9:
            return f"{int(b / (10**6))}MB"
        else:
            return f"{int(b / (10**9))}GB"
